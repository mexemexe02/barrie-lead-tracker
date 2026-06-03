import subprocess, json, urllib.request, sys

# Get Coolify token
result = subprocess.run(['coolify', 'context', 'list', '-s', '--format', 'json'],
                       capture_output=True, text=True)
contexts = json.loads(result.stdout)
token = ""
base_url = ""
for ctx in contexts:
    if ctx.get('default'):
        token = ctx['token']
        base_url = ctx['fqdn']
        break

if not token:
    print("ERROR: No token")
    sys.exit(1)

print(f"URL: {base_url}")

# Get existing projects to find the two we just created
req = urllib.request.Request(
    f"{base_url}/api/v1/projects",
    headers={'Authorization': f'Bearer {token}'}
)
with urllib.request.urlopen(req) as resp:
    projects = json.loads(resp.read())

pacheco = None
carmens = None
for p in projects:
    if "Pacheco" in p['name']:
        pacheco = p
    elif "Carmen" in p['name']:
        carmens = p

print(f"Pacheco: {pacheco}")
print(f"Carmens: {carmens}")

# Now create applications. For Coolify, we need to create a service/resource
# Let's try the API for creating an application
def create_application(project_uuid, name, description, github_repo):
    data = json.dumps({
        "project_uuid": project_uuid,
        "name": name,
        "description": description,
        # For static site with public git
    }).encode('utf-8')

    # Try different API paths
    paths = [
        f"/api/v1/projects/{project_uuid}/applications",
        "/api/v1/applications",
        f"/api/v1/services",
    ]

    for path in paths:
        try:
            req = urllib.request.Request(
                f"{base_url}{path}",
                data=data,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json',
                },
                method='POST'
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                print(f"SUCCESS {path}: {json.dumps(result, indent=2)[:500]}")
                return result
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  {path} -> {e.code}: {body[:200]}")
        except Exception as e:
            print(f"  {path} -> Error: {e}")
    return None

# Let's first explore what's available
print("\n=== Exploring API ===")
for endpoint in ['/api/v1/applications', '/api/v1/services', '/api/v1/resources']:
    try:
        req = urllib.request.Request(
            f"{base_url}{endpoint}",
            headers={'Authorization': f'Bearer {token}'}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"GET {endpoint}: {type(data).__name__} with {len(data) if isinstance(data, list) else 'N/A'} items")
            if isinstance(data, list) and len(data) > 0:
                print(f"  First item keys: {list(data[0].keys())[:10]}")
    except Exception as e:
        print(f"GET {endpoint}: {e}")
