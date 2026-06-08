"""Check Ready-lead Facebook pages for website links via browser-harness CDP.
Pipe: Get-Content browser_verify_ready_fb.py | browser-harness

Requires Edge CDP:
  msedge --remote-debugging-port=9224 --user-data-dir=C:\temp\edge-cdp
"""
import json
import re

# Remaining ready leads with Facebook URLs (exclude Island Mainland — dead)
CHECKS = [
    ("prestige_classic", "Prestige Classic Painting", "https://www.facebook.com/prestigeclassicpainting/"),
    ("shacor", "Shacor Painting", "https://www.facebook.com/1188849051139274/"),
    ("vellinga", "Vellinga Painting", "https://www.facebook.com/728512927322010/"),
    ("clearview_hvac", "Clearview Heating", "https://www.facebook.com/pages/Clearview-Heating-Air-Condition-Supply/1602017150120748"),
    ("ns_flooring", "NS Flooring", "https://www.facebook.com/p/NS-Flooring-Contracting-100064703930831/"),
    ("barrie_sandblasting", "Barrie Sandblasting", "https://www.facebook.com/1101473186563013/"),
    ("actright_roofing", "ActRight Roofing", "https://www.facebook.com/61576707270558/"),
    ("pattimore", "Pattimore Painting", "https://www.facebook.com/pattimorepainting/"),
]

WEBSITE_RE = re.compile(
    r"https?://(?:www\.)?[a-z0-9][a-z0-9.-]+\.[a-z]{2,}(?:/[^\s\"'<>]*)?",
    re.I,
)

SKIP_DOMAINS = {
    "facebook.com", "fb.com", "instagram.com", "linkedin.com", "youtube.com",
    "google.com", "goo.gl", "bit.ly", "whatsapp.com", "messenger.com",
}


def extract_urls(text):
    found = []
    for m in WEBSITE_RE.finditer(text or ""):
        url = m.group(0).rstrip(".,)")
        host = url.split("/")[2].lower().removeprefix("www.")
        if any(host == d or host.endswith("." + d) for d in SKIP_DOMAINS):
            continue
        if url not in found:
            found.append(url)
    return found


results = []
for key, name, url in CHECKS:
    new_tab(url)
    wait_for_load(timeout=30)
    wait(3)
    info = page_info()
    body = js("document.body ? document.body.innerText : ''") or ""
    html = js("document.documentElement ? document.documentElement.innerHTML : ''") or ""
    urls = extract_urls(body + "\n" + html)
    results.append({
        "key": key,
        "name": name,
        "fb_url": info.get("url", url),
        "title": info.get("title", ""),
        "website_links": urls[:8],
        "snippet": "\n".join([ln.strip() for ln in body.splitlines() if ln.strip()][:25]),
    })
    print(f"OK {key}: {len(urls)} external links")

out = r"C:\Users\Humberto\website-projects\browser-ready-fb-website-check.txt"
with open(out, "w", encoding="utf-8") as f:
    f.write("# Ready leads — FB website link check (browser-harness)\n\n")
    for r in results:
        f.write(f"=== {r['name']} ({r['key']}) ===\n")
        f.write(f"FB: {r['fb_url']}\n")
        f.write(f"Title: {r['title']}\n")
        f.write(f"Website links found: {r['website_links'] or 'NONE'}\n\n")
        f.write(r["snippet"])
        f.write("\n\n")

print("WROTE", out)
print(json.dumps([{"k": r["key"], "sites": r["website_links"]} for r in results], indent=2))
