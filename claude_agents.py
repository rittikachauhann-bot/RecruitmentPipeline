"""All Claude-powered agent functions."""

import json
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CANDIDATE

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

PROFILE_SUMMARY = """
- Current title: Consultant – Digital Transformation & Cloud Strategy at Coforge
- Experience: 14+ years in AI Strategy, BFSI & GovTech
- Key skills: AI strategy, Azure AKS, Responsible AI (EU AI Act, ISO 42001),
  SAFe 6.0, BFSI consulting, GovTech, CXO advisory, AI CoE design
- Certifications: SAFe 6.0 Agilist, CSPO, Azure AI-900, AZ-900, PL-900
- Notable: Led UIDAI (Aadhaar) cloud modernisation serving 1 billion+ citizens
- Key metrics: 40% cost reduction, 99.99% uptime SLA, 35% efficiency gain,
  30% velocity uplift, 25% faster delivery
- Target: Director / Principal Consultant roles
- Locations: Delhi NCR, Bengaluru, Mumbai, Hyderabad, UK, US Remote, Global
""".strip()


def score_job(company: str, role: str, location: str, jd_text: str) -> dict:
    """Agent 1+2: Score a job description against Ritika's profile."""
    prompt = f"""You are an expert recruitment analyst helping Ritika Chouhan find the best matching roles.

Her profile:
{PROFILE_SUMMARY}

Score this role on 0–100 using these weighted criteria:
- AI strategy experience (20%)
- Azure cloud skills (15%)
- BFSI sector depth (15%)
- GovTech experience (10%)
- Agile/SAFe leadership (10%)
- CXO advisory (10%)
- Team leadership (10%)
- Governance & compliance (10%)

COMPANY: {company}
ROLE: {role}
LOCATION: {location}
JOB DESCRIPTION:
{jd_text}

Return ONLY valid JSON (no markdown, no extra text):
{{
  "match_score": <number 0-100>,
  "top_matching_skills": ["skill1", "skill2", "skill3"],
  "gaps": ["gap1"],
  "apply_recommendation": "Yes | Yes with tailoring | Skip",
  "suggested_hook": "<one sentence to open the cover email>"
}}"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise


def draft_outreach_email(job: dict) -> dict:
    """Agent 3: Draft personalised recruiter email. Returns {subject, body}."""
    matching_skills = ", ".join(job.get("top_matching_skills", ["AI Strategy", "Azure", "BFSI"]))
    prompt = f"""You are {CANDIDATE['name']}'s personal career assistant. Write a professional recruiter outreach email.

CANDIDATE:
- Name: {CANDIDATE['name']}
- Email: {CANDIDATE['email']}
- Phone: {CANDIDATE['phone']}
- LinkedIn: {CANDIDATE['linkedin']}
- Experience: 14+ years in Digital Transformation & AI Strategy
- Top achievement: Led UIDAI (Aadhaar) cloud-native modernisation on Azure serving 1 billion+ Indian citizens
- Key metrics: 40% cost reduction, 99.99% uptime SLA, 35% efficiency gain, 30% velocity uplift
- Certifications: SAFe 6.0 Agilist, CSPO, Azure AI-900, AZ-900, PL-900
- Notice period: 60 days. Open to relocation.

JOB:
- Company: {job['company']}
- Role: {job['role']}
- Recruiter name: {job.get('recruiter_name', 'Hiring Manager')}
- Reference ID: {job['id']}
- Top matching skills: {matching_skills}
- Suggested hook: {job.get('suggested_hook', '')}

INSTRUCTIONS:
- Maximum 300 words
- Professional but warm tone
- Open with the most relevant achievement for THIS role
- Include 3–4 bullet point highlights matching the role
- End with notice period, relocation availability, and reference ID
- Subject line: [Ref: {job['id']}] {job['role']} | 14 yrs BFSI + GovTech | Ritika Chouhan
- Do NOT use generic phrases like "I am excited to apply"
- CV is attached as Ritika_Chouhan_CV_Global_1.docx

