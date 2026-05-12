"""Central configuration for Ritika Chouhan's recruitment pipeline."""

import os

# --- Candidate ---
CANDIDATE = {
    "name": "Ritika Chouhan",
    "email": "riti.iiit@gmail.com",
    "phone": "+91-7042656887",
    "linkedin": "https://linkedin.com/in/ritikachouhan",
    "portfolio_url": "https://rittikachauhann-bot.github.io/RecruitmentPipeline/portfolio.html",  # Web-based CV/portfolio link
    "notice_period": "60 days",
    "cv_path": os.path.expanduser("~/Downloads/Ritika_Chouhan_CV_Global_1.docx"),
}

# --- Anthropic ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-6"

# --- Gmail OAuth ---
GMAIL_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
GMAIL_TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# --- Adzuna (free job search API) ---
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")

# --- Pipeline DB ---
PIPELINE_DB = os.path.join(os.path.dirname(__file__), "pipeline.json")

# --- Scoring thresholds ---
AUTO_APPLY_THRESHOLD = 85   # score >= this → auto-draft outreach email
SKIP_THRESHOLD = 60         # score < this → skip

# --- Follow-up days ---
FOLLOWUP_DAYS = 5

# --- Pre-loaded pipeline (from claude.md) ---
INITIAL_PIPELINE = [
    {
        "id": "RC-DELO-2847-2026",
        "company": "Deloitte India",
        "role": "Director – AI Strategy & Digital Transformation",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "talent-india@deloitte.com",
        "stage": "Screening",
        "applied_date": "2026-05-01",
        "followup_date": "2026-05-06",
        "match_score": 97,
        "location": "Delhi NCR / Bengaluru",
    },
    {
        "id": "RC-EYGS-3192-2026",
        "company": "EY GDS",
        "role": "Principal Consultant – AI & Cloud",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "gds.careers@ey.com",
        "stage": "Applied",
        "applied_date": "2026-05-01",
        "followup_date": "2026-05-06",
        "match_score": 94,
        "location": "Bengaluru",
    },
    {
        "id": "RC-KPMG-4815-2026",
        "company": "KPMG India",
        "role": "Director – Digital Transformation (BFSI)",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "careers.india@kpmg.com",
        "stage": "Applied",
        "applied_date": "2026-05-01",
        "followup_date": "2026-05-06",
        "match_score": 93,
        "location": "Mumbai",
    },
    {
        "id": "RC-ACCE-7263-2026",
        "company": "Accenture India",
        "role": "Director – Enterprise Cloud & AI",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "careers@accenture.com",
        "stage": "Interview",
        "applied_date": "2026-04-30",
        "followup_date": "2026-05-07",
        "match_score": 90,
        "location": "Delhi NCR",
        "interview_date": "2026-05-07 11:00",
    },
    {
        "id": "RC-PWCI-9034-2026",
        "company": "PwC India",
        "role": "Director – GovTech Consulting",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "careers@pwc.in",
        "stage": "Applied",
        "applied_date": "2026-05-01",
        "followup_date": "2026-05-06",
        "match_score": 89,
        "location": "Delhi NCR",
    },
    {
        "id": "RC-HSBC-5571-2026",
        "company": "HSBC GCC India",
        "role": "Head of AI Governance",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "careers@hsbc.in",
        "stage": "Screening",
        "applied_date": "2026-04-29",
        "followup_date": "2026-05-04",
        "match_score": 91,
        "location": "Bengaluru / Mumbai",
    },
    {
        "id": "RC-CAPG-6128-2026",
        "company": "Capgemini India",
        "role": "Director – Cloud Modernisation & AI",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "india.careers@capgemini.com",
        "stage": "Discovered",
        "applied_date": None,
        "followup_date": "2026-05-02",
        "match_score": 87,
        "location": "Delhi NCR / Mumbai",
    },
    {
        "id": "RC-BCGI-3847-2026",
        "company": "BCG India",
        "role": "Senior Director – Digital Strategy",
        "recruiter_name": "Hiring Manager",
        "recruiter_email": "careers@bcg.com",
        "stage": "Discovered",
        "applied_date": None,
        "followup_date": "2026-05-02",
        "match_score": 85,
        "location": "Mumbai / Delhi NCR",
    },
]
