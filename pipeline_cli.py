#!/usr/bin/env python3
"""
Recruitment Pipeline CLI — Ritika Chouhan
Usage:
  python pipeline_cli.py status          # Show full pipeline
  python pipeline_cli.py score           # Score a new job (interactive)
  python pipeline_cli.py apply <ref_id>  # Draft + send application email
  python pipeline_cli.py followup        # Send overdue follow-ups
  python pipeline_cli.py prep <ref_id>   # Generate interview prep brief
  python pipeline_cli.py report          # Weekly pipeline report
  python pipeline_cli.py add             # Add a new job to pipeline
  python pipeline_cli.py update <ref_id> <stage>  # Update job stage
  python pipeline_cli.py search          # Search Naukri + LinkedIn for new jobs
  python pipeline_cli.py search naukri   # Search Naukri only
  python pipeline_cli.py search linkedin # Search LinkedIn only
"""

import sys
import os
from datetime import date, datetime

# allow running from any directory
sys.path.insert(0, os.path.dirname(__file__))

import pipeline_db as db
import claude_agents as agents
from config import AUTO_APPLY_THRESHOLD, ANTHROPIC_API_KEY


STAGES = ["Discovered", "Applied", "Screening", "Interview", "Offer", "Rejected"]
STAGE_EMOJI = {
    "Discovered": "🔍",
    "Applied": "📤",
    "Screening": "📞",
    "Interview": "🎯",
    "Offer": "🎉",
    "Rejected": "❌",
}


def _check_api_key():
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)


def _days_since(date_str: str) -> int:
    if not date_str:
        return 0
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (date.today() - d).days
    except Exception:
        return 0


def cmd_status():
    pipeline = db.load()
    print(f"\n{'='*70}")
    print(f"  RITIKA CHOUHAN — RECRUITMENT PIPELINE  ({date.today()})")
    print(f"{'='*70}")
    print(f"  {'#':<4} {'Company':<22} {'Role':<32} {'Stage':<12} {'Score':<6} {'Days'}")
    print(f"  {'-'*4} {'-'*22} {'-'*32} {'-'*12} {'-'*6} {'-'*5}")
    for i, j in enumerate(pipeline, 1):
        stage = j["stage"]
        emoji = STAGE_EMOJI.get(stage, "")
        days = _days_since(j.get("applied_date")) if j.get("applied_date") else "-"
        print(
            f"  {i:<4} {j['company'][:22]:<22} {j['role'][:32]:<32} "
            f"{emoji} {stage:<10} {j.get('match_score', '?'):>4}%  {days}"
        )

    # Stage summary
    counts = {}
    for j in pipeline:
        counts[j["stage"]] = counts.get(j["stage"], 0) + 1
    print(f"\n  Summary: ", end="")
    print("  ".join(f"{STAGE_EMOJI.get(s,'')} {s}: {c}" for s, c in counts.items()))

    # Overdue follow-ups
    overdue = db.get_overdue_followups()
    if overdue:
        print(f"\n  ⚠️  OVERDUE FOLLOW-UPS ({len(overdue)}):")
        for j in overdue:
            print(f"     → {j['company']} [{j['id']}] — due {j['followup_date']}")
    print()


