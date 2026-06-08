#!/usr/bin/env python3
"""Regenerate the Barrie Demo Drop tracker HTML from leads.csv and push to GitHub Pages.
V2: Added SMS/Email copy buttons with outreach templates."""
import csv, os, subprocess
from datetime import datetime, timezone

PROJ_DIR = os.path.expanduser("~/website-projects")
CSV_PATH = os.path.join(PROJ_DIR, "leads.csv")
TRACKER_DIR = os.path.join(PROJ_DIR, "barrie-lead-tracker")
HTML_PATH = os.path.join(TRACKER_DIR, "index.html")

STATUS_CLASS = {
    "new": "badge-new",
    "ready": "badge-ready",
    "sent": "badge-sent",
    "pending": "badge-pending",
    "replied": "badge-replied",
    "dead": "badge-dead",
    "verified": "badge-new",
}

KUMON_LINE = "I run Kumon Mapleview here in Barrie, and I also build websites for local businesses."

def clean(val):
    v = (val or "").strip()
    return "—" if v in ("", "—", "-", "@") else v

def phone_digits(phone):
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    return digits[1:] if len(digits) == 11 and digits.startswith("1") else digits

def is_textable_phone(phone):
    digits = phone_digits(phone)
    toll_free_prefixes = ("800", "833", "844", "855", "866", "877", "888")
    return bool(digits) and not digits.startswith(toll_free_prefixes)

def has_demo(lead):
    demo_url = clean(lead.get("demo_url"))
    return demo_url != "—" and "TBD" not in demo_url

def has_outreach_route(lead):
    return (
        is_textable_phone(lead.get("phone", ""))
        or clean(lead.get("email")) != "—"
        or clean(lead.get("social")) != "—"
    )

def inferred_no_website(lead):
    notes = lead.get("notes", "").lower()
    status = lead.get("status", "new")
    if status == "dead" and ("website" in notes or "domain" in notes):
        return False
    return (
        "verified no website" in notes
        or "no official website" in notes
        or status == "live"
        or (has_demo(lead) and "demo deployed" in notes)
    )

def is_ready_outreach(lead):
    status = lead.get("status", "new")
    if status == "ready":
        return True
    if status in ("dead", "sent", "replied", "in_progress"):
        return False
    return has_demo(lead) and inferred_no_website(lead) and has_outreach_route(lead)

def load_leads():
    leads = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("business", "").strip():
                leads.append(row)
    return leads

def compute_stats(leads):
    total = len(leads)
    contacted = sum(1 for l in leads if l.get("status", "new") in ("sent", "replied"))
    new_count = sum(1 for l in leads if l.get("status", "new") == "new")
    ready_count = sum(1 for l in leads if is_ready_outreach(l))
    verified = sum(1 for l in leads if "cleaned" in l.get("notes", "").lower() or "verified" in l.get("notes", "").lower())
    return total, contacted, new_count, ready_count, verified

def first_name(contact_name):
    """Return a first name only when a real contact name is known."""
    value = clean(contact_name)
    if value == "—":
        return ""
    return value.replace("&amp;", "and").split()[0]

def greeting(contact_name):
    name = first_name(contact_name)
    return f"Hi {name}," if name else "Hi,"

def sms_template(business, category, demo_url, phone, contact_name=""):
    """Short SMS pitch — Humberto's preferred soft close (2026-06-08)."""
    name = first_name(contact_name)
    greet = f"Hi {name} —" if name else "Hi —"
    url = (demo_url or "").rstrip("/")
    return (
        f"{greet} I'm Humberto, local to Barrie (Kumon Mapleview). "
        f"I noticed {business} doesn't have a website yet, and I put together a quick demo: {url}\n\n"
        f"Let me know what you think if you're interested."
    )

def email_template(business, category, demo_url, contact_name=""):
    """Longer email pitch."""
    return (
        f"Subject: Website demo for {business}\n\n"
        f"{greeting(contact_name)}\n\n"
        f"My name is Humberto Domingues. I run the Kumon Math & Reading Centre on Mapleview, "
        f"and I also build websites for local Barrie businesses.\n\n"
        f"I noticed {business} does not have a website yet, so I put together a quick professional demo "
        f"to show what an online presence could look like:\n{demo_url}\n\n"
        f"It's a single page with your services, about info, and a contact form — "
        f"mobile-friendly and built to convert visitors into customers.\n\n"
        f"If you are interested, I can build you a proper professional site. Worth a look?\n\n"
        f"Best,\n"
        f"Humberto Domingues\n"
        f"Kumon Barrie Mapleview\n"
        f"humbertobizes@gmail.com"
    )

