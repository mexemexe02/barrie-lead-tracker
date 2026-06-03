import subprocess, json, urllib.request, sys

# Get Coolify token and URL
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

# Project UUIDs from previous run
PACHECO_UUID = "fkso1ycqojvt3vjquo2ebs1c"
CARMENS_UUID = "z2sp5a46pnk0t0z8yiq2d110"

# GitHub repo URLs
PACHECO_REPO = "https://github.com/mexemexe02/pacheco-mobile-mechanic.git"
CARMENS_REPO = "https://github.com/mexemexe02/carmens-maid-service.git"

def create_app(project_uuid, name, repo_url, branch="master"):
    """Try to create a Coolify application via API"""
    
    # Based on Coolify's API, applications might be created via different endpoints
    payload = {
        "project_uuid": project_uuid,
        "name": name,
        "git_repository": "public",
        "git_branch": branch,
        "git_full_url": repo_url,
        "build_pack": "static",
        "publish_directory": "/",
        "ports_exposes": "80",
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    # Try different endpoints
    endpoints = [
        f"/api/v1/applications",
        f"/api/v1/projects/{project_uuid}/applications",
        f"/api/v1/services",
    ]
    
    for endpoint in endpoints:
        try:
            req = urllib.request.Request(
                f"{base_url}{endpoint}",
                data=data,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json',
                },
                method='POST'
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                print(f"  ✓ {endpoint} -> {result.get('uuid', result)[:100]}")
                return result
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            try:
                err = json.loads(body)
                msg = err.get('message', body[:100])
            except:
                msg = body[:100]
            print(f"  ✗ {endpoint} ({e.code}): {msg}")
        except Exception as e:
            print(f"  ✗ {endpoint}: {e}")
    
    return None

print("=== Creating Pacheco Mobile Mechanic App ===")
pacheco_app = create_app(PACHECO_UUID, "pacheco-mobile-mechanic", PACHECO_REPO)

print("\n=== Creating Carmens Maid Service App ===")
carmens_app = create_app(CARMENS_UUID, "carmens-maid-service", CARMENS_REPO)

# If creation fails, print guidance
if not pacheco_app or not carmens_app:
    print("\n" + "="*60)
    print("MANUAL SETUP NEEDED: Use the Coolify Web Dashboard")
    print("="*60)
    print(f"URL: {base_url}")
    print("\nSteps:")
    print("1. Log in to Coolify")
    print("2. For each project, create a new Application:")
    print(f"   - Pacheco Mobile Mechanic -> Add Resource -> Application")
    print(f"     GitHub repo: {PACHECO_REPO}")
    print(f"   - Carmens Maid Service -> Add Resource -> Application")
    print(f"     GitHub repo: {CARMENS_REPO}")
    print("3. Configure as Static Site (build pack: static)")
    print("4. Deploy!")
