import subprocess
import json
import urllib.request
import sys

# Get Coolify token from CLI
result = subprocess.run(
    ['coolify', 'context', 'list', '-s', '--format', 'json'],
    capture_output=True, text=True
)
contexts = json.loads(result.stdout)
token = None
base_url = None
for ctx in contexts:
    if ctx.get('default'):
        token = ctx['token']
        base_url = ctx['fqdn']
        break

if not token:
    print("ERROR: No default context")
    sys.exit(1)

print(f"URL: {base_url}")
print(f"Token: {token[:20]}...")
print()

# Projects to create
projects = [
    {"name": "Pacheco Mobile Mechanic", "description": "Mobile auto repair website - Barrie, ON"},
    {"name": "Carmens Maid Service", "description": "Family-owned residential cleaning since 1987 - Barrie, ON"},
]

for proj in projects:
    data = json.dumps(proj).encode('utf-8')
    req = urllib.request.Request(
        f"{base_url}/api/v1/projects",
        data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"OK Created: {proj['name']}")
            print(f"  UUID: {result.get('uuid', 'N/A')}")
            print(f"  ID: {result.get('id', 'N/A')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"FAIL: {proj['name']}")
        print(f"  Status: {e.code}")
        print(f"  Body: {body[:300]}")
    print()
