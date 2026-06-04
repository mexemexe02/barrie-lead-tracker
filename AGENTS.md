# Barrie Demo Drop — Website Pipeline Project

> Shared project file for all AI agents (Hermes, Cursor, Claude Code, etc.).
> **Read this first** before doing any work on this project.

## What This Is

Humberto's side hustle: find local Barrie, Ontario businesses without websites, build professional demo sites, deploy them, and pitch the owners. **Only build infrastructure (domains, Supabase, Cloudflare) AFTER a business says yes.**

## Current State (updated 2026-06-04)

| Metric | Count |
|--------|-------|
| Total leads | 151 |
| Demo sites live | 37 |
| Needs demo sites | 114 |
| Sent / awaiting reply | 6 |
| Dead (has website) | 19 |
| Pending (draft, not sent) | 1 |

## Key Files

| File | Purpose |
|------|---------|
| `leads.csv` | **Source of truth** — all leads, statuses, demo URLs |
| `development_log.md` | **Session log** — every agent appends work done (auto-maintained via `.cursor/rules/dev-log.mdc`) |
| `barrie-lead-tracker/index.html` | Public dashboard (GitHub Pages) |
| `barrie-lead-tracker/leads.csv` | Tracker subset with Coolify URLs |
| `<business-slug>/index.html` | Individual demo sites (34 local folders) |

## The Pipeline (6 Steps)

### 1. Find Candidates
- Search YellowPages, Google, Bing for Barrie businesses by category
- Target: small owner-operators without websites
- Prioritize businesses WITH phone numbers (need contact info to pitch)

### 2. Verify No Website ⚠️ CRITICAL
- **Google + Bing search** for "[Business Name] Barrie"
- Click through non-directory results
- Check page content matches business name + Barrie/705 area code
- Social media only does NOT count as having a website
- **NEVER skip this step.** 42% of YellowPages leads had websites.

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
- SMS template: "Hi, I'm Humberto — local Barrie biz owner (Kumon Mapleview). I noticed [Business] doesn't have a website yet. I put together a quick demo: [URL]. If you're interested, I can build you a proper professional site. No pressure. Worth a look?"
- Email: CC mexemexe02@gmail.com on EVERY outreach
- **NEVER send without Humberto's approval**
- Never say "free", "no catch", "it's yours" — professional positioning only

## Quality Standards

### Demo Site Requirements
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

- ✅ Check `leads.csv` status first — if `sent`, do NOT reach out again
- ✅ Let Humberto review and approve before sending
- ✅ Use Kumon Mapleview as local credibility anchor
- ✅ CC mexemexe02@gmail.com on every email
- ❌ Never send without approval
- ❌ Never use "free of charge", "no catch", "it's yours"
- ❌ Never state a price in first contact

## GitHub / Deployment

- GitHub: `mexemexe02` account
- Tracker: https://mexemexe02.github.io/barrie-lead-tracker/
- Coolify: http://178.156.135.237:8000 (context: `schedulo-coolify`)
- Coolify server UUID: `cgcwkkccsws8s8wkkswsco8k`
- Coolify project UUID: `obgw2u5jxkddqa3p6nr8fo9u`
- Deploy command: `gh api repos/mexemexe02/<repo>/pages -X POST -f "source[branch]=master" -f "source[path]=/"`
- **GitHub Pages > Coolify** when Coolify is being flaky

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
| `new` | Verified no website, demo built or pending |
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

- **Don't rebuild existing sites** — check `leads.csv` demo_url field and the Coolify app list first
- **Don't copy-paste templates** — 40-60% of content can leak between sites
- **Verify images after subagent builds** — they fabricate Unsplash IDs
- **Ampersands in business names** break shell commands — use Python for CSV operations
- **Don't trust curl-only domain checks** — ISP DNS hijacking causes false negatives
- **Tracker HTML regenerated from CSV** — never hand-edit the HTML
- **Fils Rest already has a Coolify app** (UUID: yk8k7v8eluzwvorpjmia5t04) — don't rebuild