def cmd_score():
    _check_api_key()
    print("\n─── Score a New Job ─────────────────────────────────────────────")
    company = input("Company name: ").strip()
    role = input("Role title: ").strip()
    location = input("Location: ").strip()
    print("Paste job description (blank line to finish):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    jd_text = "\n".join(lines)

    print("\n⏳ Scoring with Claude…")
    result = agents.score_job(company, role, location, jd_text)

    score = result.get("match_score", 0)
    rec = result.get("apply_recommendation", "")
    print(f"\n  Match Score : {score}%")
    print(f"  Recommendation: {rec}")
    print(f"  Top Skills  : {', '.join(result.get('top_matching_skills', []))}")
    if result.get("gaps"):
        print(f"  Gaps        : {', '.join(result['gaps'])}")
    print(f"  Hook        : {result.get('suggested_hook', '')}")

    if score >= AUTO_APPLY_THRESHOLD:
        add = input(f"\nScore ≥ {AUTO_APPLY_THRESHOLD}% — add to pipeline? [Y/n]: ").strip().lower()
        if add != "n":
            ref_id = f"RC-{company[:4].upper().replace(' ', '')}-{abs(hash(role)) % 9000 + 1000}-2026"
            recruiter_name = input("Recruiter name (or Enter for 'Hiring Manager'): ").strip() or "Hiring Manager"
            recruiter_email = input("Recruiter email: ").strip()
            job = {
                "id": ref_id,
                "company": company,
                "role": role,
                "location": location,
                "recruiter_name": recruiter_name,
                "recruiter_email": recruiter_email,
                "stage": "Discovered",
                "applied_date": None,
                "followup_date": None,
                "match_score": score,
                "top_matching_skills": result.get("top_matching_skills", []),
                "suggested_hook": result.get("suggested_hook", ""),
            }
            db.upsert(job)
            print(f"  ✓ Added to pipeline as {ref_id}")
            print(f"  Run: python pipeline_cli.py apply {ref_id}")


def cmd_apply(ref_id: str):
    _check_api_key()
    job = db.get(ref_id)
    if not job:
        print(f"ERROR: {ref_id} not found in pipeline.")
        sys.exit(1)

    print(f"\n⏳ Drafting outreach email for {job['company']} — {job['role']}…")
    email = agents.draft_outreach_email(job)

    print(f"\n{'='*60}")
    print(f"TO     : {job['recruiter_email']}")
    print(f"SUBJECT: {email['subject']}")
    print(f"{'─'*60}")
    print(email["body"])
    print(f"{'='*60}")

    action = input("\n[S]end via Gmail / [P]rint only / [E]dit subject / [Q]uit: ").strip().lower()

    if action == "e":
        email["subject"] = input("New subject: ").strip() or email["subject"]
        action = input("[S]end / [P]rint: ").strip().lower()

    if action == "s":
        try:
            from gmail_sender import send_email, is_gmail_configured
            if not is_gmail_configured():
                print("\n⚠️  credentials.json not found — saving email as draft instead.")
                _save_email_draft(job, email)
            else:
                msg_id = send_email(job["recruiter_email"], email["subject"], email["body"])
                print(f"\n  ✓ Sent! Gmail message ID: {msg_id}")
                db.update_stage(ref_id, "Applied")
                from datetime import date, timedelta
                from config import FOLLOWUP_DAYS
                today = date.today()
                data = db.load()
                for j in data:
                    if j["id"] == ref_id:
                        j["applied_date"] = today.isoformat()
                        j["followup_date"] = (today + timedelta(days=FOLLOWUP_DAYS)).isoformat()
                        db.save(data)
                        break
                print(f"  ✓ Stage updated to Applied. Follow-up set for +{FOLLOWUP_DAYS} days.")
        except Exception as e:
            print(f"\n  ✗ Gmail error: {e}")
            print("  Saving draft to file instead.")
            _save_email_draft(job, email)
    elif action == "p":
        pass  # already printed above
    else:
        print("Cancelled.")


def _save_email_draft(job: dict, email: dict):
    draft_path = os.path.join(os.path.dirname(__file__), "drafts")
    os.makedirs(draft_path, exist_ok=True)
    filename = os.path.join(draft_path, f"{job['id']}_outreach.txt")
    with open(filename, "w") as f:
        f.write(f"TO: {job['recruiter_email']}\n")
        f.write(f"SUBJECT: {email['subject']}\n")
        f.write(f"{'─'*60}\n")
        f.write(email["body"])
    print(f"  ✓ Draft saved to {filename}")


def cmd_followup():
    _check_api_key()
    overdue = db.get_overdue_followups()
    if not overdue:
        print("\n  ✓ No overdue follow-ups today.")
        return

    print(f"\n  {len(overdue)} overdue follow-up(s):")
    for job in overdue:
        days = _days_since(job.get("applied_date"))
        print(f"\n  → {job['company']} [{job['id']}] ({days} days since application)")
        print(f"     Role: {job['role']}")
        action = input("     [D]raft follow-up / [S]kip: ").strip().lower()
        if action == "d":
            print("     ⏳ Drafting follow-up…")
            email = agents.draft_followup_email(job, days)
            print(f"\n     SUBJECT: {email['subject']}")
            print(f"     {'─'*50}")
            print(f"     {email['body']}")
            send = input("\n     [S]end / [P]rint only: ").strip().lower()
            if send == "s":
                try:
                    from gmail_sender import send_email, is_gmail_configured
                    if not is_gmail_configured():
                        _save_email_draft(job, email)
                    else:
                        msg_id = send_email(job["recruiter_email"], email["subject"], email["body"], attach_cv=False)
                        print(f"     ✓ Sent! Message ID: {msg_id}")
                        db.mark_followup_sent(job["id"])
                except Exception as e:
                    print(f"     ✗ Error: {e}")
                    _save_email_draft(job, email)
            else:
                _save_email_draft(job, email)


def cmd_prep(ref_id: str):
    _check_api_key()
    job = db.get(ref_id)
    if not job:
        print(f"ERROR: {ref_id} not found.")
        sys.exit(1)

    interview_type = input("Interview type [Panel/HR/Technical/Case]: ").strip() or "Panel"
    round_num_str = input("Round number [1]: ").strip()
    round_num = int(round_num_str) if round_num_str.isdigit() else 1

    print(f"\n⏳ Generating interview brief for {job['company']}…")
    brief = agents.generate_interview_brief(job, interview_type, round_num)

    print(f"\n{'='*70}")
    print(brief)
    print(f"{'='*70}")

    save = input("\nSave to file? [Y/n]: ").strip().lower()
    if save != "n":
        out_dir = os.path.join(os.path.dirname(__file__), "interview_briefs")
        os.makedirs(out_dir, exist_ok=True)
        filename = os.path.join(out_dir, f"{job['id']}_prep.txt")
        with open(filename, "w") as f:
            f.write(f"INTERVIEW PREP: {job['company']} — {job['role']}\n")
            f.write(f"Date: {job.get('interview_date', 'TBC')}\n")
            f.write("="*70 + "\n")
            f.write(brief)
        print(f"  ✓ Saved to {filename}")


def cmd_report():
    _check_api_key()
    pipeline = db.load()
    print("\n⏳ Generating weekly report…")
    report = agents.generate_weekly_report(pipeline)
    print(f"\n{'='*70}")
    print(report)
    print(f"{'='*70}")

    save = input("\nSave report? [Y/n]: ").strip().lower()
    if save != "n":
        out_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(out_dir, exist_ok=True)
        filename = os.path.join(out_dir, f"report_{date.today()}.txt")
        with open(filename, "w") as f:
            f.write(report)
        print(f"  ✓ Saved to {filename}")


def cmd_add():
    print("\n─── Add New Job to Pipeline ─────────────────────────────────────")
    ref_id = input("Reference ID (e.g. RC-FIRM-1234-2026): ").strip()
    company = input("Company: ").strip()
    role = input("Role: ").strip()
    location = input("Location: ").strip()
    recruiter_name = input("Recruiter name [Hiring Manager]: ").strip() or "Hiring Manager"
    recruiter_email = input("Recruiter email: ").strip()
    score_str = input("Match score % [85]: ").strip()
    score = int(score_str) if score_str.isdigit() else 85
    stage = input(f"Stage {STAGES} [Discovered]: ").strip() or "Discovered"
    if stage not in STAGES:
        stage = "Discovered"

    job = {
        "id": ref_id,
        "company": company,
        "role": role,
        "location": location,
        "recruiter_name": recruiter_name,
        "recruiter_email": recruiter_email,
        "stage": stage,
        "applied_date": None,
        "followup_date": None,
        "match_score": score,
    }
    db.upsert(job)
    print(f"  ✓ Added {ref_id} to pipeline.")


def cmd_update(ref_id: str, stage: str):
    if stage not in STAGES:
        print(f"Invalid stage. Choose from: {STAGES}")
        sys.exit(1)
    db.update_stage(ref_id, stage)
    print(f"  ✓ {ref_id} → {stage}")


def cmd_search(source_filter: str = "both"):
    _check_api_key()
    from job_searcher import search_and_score
    from config import AUTO_APPLY_THRESHOLD

    sources = []
    if source_filter in ("both", "naukri"):
        sources.append("naukri")
    if source_filter in ("both", "linkedin"):
        sources.append("linkedin")

    print(f"\n  Searching {', '.join(s.capitalize() for s in sources)} for matching jobs…")
    print("  (Note: sites may block automated requests — results may be partial)\n")

    pipeline = db.load()
    new_jobs = search_and_score(
        existing_pipeline=pipeline,
        score_fn=agents.score_job,
        min_score=70,
        sources=sources,
    )

    if not new_jobs:
        print("\n  No new matching jobs found above 70% score.")
        print("  Possible reasons: bot-blocking, no new listings, or all already in pipeline.")
        return

    new_jobs.sort(key=lambda j: j["match_score"], reverse=True)
    print(f"\n  Found {len(new_jobs)} new job(s) above 70% match:\n")
    print(f"  {'#':<4} {'Score':<7} {'Company':<25} {'Role':<35} {'Source'}")
    print(f"  {'-'*4} {'-'*7} {'-'*25} {'-'*35} {'-'*8}")
    for i, j in enumerate(new_jobs, 1):
        print(
            f"  {i:<4} {j['match_score']:>4}%   {j['company'][:25]:<25} "
            f"{j['role'][:35]:<35} {j['source']}"
        )

    print()
    add_all = input(f"  Add all {len(new_jobs)} jobs to pipeline as 'Discovered'? [Y/n]: ").strip().lower()
    if add_all == "n":
        for i, j in enumerate(new_jobs, 1):
            ans = input(f"  Add #{i} {j['company']} — {j['role']}? [Y/n]: ").strip().lower()
            if ans != "n":
                db.upsert(j)
                print(f"    ✓ Added {j['id']}")
                if j.get("source_url"):
                    print(f"    URL: {j['source_url']}")
    else:
        for j in new_jobs:
            db.upsert(j)
            print(f"  ✓ {j['id']} — {j['company']}: {j['role']}")
            if j.get("source_url"):
                print(f"     URL: {j['source_url']}")

    auto_apply = [j for j in new_jobs if j["match_score"] >= AUTO_APPLY_THRESHOLD]
    if auto_apply:
        print(f"\n  {len(auto_apply)} job(s) score ≥ {AUTO_APPLY_THRESHOLD}% (auto-apply threshold).")
        print("  Run: python pipeline_cli.py apply <ref_id>  to send outreach emails.")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        print(__doc__)
        return

    cmd = args[0]
    if cmd == "status":
        cmd_status()
    elif cmd == "score":
        cmd_score()
    elif cmd == "apply":
        if len(args) < 2:
            print("Usage: python pipeline_cli.py apply <ref_id>")
            sys.exit(1)
        cmd_apply(args[1])
    elif cmd == "followup":
        cmd_followup()
    elif cmd == "prep":
        if len(args) < 2:
            print("Usage: python pipeline_cli.py prep <ref_id>")
            sys.exit(1)
        cmd_prep(args[1])
    elif cmd == "report":
        cmd_report()
    elif cmd == "add":
        cmd_add()
    elif cmd == "update":
        if len(args) < 3:
            print("Usage: python pipeline_cli.py update <ref_id> <stage>")
            sys.exit(1)
        cmd_update(args[1], args[2])
    elif cmd == "search":
        source = args[1].lower() if len(args) > 1 else "both"
        if source not in ("naukri", "linkedin", "both"):
            print("Usage: python pipeline_cli.py search [naukri|linkedin|both]")
            sys.exit(1)
        cmd_search(source)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
