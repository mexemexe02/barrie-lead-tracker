"""
Deep research: Verify businesses via Edge CDP WebSocket.
Google search → extract results → phone audit → FB/IG presence.
"""
import asyncio
import json
import urllib.request
import re
import sys

LEADS = [
    ("Thibeau Snow Plowing", "705-790-4330", "Snow Removal"),
    ("Dumex Painting", "705-309-4478", "Painting"),
    ("Pro Paint", "705-984-6097", "Painting"),
    ("Ont.paintworks", "705-623-7524", "Painting"),
    ("Shacor Painting", "705-719-0719", "Painting"),
    ("Ritekote Painting", "416-892-5015", "Painting"),
    ("Cann-Paint", "705-795-4587", "Painting"),
    ("B8's Deli and Cafe Ole", "249-252-0148", "Cafes"),
]

async def cdp_send(ws, method, params=None, session_id=None):
    msg = {"id": int(time.time()*1000) % 100000, "method": method, "params": params or {}}
    if session_id:
        msg["sessionId"] = session_id
    await ws.send(json.dumps(msg))
    resp = await ws.recv()
    return json.loads(resp)

async def cdp_eval(ws, expression, session_id=None):
    """Evaluate JS in page and return result."""
    result = await cdp_send(ws, "Runtime.evaluate", {
        "expression": expression,
        "returnByValue": True
    }, session_id)
    return result.get("result", {}).get("result", {}).get("value", None)

async def search_and_extract(ws, query, session_id=None):
    """Navigate to Google search and extract organic results."""
    import urllib.parse
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    await cdp_send(ws, "Page.navigate", {"url": url}, session_id)
    await asyncio.sleep(3.5)
    
    # Extract results
    js = """
    (() => {
        const results = [];
        // Main organic results
        document.querySelectorAll('h3').forEach(h3 => {
            const link = h3.closest('a');
            if (link) {
                results.push({
                    title: h3.innerText,
                    url: link.href,
                    snippet: ''
                });
            }
        });
        // Snippets
        document.querySelectorAll('.VwiC3b, [data-sncf]').forEach((s, i) => {
            if (i < results.length) results[i].snippet = s.innerText.substring(0, 200);
        });
        return results.slice(0, 8);
    })()
    """
    results = await cdp_eval(ws, js, session_id)
    return results or []

async def research_business(name, phone, category, ws):
    """Deep research one business."""
    out = {
        "name": name,
        "phone": phone,
        "category": category,
        "google_results": [],
        "phone_search_results": [],
        "has_website": False,
        "website_url": None,
        "fb_url": None,
        "ig_url": None,
        "phone_verified": False,
    }
    
    # 1. Search: business name + barrie
    out["google_results"] = await search_and_extract(ws, f'"{name}" barrie ontario')
    
    # Analyze for website
    exclude_domains = {"yellowpages.ca", "yelp.ca", "facebook.com", "instagram.com", 
                       "bbb.org", "canada411.ca", "411.ca", "homestars.com",
                       "linkedin.com", "nextdoor.com", "realtor.ca", "chamberofcommerce.com",
                       "pagesjaunes.ca", "infobel.com", "dnb.com", "birdeye.com",
                       "google.com", "bing.com", "youtube.com", "allpages.com",
                       "canadapages.com", "barrietoday.com"}
    
    for r in out["google_results"]:
        url = r.get("url", "")
        # Check if FB/IG
        if "facebook.com/" in url and "/profile" not in url and not out["fb_url"]:
            out["fb_url"] = url
        if "instagram.com/" in url and not out["ig_url"]:
            out["ig_url"] = url
        # Check for potential website
        domain = url.split("/")[2] if "://" in url else ""
        is_dir = any(d in domain for d in exclude_domains)
        if not is_dir and "." in domain and not out["website_url"]:
            out["website_url"] = url
            out["has_website"] = True
    
    # 2. Search: phone number
    out["phone_search_results"] = await search_and_extract(ws, f'"{phone}" barrie')
    
    # Check phone match
    for r in out["phone_search_results"]:
        snippet = r.get("snippet", "") + r.get("title", "")
        if name.lower() in snippet.lower():
            # Also verify phone in snippet
            clean_phone = phone.replace("-", "").replace(" ", "")
            snippet_clean = snippet.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if clean_phone[-7:] in snippet_clean:
                out["phone_verified"] = True
                break
    
    return out

async def main():
    # Get CDP tabs
    resp = urllib.request.urlopen("http://127.0.0.1:9224/json/list")
    tabs = json.loads(resp.read())
    
    # Find an existing page tab or create new
    target_tab = None
    for t in tabs:
        if t.get("type") == "page" and "google" not in t.get("url", ""):
            target_tab = t
            break
    if not target_tab:
        target_tab = [t for t in tabs if t.get("type") == "page"][0]
    
    ws_url = target_tab["webSocketDebuggerUrl"]
    print(f"Connected to: {target_tab.get('url','')[:80]}", file=sys.stderr)
    
    import websockets
    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        results = {}
        for name, phone, cat in LEADS:
            print(f"\n--- {name} ({phone}) ---", file=sys.stderr)
            try:
                r = await research_business(name, phone, cat, ws)
                results[name] = r
                print(f"  Web: {r['has_website']} | FB: {'✓' if r['fb_url'] else '✗'} | IG: {'✓' if r['ig_url'] else '✗'} | Phone: {'✓' if r['phone_verified'] else '✗'}", file=sys.stderr)
                if r["google_results"]:
                    for gr in r["google_results"][:3]:
                        print(f"    → {gr.get('title','?')[:80]} | {gr.get('url','?')[:80]}", file=sys.stderr)
            except Exception as e:
                results[name] = {"error": str(e)}
                print(f"  ERROR: {e}", file=sys.stderr)
    
    # Print final JSON to stdout
    print(json.dumps(results, indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    import time
    asyncio.run(main())
