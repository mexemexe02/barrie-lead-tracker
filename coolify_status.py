import subprocess, json, urllib.request

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

# Check both apps
app_uuids = {
    "Pacheco Mobile Mechanic": "b12f6ruz0z3vlidk4pj1c344",
    "Carmens Maid Service": "vbc05q9ireu4i6re7hogzsfh",
}

for name, uuid in app_uuids.items():
    req = urllib.request.Request(
        f"{base_url}/api/v1/applications/{uuid}",
        headers={'Authorization': f'Bearer {token}'}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            app = json.loads(resp.read())
            status = app.get('status', 'unknown')
            fqdn = app.get('fqdn', 'none')
            print(f"\n=== {name} ===")
            print(f"  Status: {status}")
            print(f"  FQDN: {fqdn}")
            print(f"  Git branch: {app.get('git_branch', '?')}")
            print(f"  Build pack: {app.get('build_pack', '?')}")
    except Exception as e:
        print(f"\n{name}: ERROR - {e}")
