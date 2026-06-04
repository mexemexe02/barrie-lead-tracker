# Barrie Demo Drop — Development Log

> Shared session log for all AI agents (Hermes, Cursor, Claude Code, etc.).
> **Every agent appends to this file** after completing work.
> Coordination rules: `.cursor/rules/dev-log.mdc` | Project rules: `AGENTS.md`

---

## Baseline (preexisting as of 2026-06-04)

37 demo sites live. 151 total leads (6 sent, 19 dead, 1 pending, 125 new/demo-ready).
Full state and pipeline rules in `AGENTS.md`. Per-lead details in `leads.csv`.
Tracker dashboard: https://mexemexe02.github.io/barrie-lead-tracker/

### Active Sites (sent, awaiting reply)
- Pacheco Mobile Mechanic, Carmen's Maid Service, Blanchettes Services, Atrium Landscapes, Tree Time Outdoor Services, Pawtricia's Dog Grooming

### Dead (already had websites — demos built but not pitched)
- Pawfection Grooming, Grass Barber, Strong Roots Landscaping, TLC Landscapes, Eaglecrest Painting, Wagg's Painting, Fresh Coat Painting, Luv To Paint, Georgian Detailing, Foxcon Contracting, 7 Oaks Tree Care, + 8 more

---

## 2026-06-04 — Project Infrastructure

### Summary
Established multi-agent coordination protocol (Cursor + Hermes). Created claiming system to prevent double-work.

### Actions
- Created `.cursor/rules/dev-log.mdc` — Cursor auto-loads coordination rules (alwaysApply: true)
- Updated `AGENTS.md` — added Multi-Agent Coordination section, `in_progress` status, claiming workflow
- Updated Pipeline Step 5 (Track) — requires claiming before building
- Created `development_log.md` — this file, with baseline entry
- Created `cursor-session-prompt.txt` — ready-to-use prompt for Cursor sessions

### Key Decisions
- Chose `in_progress` status in CSV as the claiming mechanism — simple, both agents can read/write CSV
- Rule file is `alwaysApply: true` so Cursor follows protocol without user prompting
- Did NOT backfill all 37 sites into log — AGENTS.md + leads.csv are the ground truth for historical state
- Development log is forward-looking (session activity), not a state snapshot

### Files Changed
- `.cursor/rules/dev-log.mdc` — NEW: coordination rules (session start, claiming, logging, conflict prevention)
- `AGENTS.md` — updated: status values table, multi-agent coordination section, pipeline step 5
- `development_log.md` — NEW: this file with baseline + today's entry
- `cursor-session-prompt.txt` — NEW: convenience prompt for Cursor

### Blockers / Notes
- None. Protocol is live. Both agents should now follow the claiming workflow.
