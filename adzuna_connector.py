"""
Adzuna job search connector — free API, no credit card required.

Setup (1 minute):
1. Sign up at https://developer.adzuna.com/signup
2. Copy App ID and App Key from dashboard
3. export ADZUNA_APP_ID=your_app_id
   export ADZUNA_APP_KEY=your_app_key

Free tier: unlimited calls, covers India (endpoint: /jobs/in/)
"""

import logging
import time
from typing import Optional

import requests

from config import ADZUNA_APP_ID, ADZUNA_APP_KEY

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs/in/search"

DEFAULT_KEYWORDS = [
    "Director AI Strategy",
    "Director Digital Transformation",
    "Principal Consultant AI",
    "Director BFSI Consulting",
    "Head AI Governance",
]

DEFAULT_LOCATIONS = ["Delhi", "Bengaluru", "Mumbai", "Hyderabad"]


def _search(keyword: str, location: str, page: int = 1, results: int = 20) -> list[dict]:
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise RuntimeError(
            "ADZUNA_APP_ID / ADZUNA_APP_KEY not set.\n"
            "Sign up free at https://developer.adzuna.com/signup"
        )

    url = f"{ADZUNA_BASE}/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results,
        "what": keyword,
        "where": location,
        "sort_by": "date",
        "content-type": "application/json",
    }

    try:
        r = requests.get(url, params=params, timeout=12)
        if r.status_code != 200:
            log.warning("Adzuna HTTP %s for '%s' in '%s'", r.status_code, keyword, location)
            return []
        data = r.json()
        jobs = []
        for item in data.get("results", []):
            title = item.get("title", "").strip()
            company = (item.get("company") or {}).get("display_name", "").strip()
            loc = (item.get("location") or {}).get("display_name", location)
            desc = item.get("description", "")
            url_ = item.get("redirect_url", "")
            if title and company:
                jobs.append({
                    "source": "adzuna",
                    "company": company,
                    "role": title,
                    "location": loc,
                    "jd_snippet": desc[:1500],
                    "url": url_,
                })
        log.info("Adzuna: %d jobs for '%s' in '%s'", len(jobs), keyword, location)
        return jobs
    except Exception as e:
        log.warning("Adzuna error for '%s' in '%s': %s", keyword, location, e)
        return []


def search_jobs(
    keywords: list[str] = DEFAULT_KEYWORDS,
    locations: list[str] = DEFAULT_LOCATIONS,
) -> list[dict]:
    seen = set()
    all_jobs = []
    for kw in keywords:
        for loc in locations:
            for job in _search(kw, loc):
                key = (job["company"].lower(), job["role"].lower())
                if key not in seen:
                    seen.add(key)
                    all_jobs.append(job)
            time.sleep(0.5)
    return all_jobs


def search_and_score(
    existing_pipeline: list[dict],
    score_fn,
    min_score: int = 70,
    sources: tuple = ("adzuna",),
    keywords: Optional[list[str]] = None,
    locations: Optional[list[str]] = None,
) -> list[dict]:
    """
    Search Adzuna, score via Claude, return new jobs above min_score.
    Drop-in replacement for job_searcher.search_and_score.
    """
    from job_searcher import _ref_id

    keywords = keywords or DEFAULT_KEYWORDS
    locations = locations or DEFAULT_LOCATIONS

    existing_keys = {
        (j["company"].lower(), j["role"].lower()) for j in existing_pipeline
    }

    raw = search_jobs(keywords, locations)
    log.info("Total unique jobs from Adzuna: %d", len(raw))

    new_jobs = []
    for job in raw:
        key = (job["company"].lower(), job["role"].lower())
        if key in existing_keys:
            continue

        try:
            score_data = score_fn(
                company=job["company"],
                role=job["role"],
                location=job["location"],
                jd_text=job.get("jd_snippet") or f"{job['role']} at {job['company']}",
            )
        except Exception as e:
            log.warning("Scoring failed: %s", e)
            continue

        match_score = score_data.get("match_score", 0)
        if match_score < min_score:
            continue

        new_jobs.append({
            "id": _ref_id(job["company"], job["role"]),
            "company": job["company"],
            "role": job["role"],
            "location": job["location"],
            "recruiter_name": "Hiring Manager",
            "recruiter_email": "",
            "stage": "Discovered",
            "applied_date": None,
            "followup_date": None,
            "match_score": match_score,
            "top_matching_skills": score_data.get("top_matching_skills", []),
            "gaps": score_data.get("gaps", []),
            "apply_recommendation": score_data.get("apply_recommendation", ""),
            "suggested_hook": score_data.get("suggested_hook", ""),
            "source": "adzuna",
            "source_url": job.get("url", ""),
        })
        existing_keys.add(key)
        log.info("  Score %d — %s @ %s", match_score, job["role"], job["company"])

    return new_jobs