def format_actions(lead):
    """Generate copy buttons for SMS and Email."""
    business = clean(lead.get("business", ""))
    category = clean(lead.get("category", "Business"))
    contact_name = lead.get("contact_name", "")
    raw_phone = clean(lead.get("phone", ""))
    phone = raw_phone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
    email_addr = clean(lead.get("email", ""))
    demo_url = clean(lead.get("demo_url", "")).strip()
    
    if demo_url == "—" or "TBD" in demo_url:
        return "—"
    
    if not demo_url.startswith("http"):
        demo_url = "https://" + demo_url
    
    buttons = []
    
    # SMS button (if phone exists)
    if phone not in ("—", "") and is_textable_phone(raw_phone):
        sms_msg = sms_template(business, category, demo_url, phone, contact_name).replace("\\", "\\\\").replace("'", "\\'").replace('"', '&quot;').replace("\n", "\\n").replace("\r", "")
        buttons.append(
            f'<button class="copy-btn copy-sms" onclick="copyMsg(\'{sms_msg}\',this)" '
            f'title="Copy SMS for {business}">📱 SMS</button>'
        )
    
    # Email button (if email exists)
    if email_addr not in ("—", ""):
        email_msg = email_template(business, category, demo_url, contact_name).replace("'", "\\'").replace('"', '&quot;').replace('\n', '\\n')
        buttons.append(
            f'<button class="copy-btn copy-email" onclick="copyMsg(\'{email_msg}\',this)" '
            f'title="Copy Email for {business}">✉️ Email</button>'
        )
    
    return " ".join(buttons) if buttons else "—"

def format_phone(lead):
    phone = clean(lead.get("phone", ""))
    return f'<a href="tel:{phone}" class="url">{phone}</a>' if phone != "—" else "—"

def format_email(lead):
    email = clean(lead.get("email", ""))
    return f'<a href="mailto:{email}" class="url">{email}</a>' if email != "—" else "—"

def format_social(lead):
    social = clean(lead.get("social", lead.get("contact_name", "")))
    if social == "—": return "—"
    if "facebook.com" in social or "fb.com" in social or "instagram.com" in social:
        if not social.startswith("http"):
            social = "https://www." + social if not social.startswith("www.") else "https://" + social
        return f'<a href="{social}" target="_blank" class="url" rel="noopener">FB Page ↗</a>'
    if social.startswith("http"):
        return f'<a href="{social}" target="_blank" class="url">{social.split("/")[-1] or social}</a>'
    return social

def format_demo_url(demo_url):
    if not demo_url or demo_url.strip() in ("TBD", "—", "-", ""): return "TBD"
    full_url = demo_url.strip()
    if not full_url.startswith("http"): full_url = "http://" + full_url
    short = full_url.replace("http://", "").replace("https://", "").rstrip("/")
    return f'<a href="{full_url}" target="_blank" class="url" rel="noopener">{short}</a>'

def status_key(business):
    key = "".join(ch.lower() if ch.isalnum() else "-" for ch in business)
    return "-".join(part for part in key.split("-") if part) or "unknown"

def badge(status, key):
    label = status
    extra = " ✓ cleaned" if "cleaned" in status or "verified" in status else ""
    if extra: label = "new"
    cls = STATUS_CLASS.get(label, "badge-new")
    return (
        f'<span class="badge {cls} status-toggle" data-status-key="{key}" '
        f'data-status="{label}" title="Click to cycle: new → sent → dead">{label}{extra}</span>'
    )

