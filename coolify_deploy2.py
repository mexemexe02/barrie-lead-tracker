import subprocess, json, urllib.request, sys

result = subprocess.run(['coolify', 'context', 'list', '-s', '--format', 'json'],
                       capture_output=True, text=True)
contexts = json.loads(result.stdout)
token = base_url = ""
for ctx in contexts:
    if ctx.get('default'):
        token = ctx['token']
        base_url = ctx['fqdn']
        break

if not token:
    print("No token"); sys.exit(1)

SERVER_UUID = "cgcwwkccsws8s8wkkswsco8k"
DEST_UUID = "w0ws0ggggcwgookw0048cokc"

apps = [
    {
        "name": "Pawfection Grooming Boutique",
        "desc": "Dog grooming - Barrie ON since 2005",
        "repo": "https://github.com/mexemexe02/pawfection-grooming.git",
    },
    {
        "name": "Pawtricias Dog Grooming",
        "desc": "All breeds & cats grooming - Barrie ON",
        "repo": "https://github.com/mexemexe02/pawtricias-dog-grooming.git",
    },
]

for app in apps:
    # 1. Create project
    proj_data = json.dumps({"name": app["name"], "description": app["desc"]}).encode()
    try:
        req = urllib.request.Request(f"{base_url}/api/v1/projects", data=proj_data,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as r:
            proj = json.loads(r.read())
            proj_uuid = proj['uuid']
            print(f"Project: {app['name']} -> {proj_uuid}")
    except Exception as e:
        print(f"Project ERROR {app['name']}: {e}")
        continue

    # 2. Create application
    payload = {
        "project_uuid": proj_uuid,
        "server_uuid": SERVER_UUID,
        "environment_name": "production",
        "git_repository": app["repo"],
        "git_branch": "master",
        "build_pack": "static",
        "name": app["name"].lower().replace(" ", "-").replace("'", ""),
        "description": app["desc"],
        "is_static": True,
        "static_image": "nginx:alpine",
        "publish_directory": "/",
        "ports_exposes": "80",
        "instant_deploy": True,
        "destination_uuid": DEST_UUID,
    }
    app_data = json.dumps(payload).encode()
    try:
        req2 = urllib.request.Request(f"{base_url}/api/v1/applications/public", data=app_data,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req2) as r2:
            result = json.loads(r2.read())
            print(f"  App: {result.get('uuid')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  App ERROR: {e.code} {body[:200]}")
    print()
