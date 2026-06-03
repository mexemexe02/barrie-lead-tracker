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

# UUIDs
PACHECO_PROJECT = "fkso1ycqojvt3vjquo2ebs1c"
CARMENS_PROJECT = "z2sp5a46pnk0t0z8yiq2d110"
SERVER_UUID = "cgcwwkccsws8s8wkkswsco8k"
DESTINATION_UUID = "w0ws0ggggcwgookw0048cokc"

apps = [
    {
        "project_uuid": PACHECO_PROJECT,
        "server_uuid": SERVER_UUID,
        "environment_name": "production",
        "git_repository": "https://github.com/mexemexe02/pacheco-mobile-mechanic.git",
        "git_branch": "master",
        "build_pack": "static",
        "name": "pacheco-mobile-mechanic",
        "description": "Mobile auto repair website - Barrie, ON",
        "is_static": True,
        "static_image": "nginx:alpine",
        "publish_directory": "/",
        "ports_exposes": "80",
        "instant_deploy": True,
        "destination_uuid": DESTINATION_UUID,
    },
    {
        "project_uuid": CARMENS_PROJECT,
        "server_uuid": SERVER_UUID,
        "environment_name": "production",
        "git_repository": "https://github.com/mexemexe02/carmens-maid-service.git",
        "git_branch": "master",
        "build_pack": "static",
        "name": "carmens-maid-service",
        "description": "Family-owned residential cleaning since 1987 - Barrie, ON",
        "is_static": True,
        "static_image": "nginx:alpine",
        "publish_directory": "/",
        "ports_exposes": "80",
        "instant_deploy": True,
        "destination_uuid": DESTINATION_UUID,
    },
]

for app in apps:
    data = json.dumps(app).encode('utf-8')
    req = urllib.request.Request(
        f"{base_url}/api/v1/applications/public",
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
            print(f"OK: {app['name']}")
            print(f"  UUID: {result.get('uuid', result)}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"FAIL ({e.code}): {app['name']}")
        try:
            err = json.loads(body)
            print(f"  {json.dumps(err, indent=2)[:500]}")
        except:
            print(f"  {body[:300]}")
    print()
