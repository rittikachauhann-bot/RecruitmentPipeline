# Recruitment Pipeline — Setup Guide

## Quick start

```bash
cd ~/recruitment_pipeline
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
python pipeline_cli.py status
```

## Commands

| Command | What it does |
|---------|-------------|
| `python pipeline_cli.py status` | Show full pipeline with stages and scores |
| `python pipeline_cli.py score` | Paste a JD → get match % + auto-add if ≥85% |
| `python pipeline_cli.py apply RC-DELO-2847-2026` | Draft + send application email |
| `python pipeline_cli.py followup` | Send overdue follow-ups (due today or past) |
| `python pipeline_cli.py prep RC-ACCE-7263-2026` | Generate interview prep brief |
| `python pipeline_cli.py report` | Weekly pipeline status report |
| `python pipeline_cli.py add` | Manually add a job |
| `python pipeline_cli.py update RC-CAPG-6128-2026 Applied` | Update stage |

## Gmail setup (to actually send emails)

1. Go to https://console.cloud.google.com
2. Create project `RitikaJobApply`
3. Enable Gmail API
4. Credentials → Create → OAuth 2.0 Client ID → Desktop App
5. Download as `credentials.json` into `~/recruitment_pipeline/`
6. First send will open a browser for Google sign-in → creates `token.json`

**Without credentials.json** — emails are saved as `.txt` files in `drafts/`

## Files

```
recruitment_pipeline/
├── config.py           — all settings + initial pipeline data
├── pipeline_db.py      — read/write pipeline.json
├── claude_agents.py    — all 5 Claude-powered agent functions
├── gmail_sender.py     — Gmail OAuth sender
├── pipeline_cli.py     — main CLI
├── pipeline.json       — live pipeline state (auto-created)
├── drafts/             — saved email drafts
├── interview_briefs/   — saved prep briefs
└── reports/            — saved weekly reports
```

## Priority actions (as of 1 May 2026)

1. `python pipeline_cli.py prep RC-ACCE-7263-2026` — Accenture interview Wed 7 May
2. `python pipeline_cli.py followup` — HSBC due 4 May, Accenture due 5 May
3. `python pipeline_cli.py apply RC-CAPG-6128-2026` — Move Capgemini from Discovered
4. `python pipeline_cli.py apply RC-BCGI-3847-2026` — Move BCG from Discovered
5. `python pipeline_cli.py prep RC-DELO-2847-2026` — Deloitte interview Fri 9 May
