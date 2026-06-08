"""Verify website domains found on FB About pages."""
import json

CHECKS = [
    ("prestige", "https://prestigeclassicpainting.com/"),
    ("prestige_www", "https://www.prestigeclassicpainting.com/"),
    ("barrie_sand", "http://www.barriesandblastingon.ca/"),
    ("barrie_sand_https", "https://www.barriesandblastingon.ca/"),
    ("pattimore", "https://pattimorepainting.com/"),
    ("pattimore_www", "https://www.pattimorepainting.com/"),
]

results = []
for key, url in CHECKS:
    new_tab(url)
    wait_for_load(timeout=20)
    wait(2)
    info = page_info()
    body = js("document.body ? document.body.innerText.slice(0,500) : ''") or ""
    results.append({
        "key": key,
        "url": info.get("url", url),
        "title": info.get("title", ""),
        "snippet": body.replace("\n", " ")[:200],
    })
    print(f"OK {key}: {info.get('title','')[:60]}")

out = r"C:\Users\Humberto\website-projects\browser-ready-domain-verify.txt"
with open(out, "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"=== {r['key']} ===\nURL: {r['url']}\nTitle: {r['title']}\n{r['snippet']}\n\n")
print("WROTE", out)
print(json.dumps(results, indent=2))
