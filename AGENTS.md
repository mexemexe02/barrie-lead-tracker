# Barrie Demo Drop — Website Pipeline Project

> Shared project file for all AI agents (Hermes, Cursor, Claude Code, etc.).
> **Read this first** before doing any work on this project.

## What This Is

Humberto's side hustle: find local Barrie, Ontario businesses without websites, build professional demo sites, deploy them, and pitch the owners. **Only build infrastructure (domains, Supabase, Cloudflare) AFTER a business says yes.**

## Current State (updated 2026-06-08)

| Metric | Count |
|--------|-------|
| Total leads | 151 |
| With demo URL | 67 |
| Ready for outreach (`ready`) | 14 |
| Sent / awaiting reply (`sent`) | 20 |
| Dead (has website) | 38 |
| New (no outreach yet) | 76 |
| Pending (draft, not sent) | 1 |

### Outreach priority (Cursor session 2026-06-08) — read before more SMS or builds

**Cold SMS failed:** 23 sends, 0 replies. Root cause: ~16 wrong numbers (Starbucks, Hamilton Bros, schools, etc.) + 7 texts to leads that already had websites.

**Do NOT:** resend SMS to wrong-number rows; use tracker `Copy SMS` without reading audit first; build new demos while 14 `ready` leads + wrong-SMS re-outreach targets still need contact.

**DO:** FB DM or call using corrected contacts. Full plans in:

| File | Purpose |
|------|---------|
| `outreach-sms-audit-and-corrected-list.md` | All 23 SMS audited; Tier A–D re-outreach (FB DM / call, not SMS resend) |
| `outreach-ready-enrichment.md` | 14 `ready` leads — owner names, FB links, copy-paste DM drafts |
| `browser-sms-verification-direct.txt` | Canada411/FB browser proof for wrong vs correct numbers |

**Tier A (wrong SMS — pitch never reached them):** Thornton Cafe (FB), Express Country Style (705-730-0944), The Installer (705-796-3499), Huronia Hardwood (705-739-9453), B8's (FB).

