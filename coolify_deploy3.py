import subprocess, json, urllib.request

result = subprocess.run(['coolify', 'context', 'list', '-s', '--format', 'json'],
                       capture_output=True, text=True)
contexts = json.loads(result.stdout)
token = base_url = ""
for ctx in contexts:
    if ctx.get('default'):
        token = ctx['token']
        base_url = ctx['fqdn']
        break

SERVER_UUID = "cgcwwkccsws8s8wkkswsco8k"
DEST_UUID = "w0ws0ggggcwgookw0048cokc"

apps = [
    ("Fitness Training with Olga", "Womens personal training - Barrie ON",
     "https://github.com/mexemexe02/fitness-training-olga.git"),
    ("Blanchettes Services", "Handyman & contracting - Barrie ON",
     "https://github.com/mexemexe02/blanchettes-services.git"),
]

for name, desc, repo in apps:
    proj_data = json.dumps({"name": name, "description": desc}).encode()
    req = urllib.request.Request(f"{base_url}/api/v1/projects", data=proj_data,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as r:
        proj_uuid = json.loads(r.read())['uuid']
        print(f"Project: {name} -> {proj_uuid}")

    payload = {
        "project_uuid": proj_uuid, "server_uuid": SERVER_UUID,
        "environment_name": "production", "git_repository": repo,
        "git_branch": "master", "build_pack": "static",
        "name": name.lower().replace(" ", "-"),
        "description": desc, "is_static": True,
        "static_image": "nginx:alpine", "publish_directory": "/",
        "ports_exposes": "80", "instant_deploy": True,
        "destination_uuid": DEST_UUID,
    }
    app_data = json.dumps(payload).encode()
    req2 = urllib.request.Request(f"{base_url}/api/v1/applications/public", data=app_data,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req2) as r2:
        app_uuid = json.loads(r2.read()).get('uuid')
        print(f"  App: {app_uuid}")
        print(f"  URL: http://{app_uuid}.178.156.135.237.sslip.io")
    print()
