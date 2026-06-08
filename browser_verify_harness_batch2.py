"""Remaining SMS audit checks — FB, Shopify, Yelp. Pipe: browser-harness < browser_verify_harness_batch2.py"""
import json

CHECKS = [
    ("fb_chadwick", "chadwick", "https://www.facebook.com/chadwickpainting/"),
    ("bruno_shopify", "bruno", "https://brunos-bakery.myshopify.com/pages/bakery-menu"),
    ("yelp_installer", "installer", "https://www.yelp.ca/biz/the-installer-barrie-2"),
]

SKIP = {
    "search", "log in", "fr", "please enter what you're searching for",
    "please enter your search location", "email or phone number", "password",
}


def page_text_snippet(max_lines=45):
    txt = js("document.body ? document.body.innerText : ''") or ""
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    return lines[:max_lines]


def headline_from_lines(lines):
    for ln in lines:
        low = ln.lower()
        if low in SKIP or "passer en" in low or "switch to french" in low:
            continue
        if len(ln) > 3:
            return ln
    return ""


results = []
for key, label, url in CHECKS:
    new_tab(url)
    wait_for_load(timeout=30)
    wait(4)
    info = page_info()
    lines = page_text_snippet(50)
    headline = headline_from_lines(lines)
    results.append({
        "key": key,
        "label": label,
        "url": info.get("url", url),
        "title": info.get("title", ""),
        "headline": headline,
        "snippet": "\n".join(lines[:35]),
    })
    print(f"OK {key}: {headline[:100]}")

out_path = r"C:\Users\Humberto\website-projects\browser-sms-verification-mcp-batch2.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("# Browser SMS Verification batch 2 (browser-harness CDP) — 2026-06-08\n\n")
    for r in results:
        f.write(f"=== {r['key']} ({r['label']}) ===\n")
        f.write(f"URL: {r['url']}\n")
        f.write(f"Title: {r['title']}\n")
        f.write(f"Headline: {r['headline']}\n\n")
        f.write(r["snippet"])
        f.write("\n\n")

print("WROTE", out_path)
print(json.dumps(results, indent=2))