Return ONLY valid JSON (no markdown):
{{"subject": "<subject line>", "body": "<full email body>"}}"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"subject": f"[Ref: {job['id']}] {job['role']} | Ritika Chouhan", "body": raw}


def draft_followup_email(job: dict, days_since: int) -> dict:
    """Agent 5: Draft follow-up email after no response."""
    prompt = f"""Write a polite, professional follow-up email for Ritika Chouhan.

CONTEXT:
- Applied to: {job['role']} at {job['company']}
- Application date: {job.get('applied_date', 'recently')}
- Reference ID: {job['id']}
- Recruiter email: {job.get('recruiter_email', '')}
- Recruiter name: {job.get('recruiter_name', 'Hiring Manager')}
- Days since application: {days_since}

Write a brief (100 words max) follow-up email that:
- References the original application and Ref ID
- Reaffirms interest without being desperate
- Adds one new compelling data point not in the original email
- Asks for a brief 15-minute call
- Is warm, confident, and professional

Return ONLY valid JSON (no markdown):
{{
  "subject": "Re: [Ref: {job['id']}] {job['role']} | Following up – Ritika Chouhan",
  "body": "<email body>"
}}"""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {
            "subject": f"Re: [Ref: {job['id']}] {job['role']} | Following up – Ritika Chouhan",
            "body": raw,
        }


def generate_interview_brief(job: dict, interview_type: str = "Panel", round_num: int = 1) -> str:
    """Agent 4: Generate full interview preparation brief."""
    prompt = f"""Generate a comprehensive interview preparation brief for Ritika Chouhan.

INTERVIEW DETAILS:
- Company: {job['company']}
- Role: {job['role']}
- Interview type: {interview_type}
- Date/Time: {job.get('interview_date', 'TBC')}
- Round number: {round_num}

RITIKA'S BACKGROUND:
14+ years in Digital Transformation & AI Strategy. Current: Coforge (AI & Cloud Modernisation).
Prior: HCL Infosystems (led UIDAI Aadhaar, 1B+ users), GAIA Smart Cities (IoT).
Key skills: Azure AKS, SAFe 6.0, Responsible AI, BFSI & GovTech consulting. MBA IIITM Gwalior.

Generate these sections:
1. COMPANY SNAPSHOT (5 bullets – recent news, strategy, AI focus)
2. ROLE ANALYSIS (what they're really looking for)
3. TOP 5 LIKELY QUESTIONS + RECOMMENDED ANSWERS (STAR format)
4. 3 TECHNICAL QUESTIONS to expect
5. RITIKA'S STRONGEST TALKING POINTS for this company
6. 5 SMART QUESTIONS Ritika should ask the interviewer
7. SALARY ANCHOR: Recommended opening position if compensation discussed
8. ONE-LINER SUMMARY for "tell me about yourself"

Format clearly with section headers."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_weekly_report(pipeline: list[dict]) -> str:
    """Agent 8: Weekly pipeline status report."""
    stage_counts = {}
    for j in pipeline:
        stage_counts[j["stage"]] = stage_counts.get(j["stage"], 0) + 1

    pipeline_summary = json.dumps(
        [{"company": j["company"], "role": j["role"], "stage": j["stage"],
          "applied": j.get("applied_date"), "followup": j.get("followup_date"),
          "score": j.get("match_score")} for j in pipeline],
        indent=2
    )

    prompt = f"""Generate a weekly recruitment pipeline status report for Ritika Chouhan.

PIPELINE DATA:
{pipeline_summary}

STAGE COUNTS: {json.dumps(stage_counts)}

Generate a structured report with:
1. EXECUTIVE SUMMARY (3 sentences)
2. PIPELINE HEALTH SCORE (0–100)
3. STAGE BREAKDOWN with counts
4. URGENT ACTIONS for next 48 hours
5. RECOMMENDED ACTIONS this week (ranked by priority)
6. ONE INSIGHT from the data

Format cleanly with headers. Use tables where appropriate."""

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