**Top FB DM targets (ready, never SMS'd):** Jeff Chadwick (705-733-7151, Jchadwickpainting@gmail.com), Ray Parsons, Dennis (Prestige Classic).

## Key Files

| File | Purpose |
|------|---------|
| `leads.csv` | **Source of truth** — all leads, statuses, demo URLs, SMS audit notes |
| `development_log.md` | **Session log** — every agent appends work done (auto-maintained via `.cursor/rules/dev-log.mdc`) |
| `barrie-lead-tracker/index.html` | Public dashboard (GitHub Pages) — regenerate from root `leads.csv` |
| `barrie-lead-tracker/leads.csv` | GitHub copy of leads for admin tracker raw CSV URL — **keep synced with root `leads.csv`** |
| `barrie-tracker-app/` | Persistent admin tracker app deployed on Coolify |
| `<business-slug>/index.html` | Individual demo sites (34 local folders) |

## The Pipeline (6 Steps)

### 1. Find Candidates
- Search YellowPages, Google, Bing for Barrie businesses by category
- Target: small owner-operators without websites
- Prioritize businesses WITH phone numbers (need contact info to pitch)

### 2. Verify No Website ⚠️ CRITICAL
- **Use browser-harness** (Chrome CDP) for definitive verification. Run `browser-harness --doctor` — daemon should show alive. On Windows: `Get-Content script.py | browser-harness` (helpers pre-imported; see `C:\Users\Humberto\browser-harness\SKILL.md`).
- **Google + Bing search** in the real browser for "[Business Name] Barrie"
- Click through non-directory results in the real browser
- Check page content matches business name + Barrie/705 area code
- Social media only does NOT count as having a website
- **NEVER skip this step.** 42% of YellowPages leads had websites.
- browser-harness installed at: `C:\Users\Humberto\browser-harness` (editable install)
- CDP URL: `--remote-debugging-port=9224 --user-data-dir=C:\temp\edge-cdp`

### 2b. Enrich Contact Info
- For every viable no-website lead, research owner/contact name, email, active social profile, and useful outreach notes.
- Always keep watching for official website evidence during enrichment. If an official website is found, stop enrichment and mark the lead `dead`.
- Preferred sources: Facebook About, Instagram bio, LinkedIn, Google Business Profile snippets, YellowPages/411/ProfileCanada, local articles, sponsorship pages, business registry references, and PDFs.
- Add contact findings to the persistent Coolify admin tracker first. If editing CSV directly, update `contact_name`, `email`, `social`, and `notes`.
- A lead is only truly outreach-ready when it has no official website and at least one reliable contact route: phone, email, or active social.

### 2c. Outreach Readiness Comes Before More Builds
- **Before building any more demo sites, check existing demos first.** Filter for open leads with a `demo_url` and at least one contact route (`phone`, `email`, or `social`).
- If matching leads exist, prioritize preparing those leads for outreach instead of building more sites. Humberto should be able to click `Ready Outreach` and immediately see usable demo-site prospects.
- `Ready Outreach` must include both manually marked `ready` leads and inferred-ready leads: not `dead`/`sent`/`replied`/`in_progress`, has a live demo URL, has no official website evidence, and has at least one usable contact route.
- Keep `Ready to Text` stricter than `Ready Outreach`: SMS requires a real non-toll-free phone that has been verified or intentionally accepted for outreach.
- Do not leave demo-built leads hidden as plain `new`/`live` forever. After verification/contact cleanup, mark the lead `ready` or make sure the tracker can infer it as ready.

### 3. Build Demo Site
- Single-file HTML (all CSS/JS inline) at `website-projects/<slug>/index.html`
- Dark/dramatic themes only — no light blue/white templates
- Google Fonts (NOT system fonts), Font Awesome icons (NOT emoji)
- Hero with real Unsplash image + `background-blend-mode: multiply` + dark overlay + text-shadow
- 1500+ lines, well-formatted CSS (NOT minified)
- 6 service cards, testimonials, contact form, responsive
- **Every site MUST have a unique design** — never copy-paste themes

### 4. Deploy
- `git init && commit && gh repo create <slug> --public --push`
- Enable GitHub Pages: `gh api repos/mexemexe02/<slug>/pages -X POST -f "source[branch]=master" -f "source[path]=/"`
- Live URL: `https://mexemexe02.github.io/<slug>/`
- Also deploy to Coolify if available (server: 178.156.135.237:8000)

### 5. Track
- **Claim first**: update lead status to `in_progress` in leads.csv BEFORE building (see Multi-Agent Coordination above)
- After build: set status back to `new`, add `demo_url` and date
- Run `python regenerate-tracker.py` to update the dashboard
- Append to `development_log.md` with full session entry
- Push to GitHub

### 6. Pitch (DRAFT ONLY — Humberto approves before sending)
- SMS template: "Hi! I'm Humberto, a fellow Barrie business owner (Kumon Mapleview). I also build websites, so I built a free demo website for [Business] — take a look: [URL] No obligation — if you like it, it's yours. Let me know what you think of the site. :-) Cheers."
- Email: CC mexemexe02@gmail.com on EVERY outreach
- **NEVER send without Humberto's approval**
- Never say "free", "no catch", "it's yours" — professional positioning only

## Quality Standards

### Demo Site Requirements
- ✅ **MOBILE-FIRST — must work perfectly on phones (primary audience)**
- ✅ Responsive at 3+ breakpoints (480px, 768px, 1024px minimum)
- ✅ Touch-friendly tap targets (min 44px for all buttons/links)
- ✅ Proper viewport meta tag
- ✅ No horizontal scroll on any device
- ✅ Readable font sizes on small screens (min 16px body text on mobile)
- ✅ Cart/checkout usable on phone screens
- ✅ Dark theme (charcoal/industrial/warm tones)
- ✅ Real hero image (Unsplash, verified working)
- ✅ Google Fonts (Bebas Neue, Playfair Display, Cormorant Garamond + Inter)
- ✅ Font Awesome CDN icons (NO emoji)
- ✅ Hero: `background-blend-mode: multiply` + dark overlay + text-shadow
- ✅ Styled service cards with hover effects
- ✅ Contact form with styled inputs
- ✅ 1500+ lines, NO minified CSS
- ✅ Mobile responsive (3 breakpoints)

### Rejection Criteria
- ❌ Light blue/white color scheme
- ❌ No hero image (solid color hero)
- ❌ System fonts only
- ❌ Emoji icons
- ❌ Minified CSS
- ❌ Under 200 lines
- ❌ Placeholder/dashed-border images

## Image Rules

- **Subagents hallucinate Unsplash photo IDs** — always verify with curl
- After any site build: `curl -sI <image-url>` — expect 200
- Real Unsplash IDs are 28-char hex; fake ones work on some sizes but 404 on others
- Category-specific images: HVAC→technicians/AC, Roofing→roofs/shingles, Restaurant→food/interior
- When in doubt, use these known-working images:
  - Hero: `photo-1555396273-367ea4eb4db5` (restaurant), `photo-1501339847302-ac426a4a7cbb` (cafe)
  - Food: `photo-1551183053-bf91a1d81141`, `photo-1414235077428-338989a2e8c0`
  - Construction: `photo-1600585152220-90363fe7e115`, `photo-1560185893-a55cbc8c57e8`

## Outreach Rules

- ✅ Check `Ready Outreach` before building more demos; existing demo sites with contact routes are the priority.
- ✅ Check `leads.csv` status first — if `sent`, do NOT reach out again
- ✅ Let Humberto review and approve before sending
- ✅ Use Kumon Mapleview as local credibility anchor
- ✅ CC mexemexe02@gmail.com on every email
- ✅ If no owner/contact name is known, start outreach with `Hi,` — never greet a business name like a person.
- ❌ Never send without approval
- ❌ Never use "free of charge", "no catch", "it's yours"
- ❌ Never state a price in first contact

## GitHub / Deployment

- GitHub: `mexemexe02` account
- Tracker: https://mexemexe02.github.io/barrie-lead-tracker/
- Persistent admin tracker: `http://ew7x9b6nzzxwql770as22map.178.156.135.237.sslip.io`
- Admin tracker GitHub repo: `https://github.com/mexemexe02/barrie-tracker-app`
- Coolify: http://178.156.135.237:8000 (context: `schedulo-coolify`)
- Coolify server UUID: `cgcwkkccsws8s8wkkswsco8k`
- Coolify project UUID: `obgw2u5jxkddqa3p6nr8fo9u`
- Coolify project name for tracker app: `Barrie Demo Batch 2`
- Coolify admin tracker app UUID: `ew7x9b6nzzxwql770as22map`
- Deploy command: `gh api repos/mexemexe02/<repo>/pages -X POST -f "source[branch]=master" -f "source[path]=/"`
- **GitHub Pages > Coolify** when Coolify is being flaky

## Persistent Admin Tracker (Humberto's main UI)

**Humberto uses the Coolify admin tracker as his primary dashboard** — not the GitHub Pages static tracker.

The static GitHub Pages tracker is still generated from `leads.csv` for public/reference, but manual outreach/status/contact edits must use the Coolify admin tracker when Humberto wants them remembered.

- URL: `http://ew7x9b6nzzxwql770as22map.178.156.135.237.sslip.io`
- Repo: `mexemexe02/barrie-tracker-app`
- Coolify app: `barrie-tracker-app` in `Barrie Demo Batch 2`
- App UUID: `ew7x9b6nzzxwql770as22map`
- Persistent storage: Coolify volume mounted at `/data`
- State file inside container: `/data/tracker-state.json`
- Full lead source: `https://raw.githubusercontent.com/mexemexe02/barrie-lead-tracker/master/leads.csv`
- Auth: `ADMIN_TOKEN` is stored in the Coolify app environment. Do not commit or print it in logs.

### Tracker Rules

- Do **not** hand-edit `barrie-lead-tracker/index.html`; it is generated and changes will be overwritten.
- For permanent manual status/contact changes, use the Coolify admin tracker.
- The admin tracker overlays saved changes from `/data/tracker-state.json` on top of the latest CSV.
- If an official website is found, mark the lead `dead` and add notes explaining the website evidence.
- Owner names, emails, social URLs, and outreach notes should be added in the admin tracker when found.
- For `new` leads, owner/email fields should be treated as missing research work, not as confirmed unavailable.
- If the admin tracker code changes, push `barrie-tracker-app` to GitHub and redeploy Coolify app `ew7x9b6nzzxwql770as22map`.

## Contacts

- Humberto Domingues (NO Z — not Dominguez)
- Outreach email: humbertobizes@gmail.com
- Personal email (CC copies): mexemexe02@gmail.com
- Kumon center: https://www.kumon.com/barrie-mapleview-on

## Cron Jobs (Hermes)

| Job | Schedule | Purpose |
|-----|----------|---------|
| Barrie Lead Finder | Daily 8am ET | Find 5 new businesses |
| Reply Watcher | 10am + 4pm ET | Check for replies |
| Tracker Regenerator | Daily 8:10am ET | Rebuild dashboard from CSV |

## Lead Status Values

| Status | Meaning |
|--------|---------|
| `new` | Verified no website, demo pending or not yet outreach-prepared |
| `ready` | Demo is live, no official website evidence, and at least one usable contact route exists |
| `in_progress` | ⚠️ Another agent is actively building this demo — **DO NOT TOUCH** |
| `sent` | Outreach was delivered |
| `pending` | Pitch drafted, awaiting Humberto to send |
| `replied` | Business responded |
| `dead` | Already has a website, or bad info |

## ⚠️ Multi-Agent Coordination — READ BEFORE DOING ANYTHING

**You are not alone.** Hermes and Cursor both work on this pipeline. They share the same files. Coordination is enforced by `.cursor/rules/dev-log.mdc`.

### Before Building ANY Demo Site

1. **Read leads.csv fresh** — another agent may have changed statuses
2. **Read development_log.md** — see what was claimed today
3. **CLAIM the lead** — update status from `new` → `in_progress` in leads.csv BEFORE starting
4. **Log the claim** — append to development_log.md: `### Claimed: [business name] ([slug])`

### After Building

1. **Update leads.csv** — set status back to `new`, add `demo_url`, update `notes`
2. **Regenerate tracker** — `python regenerate-tracker.py`
3. **Log completion** — append full entry to development_log.md
4. **Push to GitHub**

### Never

- ❌ Work on a lead with status `in_progress` — another agent has it
- ❌ Change status from `in_progress` unless you're the one who set it
- ❌ Skip reading the log at session start

## Common Pitfalls

- **Zero `ready` rows does not mean zero outreach prospects** — first count open leads with `demo_url` plus phone/email/social, then fix status/readiness metadata.
- **Don't rebuild existing sites** — check `leads.csv` demo_url field and the Coolify app list first
- **Don't copy-paste templates** — 40-60% of content can leak between sites
- **Verify images after subagent builds** — they fabricate Unsplash IDs
- **Ampersands in business names** break shell commands — use Python for CSV operations
- **Don't trust curl-only domain checks** — ISP DNS hijacking causes false negatives
- **Tracker HTML regenerated from CSV** — never hand-edit the HTML
- **Fils Rest already has a Coolify app** (UUID: yk8k7v8eluzwvorpjmia5t04) — don't rebuild
