import csv, html, json, os

rows = []
csv_path = r'C:\Users\Humberto\website-projects\barrie-lead-tracker\leads.csv'
with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

def make_sms(biz, cat, url):
    return f"Hi, I'm Humberto \u2014 local Barrie biz owner. I noticed {biz} doesn't have a website yet. I put together a quick demo to show you what's possible: {url} \u2014 If you're interested, I can build you a proper professional site or sell you this one, but no pressure; I just wanted to show you what I can do for you. I'm just starting off my business so I think we can help each other. Hope to meet you soon. Cheers."

def make_email(biz, cat, url):
    return f"Subject: Website demo for {biz}\n\nHi,\n\nMy name is Humberto Dominguez. I run the Kumon Math & Reading Centre on Mapleview and also build websites for local Barrie businesses.\n\nI noticed {biz} doesn't have a website yet. I put together a quick one-page demo to show what's possible for a {cat.lower()} business like yours:\n{url}\n\nIf you're interested, I can build you a proper professional site or sell you this one, but no pressure \u2014 just wanted to show what I can do. I'm just starting off my business so I think we can help each other. Hope to meet you soon.\n\nCheers,\nHumberto"

def short_url(url):
    u = url.replace('http://','').replace('https://','')
    return u[:42] + chr(8230) if len(u) > 45 else u

sent = sum(1 for r in rows if r['status'] == 'sent')
pending = sum(1 for r in rows if r['status'] == 'pending')
new = sum(1 for r in rows if r['status'] == 'new')
total = len(rows)

table_rows = []
sms_data = {}
email_data = {}
status_data = {}

for i, r in enumerate(rows, 1):
    name = html.escape(r['business'])
    cat = html.escape(r['category'])
    phone = r['phone'].strip()
    email = r['email'].strip()
    demo = r['demo_url'].strip()
    status = r['status'].strip()
    
    ph = f'<a href="tel:{phone}" class="url">{html.escape(phone)}</a>' if phone else '\u2014'
    
    if email and '@' in email:
        em = f'<a href="mailto:{html.escape(email)}" class="url">{html.escape(email)}</a>'
    elif email:
        em = html.escape(email)
    else:
        em = '\u2014'
    
    has_url = demo and 'TBD' not in demo
    url_cell = f'<a href="{html.escape(demo)}" target="_blank" class="url" rel="noopener">{html.escape(short_url(demo))}</a>' if has_url else '\u2014'
    
    status_data[f"status-{i}"] = status
    badge = f'<span class="badge badge-{status} status-toggle" data-lead="{i}" data-status="{status}" title="Click to cycle: new \u2192 sent \u2192 pending">{status}</span>'
    
    buttons = []
    if has_url:
        if phone:
            sms_data[f"sms-{i}"] = make_sms(r['business'], r['category'], demo)
            buttons.append(f'<button class="copy-btn pitch-copy" data-pitch-id="sms-{i}" title="Copy SMS">SMS</button>')
            buttons.append(f'<button class="edit-btn pitch-edit" data-pitch-id="sms-{i}" data-lead="{i}" title="Edit SMS text">Edit</button>')
        if email and '@' in email:
            email_data[f"email-{i}"] = make_email(r['business'], r['category'], demo)
            buttons.append(f'<button class="copy-btn pitch-copy" data-pitch-id="email-{i}" title="Copy Email">Email</button>')
            buttons.append(f'<button class="edit-btn pitch-edit" data-pitch-id="email-{i}" data-lead="{i}" title="Edit Email text">Edit</button>')
    
    action_cell = ' '.join(buttons) if buttons else '\u2014'
    
    table_rows.append(f'<tr id="lead-{i}"><td>{i}</td><td>{name}</td><td>{cat}</td><td>{ph}</td><td>{em}</td><td>{url_cell}</td><td>{badge}</td><td>{action_cell}</td></tr>')

pitches_json = json.dumps({**sms_data, **email_data})
default_statuses = json.dumps(status_data)

