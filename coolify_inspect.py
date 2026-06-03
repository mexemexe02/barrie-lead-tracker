import subprocess, json, urllib.request

# Get token
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

# Get an existing application to see the schema
req = urllib.request.Request(
    f"{base_url}/api/v1/applications",
    headers={'Authorization': f'Bearer {token}'}
)
with urllib.request.urlopen(req) as resp:
    apps = json.loads(resp.read())

# Show first app's structure
if apps:
    app = apps[0]
    print("=== Existing App Schema ===")
    print(json.dumps(app, indent=2)[:3000])

    # Get one app's detail
    app_uuid = app['uuid']
    req2 = urllib.request.Request(
        f"{base_url}/api/v1/applications/{app_uuid}",
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(req2) as resp2:
        detail = json.loads(resp2.read())
        print("\n=== App Detail ===")
        print(json.dumps(detail, indent=2)[:3000])

# Also list resources 
print("\n=== Resources ===")
req3 = urllib.request.Request(
    f"{base_url}/api/v1/resources",
    headers={'Authorization': f'Bearer {token}'}
)
with urllib.request.urlopen(req3) as resp3:
    resources = json.loads(resp3.read())
    if resources:
        print(f"Count: {len(resources)}")
        print(json.dumps(resources[0], indent=2)[:2000])
