"""Canada411 batch — writes after each check. Pipe: browser-harness < browser_verify_harness_batch1.py"""
import json

CHECKS = [
    ("wrong_express", "7057916925", "https://www.canada411.ca/search/?stype=si&what=7057916925"),
    ("wrong_installer", "7054662244", "https://www.canada411.ca/search/?stype=si&what=7054662244"),
    ("wrong_thornton", "7057187816", "https://www.canada411.ca/search/?stype=si&what=7057187816"),
    ("correct_express", "7057300944", "https://www.canada411.ca/search/?stype=si&what=7057300944"),
    ("correct_fils", "7057267818", "https://www.canada411.ca/search/?stype=si&what=7057267818"),
    ("correct_carmens", "7057341118", "https://www.canada411.ca/search/?stype=si&what=7057341118"),
]

SKIP = {"search", "log in", "fr", "please enter what you're searching for", "please enter your search location"}
OUT = r"C:\Users\Humberto\website-projects\browser-sms-verification-mcp.txt"


def snippet(max_lines=30):
    txt = js("document.body ? document.body.innerText : ''") or ""
    return [ln.strip() for ln in txt.splitlines() if ln.strip()][:max_lines]


def headline(lines):
    for ln in lines:
        low = ln.lower()
        if low in SKIP or "passer en" in low:
            continue
        if ln.startswith("705") and "Result" in ln:
            continue
        if len(ln) > 3:
            return ln
    return ""


with open(OUT, "w", encoding="utf-8") as f:
    f.write("# Browser SMS Verification (browser-harness CDP) — 2026-06-08\n\n")

for key, label, url in CHECKS:
    new_tab(url)
    wait_for_load(timeout=25)
    wait(2)
    info = page_info()
    lines = snippet(35)
    h = headline(lines)
    block = (
        f"=== {key} ({label}) ===\n"
        f"URL: {info.get('url', url)}\n"
        f"Title: {info.get('title', '')}\n"
        f"Headline: {h}\n\n"
        + "\n".join(lines[:28])
        + "\n\n"
    )
    with open(OUT, "a", encoding="utf-8") as f:
        f.write(block)
    print(f"OK {key}: {h}")

print("WROTE", OUT)