html_out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Barrie Demo Drop - Lead Tracker</title>
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,sans-serif;background:#0f1117;color:#e0e0e0;padding:20px}}
h1{{color:#c9a84c;margin-bottom:4px;font-size:1.4rem}}
.subtitle{{color:#888;margin-bottom:12px;font-size:0.9rem}}
.toolbar{{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;align-items:center}}
.toolbar button{{background:#2a2d3a;color:#888;border:1px solid #3a3d4a;padding:6px 14px;border-radius:4px;cursor:pointer;font-size:0.78rem}}
.toolbar button:hover{{color:#c9a84c;border-color:#c9a84c}}
.table-wrap{{overflow-x:auto;margin-bottom:16px}}
table{{width:100%;border-collapse:collapse;font-size:0.82rem;min-width:1050px}}
th{{background:#1a1d2a;color:#c9a84c;padding:10px 8px;text-align:left;font-weight:600;border-bottom:2px solid #2a2d3a;white-space:nowrap}}
td{{padding:8px;border-bottom:1px solid #1a1d2a;vertical-align:middle}}
tr:hover{{background:#1a1d2a}}
.url{{color:#60a5fa;font-size:0.78rem;word-break:break-all;text-decoration:none}}
.url:hover{{text-decoration:underline}}
.badge{{display:inline-block;padding:3px 10px;border-radius:10px;font-size:0.72rem;font-weight:600;white-space:nowrap;cursor:pointer;user-select:none;transition:all .2s}}
.badge:hover{{filter:brightness(1.3);transform:scale(1.05)}}
.badge-new{{background:#166534;color:#4ade80}}
.badge-sent{{background:#1e3a5f;color:#60a5fa}}
.badge-pending{{background:#5c4a1f;color:#fbbf24}}
.copy-btn,.edit-btn{{background:#2a2d3a;color:#c9a84c;border:1px solid #3a3d4a;padding:3px 10px;border-radius:4px;cursor:pointer;font-size:0.78rem;margin:1px 2px;white-space:nowrap}}
.copy-btn:hover,.edit-btn:hover{{background:#3a3d4a;border-color:#c9a84c}}
.copy-btn.copied{{background:#166534;color:#4ade80;border-color:#4ade80}}
.edit-btn{{color:#888;border-color:#2a2d3a;padding:3px 6px}}
.edit-btn:hover{{color:#c9a84c}}
.summary{{display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap;align-items:center}}
.stat{{background:#1a1d2a;padding:12px 18px;border-radius:8px;text-align:center;min-width:70px}}
.stat-num{{font-size:1.6rem;font-weight:700;color:#c9a84c;transition:all .3s}}
.stat-label{{font-size:0.75rem;color:#888}}
.last-updated{{color:#666;font-size:0.75rem;margin-top:24px;text-align:center}}
.last-updated a{{color:#c9a84c;text-decoration:none}}
.modal-overlay{{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:1000;justify-content:center;align-items:center}}
.modal-overlay.active{{display:flex}}
.modal{{background:#1a1d2a;border:1px solid #3a3d4a;border-radius:8px;padding:20px;max-width:550px;width:90%;max-height:80vh;display:flex;flex-direction:column}}
.modal h3{{color:#c9a84c;margin-bottom:10px;font-size:1rem}}
.modal textarea{{flex:1;background:#0f1117;color:#e0e0e0;border:1px solid #3a3d4a;border-radius:4px;padding:10px;font-family:inherit;font-size:0.85rem;min-height:200px;resize:vertical}}
.modal-actions{{display:flex;gap:8px;margin-top:12px;justify-content:flex-end}}
.modal-actions button{{padding:8px 16px;border-radius:4px;cursor:pointer;font-size:0.82rem;border:none}}
.modal-save{{background:#c9a84c;color:#0f1117;font-weight:600}}
.modal-cancel{{background:#2a2d3a;color:#888}}
.toast{{position:fixed;bottom:20px;right:20px;background:#166534;color:#4ade80;padding:10px 18px;border-radius:6px;font-size:0.82rem;z-index:2000;opacity:0;transition:opacity .3s;pointer-events:none}}
.toast.show{{opacity:1}}
</style>
<script>
const DEFAULT_PITCHES = {pitches_json};
const DEFAULT_STATUSES = {default_statuses};

let pitches = JSON.parse(localStorage.getItem('barrie_pitches') || 'null') || {{...DEFAULT_PITCHES}};
let statuses = JSON.parse(localStorage.getItem('barrie_statuses') || 'null') || {{...DEFAULT_STATUSES}};

function savePitches() {{ localStorage.setItem('barrie_pitches', JSON.stringify(pitches)); }}
function saveStatuses() {{ localStorage.setItem('barrie_statuses', JSON.stringify(statuses)); updateStats(); }}

function updateStats() {{
    let s=0, p=0, n=0;
    Object.values(statuses).forEach(function(st) {{
        if(st==='sent')s++; else if(st==='pending')p++; else if(st==='new')n++;
    }});
    document.getElementById('stat-sent').textContent = s;
    document.getElementById('stat-pending').textContent = p;
    document.getElementById('stat-new').textContent = n;
}}

function showToast(msg) {{
    var t=document.getElementById('toast');
    t.textContent=msg; t.classList.add('show');
    setTimeout(function(){{t.classList.remove('show')}},2500);
}}

document.addEventListener('DOMContentLoaded', function() {{
    document.querySelectorAll('.pitch-copy').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
            var id=this.getAttribute('data-pitch-id');
            var text=pitches[id] || DEFAULT_PITCHES[id];
            navigator.clipboard.writeText(text).then(function() {{
                btn.textContent='Copied!'; btn.classList.add('copied');
                setTimeout(function(){{btn.classList.remove('copied'); btn.textContent=btn.title.includes('SMS')?'SMS':'Email'}},2000);
            }});
        }});
    }});
    document.querySelectorAll('.pitch-edit').forEach(function(btn) {{
        btn.addEventListener('click', function() {{
            var id=this.getAttribute('data-pitch-id');
            var text=pitches[id] || DEFAULT_PITCHES[id];
            document.getElementById('edit-pitch-id').value=id;
            document.getElementById('edit-pitch-text').value=text;
            document.getElementById('edit-modal').classList.add('active');
        }});
    }});
    document.querySelectorAll('.status-toggle').forEach(function(badge) {{
        badge.addEventListener('click', function() {{
            var lead=this.getAttribute('data-lead');
            var key='status-'+lead;
            var current=statuses[key] || DEFAULT_STATUSES[key];
            var next=current==='new'?'sent':current==='sent'?'pending':'new';
            statuses[key]=next; saveStatuses();
            this.setAttribute('data-status',next);
            this.className='badge badge-'+next+' status-toggle';
            this.textContent=next;
            showToast('Lead '+lead+' \u2192 '+next);
        }});
    }});
    document.getElementById('modal-save').addEventListener('click', function() {{
        var id=document.getElementById('edit-pitch-id').value;
        var text=document.getElementById('edit-pitch-text').value;
        pitches[id]=text; savePitches();
        document.getElementById('edit-modal').classList.remove('active');
        showToast('Pitch saved!');
    }});
    document.getElementById('modal-cancel').addEventListener('click', function() {{
        document.getElementById('edit-modal').classList.remove('active');
    }});
    document.getElementById('btn-reset').addEventListener('click', function() {{
        if(confirm('Reset all pitches and statuses to defaults?')) {{
            localStorage.removeItem('barrie_pitches');
            localStorage.removeItem('barrie_statuses');
            pitches={{...DEFAULT_PITCHES}}; statuses={{...DEFAULT_STATUSES}};
            document.querySelectorAll('.status-toggle').forEach(function(b) {{
                var lead=b.getAttribute('data-lead'); var key='status-'+lead;
                var st=DEFAULT_STATUSES[key];
                b.setAttribute('data-status',st);
                b.className='badge badge-'+st+' status-toggle';
                b.textContent=st;
            }});
            updateStats(); showToast('Reset to defaults');
        }}
    }});
    document.getElementById('btn-export').addEventListener('click', function() {{
        var data={{pitches:pitches,statuses:statuses}};
        navigator.clipboard.writeText(JSON.stringify(data,null,2)).then(function() {{
            showToast('State copied to clipboard - save as backup');
        }});
    }});
    updateStats();
}});
</script>
</head>
<body>

<h1>Barrie Demo Drop - Lead Tracker</h1>
<p class="subtitle">{total} verified Barrie businesses without websites</p>

<div class="toolbar">
  <button id="btn-reset">Reset</button>
  <button id="btn-export">Backup State</button>
  <span style="color:#666;font-size:0.75rem;margin-left:8px">Click status badges to change &bull; Click Edit to customize pitch text</span>
</div>

<div class="summary">
  <div class="stat"><div class="stat-num">{total}</div><div class="stat-label">Total</div></div>
  <div class="stat"><div class="stat-num" id="stat-sent">0</div><div class="stat-label">Sent</div></div>
  <div class="stat"><div class="stat-num" id="stat-pending">0</div><div class="stat-label">Pending</div></div>
  <div class="stat"><div class="stat-num" id="stat-new">0</div><div class="stat-label">New</div></div>
</div>

<div class="table-wrap">
<table>
<thead><tr><th>#</th><th>Business</th><th>Category</th><th>Phone</th><th>Email</th><th>Demo URL</th><th>Status</th><th>Actions</th></tr></thead>
<tbody>
{chr(10).join(table_rows)}
</tbody>
</table>
</div>

<div id="edit-modal" class="modal-overlay">
  <div class="modal">
    <h3>Edit Pitch Text</h3>
    <input type="hidden" id="edit-pitch-id">
    <textarea id="edit-pitch-text"></textarea>
    <div class="modal-actions">
      <button class="modal-cancel" id="modal-cancel">Cancel</button>
      <button class="modal-save" id="modal-save">Save and Close</button>
    </div>
  </div>
</div>

<div id="toast" class="toast"></div>

<p class="last-updated">Updated 2026-06-03 &middot; <a href="https://github.com/mexemexe02/barrie-lead-tracker">GitHub</a></p>

</body>
</html>'''

out_path = r'C:\Users\Humberto\website-projects\barrie-lead-tracker\index.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html_out)

print(f'Done: {total} leads, {sent} sent, {pending} pending, {new} new')
print(f'HTML written to: {out_path}')