def generate_html(leads):
    total, contacted, new_count, ready_count, verified = compute_stats(leads)
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    rows = ""
    for i, lead in enumerate(leads, 1):
        business = lead.get("business", "Unknown")
        category = lead.get("category", "—")
        phone = format_phone(lead)
        email = format_email(lead)
        social = format_social(lead)
        demo = format_demo_url(lead.get("demo_url", "TBD"))
        status = lead.get("status", "new")
        notes = lead.get("notes", "")
        status_display = f"{status} ✓ cleaned" if "cleaned" in notes.lower() else status
        actions = format_actions(lead)
        key = status_key(business)
        ready_default = "1" if is_ready_outreach(lead) else "0"

        rows += (
            f'<tr data-ready-default="{ready_default}"><td>{i}</td><td>{business}</td><td>{category}</td>'
            f'<td>{phone}</td><td>{email}</td><td>{social}</td>'
            f'<td>{demo}</td><td>{badge(status_display, key)}</td>'
            f'<td class="actions-col">{actions}</td></tr>\n'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Barrie Demo Drop — Lead Tracker</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,sans-serif;background:#0f1117;color:#e0e0e0;padding:20px}}
h1{{color:#c9a84c;margin-bottom:8px;font-size:1.4rem}}
.subtitle{{color:#888;margin-bottom:24px;font-size:0.9rem}}
.table-wrap{{overflow-x:auto;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;font-size:0.82rem;min-width:1100px}}
th{{background:#1a1d2a;color:#c9a84c;padding:10px 6px;text-align:left;font-weight:600;border-bottom:2px solid #2a2d3a;white-space:nowrap}}
td{{padding:8px 6px;border-bottom:1px solid #1a1d2a;vertical-align:top}}
tr:hover{{background:#1a1d2a}}
.actions-col{{white-space:nowrap;min-width:120px}}
.copy-btn{{display:inline-block;padding:3px 10px;margin:1px 2px;border-radius:4px;border:none;font-size:0.72rem;font-weight:600;cursor:pointer;transition:all 0.15s;white-space:nowrap}}
.copy-sms{{background:#1e3a5f;color:#60a5fa}}
.copy-sms:hover{{background:#2a4a7f;color:#93c5fd}}
.copy-email{{background:#3b1f5e;color:#c084fc}}
.copy-email:hover{{background:#4a2a7e;color:#d8b4fe}}
.copy-btn:active{{transform:scale(0.96)}}
.copied{{background:#166534!important;color:#4ade80!important}}
.status-new{{color:#4ade80}}
.status-sent{{color:#60a5fa}}
.status-pending{{color:#fbbf24}}
.status-replied{{color:#c084fc}}
.url{{color:#60a5fa;font-size:0.78rem;word-break:break-all;text-decoration:none}}
.url:hover{{text-decoration:underline}}
.badge{{display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.72rem;font-weight:600;white-space:nowrap}}
.badge-new{{background:#166534;color:#4ade80}}
.badge-ready{{background:#5c4a1f;color:#facc15}}
.badge-sent{{background:#1e3a5f;color:#60a5fa}}
.badge-pending{{background:#5c4a1f;color:#fbbf24}}
.badge-replied{{background:#3b1f5e;color:#c084fc}}
.badge-dead{{background:#2a1a1a;color:#aa5555}}
.status-toggle{{cursor:pointer;transition:transform 0.15s,filter 0.15s}}
.status-toggle:hover{{filter:brightness(1.2);transform:translateY(-1px)}}
.summary{{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap}}
.stat{{background:#1a1d2a;padding:12px 18px;border-radius:8px;text-align:center}}
.stat-num{{font-size:1.6rem;font-weight:700;color:#c9a84c}}
.stat-label{{font-size:0.75rem;color:#888}}
.last-updated{{color:#666;font-size:0.75rem;margin-top:24px;text-align:center}}
.last-updated a{{color:#c9a84c;text-decoration:none}}
.last-updated a:hover{{text-decoration:underline}}
.tracker-controls{{display:flex;align-items:center;gap:10px;margin-bottom:16px}}
.tracker-controls label{{display:flex;align-items:center;gap:8px;cursor:pointer;color:#888;font-size:0.85rem;-webkit-user-select:none;user-select:none}}
.tracker-controls input{{accent-color:#c9a84c;width:16px;height:16px}}
.tracker-controls select{{background:#1a1d2a;color:#e0e0e0;border:1px solid #2a2d3a;border-radius:6px;padding:6px 10px;font-size:0.85rem}}
.filter-count{{color:#888;font-size:0.8rem}}
.dead-count{{color:#666;font-size:0.8rem}}
.toast{{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#166534;color:#4ade80;padding:10px 24px;border-radius:8px;font-size:0.85rem;z-index:999;opacity:0;transition:opacity 0.3s;pointer-events:none}}
.toast.show{{opacity:1}}
</style>
<script>
const STATUS_CYCLE = ['new', 'ready', 'sent', 'dead'];
const STATUS_STORAGE_KEY = 'barrie_status_overrides_v3';
const LEGACY_STATUS_STORAGE_KEY = 'barrie_status_overrides_v2';
const VIEW_FILTER_KEY = 'barrie_view_filter_v2';
const DEFAULT_VIEW_FILTER = 'ready';

function readCookie(name) {{
    const prefix = name + '=';
    return document.cookie
        .split(';')
        .map((part) => part.trim())
        .find((part) => part.startsWith(prefix))
        ?.slice(prefix.length) || '';
}}

function parseStoredStatuses(raw) {{
    if (!raw) return {{}};
    try {{
        return JSON.parse(decodeURIComponent(raw));
    }} catch (error) {{
        return {{}};
    }}
}}

function loadStatusOverrides() {{
    try {{
        const saved = localStorage.getItem(STATUS_STORAGE_KEY) || localStorage.getItem(LEGACY_STATUS_STORAGE_KEY);
        if (saved) return parseStoredStatuses(saved);
    }} catch (error) {{
        // Some browsers block localStorage in private or restricted modes.
    }}

    return parseStoredStatuses(readCookie(STATUS_STORAGE_KEY));
}}

let statusOverrides = loadStatusOverrides();

function saveStatusOverrides() {{
    const serialized = JSON.stringify(statusOverrides);

    try {{
        localStorage.setItem(STATUS_STORAGE_KEY, serialized);
        if (localStorage.getItem(STATUS_STORAGE_KEY) === serialized) return true;
    }} catch (error) {{
        // Fall through to cookie persistence below.
    }}

    document.cookie = STATUS_STORAGE_KEY + '=' + encodeURIComponent(serialized) + '; max-age=31536000; path=/; SameSite=Lax';
    return readCookie(STATUS_STORAGE_KEY) === encodeURIComponent(serialized);
}}

function showToast(message) {{
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 1500);
}}

function setBadgeStatus(badge, status) {{
    badge.dataset.status = status;
    badge.className = 'badge badge-' + status + ' status-toggle';
    badge.textContent = status;
}}

function applySavedStatuses() {{
    document.querySelectorAll('.status-toggle').forEach((badge) => {{
        const key = badge.dataset.statusKey;
        if (statusOverrides[key]) {{
            setBadgeStatus(badge, statusOverrides[key]);
        }}
    }});
}}

function bindStatusToggles() {{
    document.querySelectorAll('.status-toggle').forEach((badge) => {{
        badge.addEventListener('click', () => {{
            const current = badge.dataset.status || badge.textContent.trim().toLowerCase();
            const currentIndex = STATUS_CYCLE.indexOf(current);
            const next = STATUS_CYCLE[(currentIndex + 1) % STATUS_CYCLE.length] || 'new';

            statusOverrides[badge.dataset.statusKey] = next;
            const saved = saveStatusOverrides();
            setBadgeStatus(badge, next);
            applyFilters();
            showToast(saved ? 'Status saved as ' + next : 'Status changed, but browser storage blocked');
        }});
    }});
}}

function effectiveStatus(row) {{
    const badge = row.querySelector('.badge');
    return (badge && badge.dataset.status) ? badge.dataset.status : 'new';
}}

function isReadyRow(row) {{
    const status = effectiveStatus(row);
    if (status === 'ready') return true;
    if (status === 'dead' || status === 'sent' || status === 'replied' || status === 'in_progress') return false;
    return row.dataset.readyDefault === '1';
}}

function loadViewFilter() {{
    // Always open on Ready outreach — user asked for this as the default every visit.
    // (Old v1 localStorage could stick on "all" and hide ready leads.)
    return DEFAULT_VIEW_FILTER;
}}

function saveViewFilter(value) {{
    // Session-only: remember filter while this tab is open, but next visit starts at Ready.
    try {{ sessionStorage.setItem(VIEW_FILTER_KEY, value); }} catch (error) {{}}
}}

function applyFilters() {{
    const hideDead = document.getElementById('hideDeadToggle').checked;
    const filter = document.getElementById('viewFilter').value;
    saveViewFilter(filter);
    const rows = document.querySelectorAll('tbody tr');
    let deadCount = 0;
    let visibleCount = 0;

    rows.forEach((tr) => {{
        const status = effectiveStatus(tr);
        const isDead = status === 'dead';
        if (isDead) deadCount += 1;

        let show = true;
        if (hideDead && isDead) show = false;
        if (show && filter === 'ready') show = isReadyRow(tr);
        if (show && filter === 'contacted') show = status === 'sent' || status === 'replied';
        if (show && filter === 'new') show = status === 'new' || status === 'live' || status === 'pending';

        tr.style.display = show ? '' : 'none';
        if (show) visibleCount += 1;
    }});

    document.getElementById('deadCount').textContent = deadCount + ' dead ' + (hideDead ? 'hidden' : 'shown');
    document.getElementById('filterCount').textContent = visibleCount + ' shown';
}}

window.addEventListener('DOMContentLoaded', () => {{
    document.getElementById('viewFilter').value = loadViewFilter();
    applySavedStatuses();
    bindStatusToggles();
    applyFilters();
}});

function markCopied(btn) {{
    btn.classList.add('copied');
    btn.textContent = '✓ Copied!';
    setTimeout(() => {{
        btn.classList.remove('copied');
        btn.textContent = btn.classList.contains('copy-sms') ? '📱 SMS' : '✉️ Email';
    }}, 1500);
}}

function fallbackCopyText(text) {{
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    ta.style.top = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    ta.setSelectionRange(0, ta.value.length);
    const copied = document.execCommand('copy');
    document.body.removeChild(ta);
    if (!copied) throw new Error('Browser blocked copy.');
}}

async function copyMsg(text, btn) {{
    try {{
        if (navigator.clipboard && window.isSecureContext) {{
            await navigator.clipboard.writeText(text);
        }} else {{
            fallbackCopyText(text);
        }}
        markCopied(btn);
        showToast('Message copied!');
    }} catch (error) {{
        try {{
            fallbackCopyText(text);
            markCopied(btn);
            showToast('Message copied!');
        }} catch (fallbackError) {{
            window.prompt('Copy this message:', text);
            showToast('Copy prompt opened');
        }}
    }}
}}
</script>
</head>
<body>

<h1>🌳 Barrie Demo Drop — Lead Tracker</h1>
<p class="subtitle">{total} local businesses found without websites. Demo sites built and ready for outreach.</p>

<div class="tracker-controls">
  <label>
    Show
    <select id="viewFilter" onchange="applyFilters()">
      <option value="ready" selected>Ready outreach</option>
      <option value="all">All leads</option>
      <option value="contacted">Contacted</option>
      <option value="new">New (not sent)</option>
    </select>
  </label>
  <span id="filterCount" class="filter-count"></span>
  <label>
    <input type="checkbox" id="hideDeadToggle" checked onchange="applyFilters()">
    Hide dead businesses
  </label>
  <span id="deadCount" class="dead-count"></span>
</div>

<div class="summary">
  <div class="stat"><div class="stat-num">{total}</div><div class="stat-label">Total Leads</div></div>
  <div class="stat"><div class="stat-num">{contacted}</div><div class="stat-label">Contacted</div></div>
  <div class="stat"><div class="stat-num">{new_count}</div><div class="stat-label">New (Not Sent)</div></div>
  <div class="stat"><div class="stat-num">{ready_count}</div><div class="stat-label">Ready Outreach</div></div>
  <div class="stat"><div class="stat-num">{verified}</div><div class="stat-label">Cleaned & Verified</div></div>
</div>

<div class="table-wrap">
<table>
<thead>
<tr><th>#</th><th>Business</th><th>Category</th><th>Phone</th><th>Email</th><th>Social</th><th>Demo URL</th><th>Status</th><th>Copy Msg</th></tr>
</thead>
<tbody>
{rows}</tbody>
</table>
</div>

<div id="toast" class="toast">✅ Message copied!</div>

<p class="last-updated">Last updated: {now} · Generated by Hermes Agent · <a href="https://www.kumon.com/barrie-mapleview-on" target="_blank" rel="noopener">Kumon Barrie Mapleview — Humberto Domingues</a></p>

<script>
// Backup init — SMS onclick HTML must not contain raw newlines (breaks page JS).
(function () {{
    var sel = document.getElementById('viewFilter');
    if (sel) sel.value = 'ready';
    if (typeof applyFilters === 'function') applyFilters();
}})();
</script>

</body>
</html>
"""
    return html

def push_to_github():
    os.chdir(TRACKER_DIR)
    subprocess.run(["git", "add", "index.html"], check=False)
    subprocess.run(["git", "commit", "-m", f"Auto-regenerate tracker — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"], check=False)
    subprocess.run(["git", "push"], check=False)

def main():
    leads = load_leads()
    if not leads:
        print("ERROR: No leads found in CSV."); return 1
    html = generate_html(leads)
    os.makedirs(TRACKER_DIR, exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Tracker regenerated: {len(leads)} leads → {HTML_PATH}")
    push_to_github()
    print("✅ Pushed to GitHub — live at https://mexemexe02.github.io/barrie-lead-tracker/")
    return 0

if __name__ == "__main__":
    exit(main())
