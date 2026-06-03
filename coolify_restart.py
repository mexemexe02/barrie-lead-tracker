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

app_uuids = {
    "Pacheco": "b12f6ruz0z3vlidk4pj1c344",
    "Carmens": "vbc05q9ireu4i6re7hogzsfh",
}

# For each app, update config and restart
for name, uuid in app_uuids.items():
    print(f"\n=== {name} ===")
    
    # Try restarting first
    req = urllib.request.Request(
        f"{base_url}/api/v1/applications/{uuid}/restart",
        headers={'Authorization': f'Bearer {token}'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  Restart triggered: {resp.read().decode()[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Restart: {e.code} - {body[:300]}")
    
    # Also try start
    req2 = urllib.request.Request(
        f"{base_url}/api/v1/applications/{uuid}/start",
        headers={'Authorization': f'Bearer {token}'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req2) as resp:
            data = json.loads(resp.read())
            print(f"  Start: {json.dumps(data)[:300]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Start: {e.code} - {body[:300]}")
