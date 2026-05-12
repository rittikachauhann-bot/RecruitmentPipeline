"""
Apify connector — fetches LinkedIn and Naukri job listings via Apify's
pre-built scraper actors. Works from server environments because Apify
handles proxies, browser fingerprinting, and bot-detection bypass.

Setup:
1. Sign up at https://apify.com (free, $5/mo credit)
2. Get API token from Settings → Integrations → API tokens
3. export APIFY_API_TOKEN=apify_api_...

Cost (free tier covers a month of daily searches):
- LinkedIn actor: ~$0.02 per job
- Naukri actor:   ~$0.01 per job
"""

import logging
import time
from typing import Optional

import requests

from config import (
    APIFY_API_TOKEN,
    APIFY_LINKEDIN_ACTOR,
    APIFY_NAUKRI_ACTOR,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

APIFY_API_BASE = "https://api.apify.com/v2"


def _run_actor(actor_id: str, run_input: dict, timeout_s: int = 300) -> list[dict]:
    """Run an Apify actor synchronously and return its dataset items."""
    if not APIFY_API_TOKEN:
        raise RuntimeError("APIFY_API_TOKEN not set. export APIFY_API_TOKEN=apify_api_...")

    actor_path = actor_id.replace("/", "~")
    url = f"{APIFY_API_BASE}/acts/{actor_path}/run-sync-get-dataset-items"
    params = {"token": APIFY_API_TOKEN}

    log.info("Calling Apify actor %s...", actor_id)
    r = requests.post(url, params=params, json=run_input, timeout=timeout_s)

    if r.status_code != 200:
        log.warning("Apify HTTP %s: %s", r.status_code, r.text[:300])
        return []

    try:
        return r.json()
    except Exception as e:
        log.warning("Apify response parse failed: %s", e)
        return []


def search_linkedin(
    keywords: list[str],
    locations: list[str],
    max_per_query: int = 20,
) -> list[dict]:
    """LinkedIn Jobs via Apify."""
    all_jobs = []
    seen = set()
    for kw in keywords:
        for loc in locations:
            log.info("LinkedIn: '%s' in '%s'", kw, loc)
            run_input = {
                "queries": [{"keyword": kw, "location": loc}],
                "maxItems": max_per_query,
                "experienceLevel": ["director", "executive"],
                "datePosted": "past-week",
            }
            items = _run_actor(APIFY_LINKEDIN_ACTOR, run_input)
            for it in items:
                company = (it.get("companyName") or it.get("company") or "").strip()
                role = (it.get("title") or it.get("jobTitle") or "").strip()
                if not company or not role:
                    continue
                key = (company.lower(), role.lower())
                if key in seen:
                    continue
                seen.add(key)
                all_jobs.append({
                    "source": "linkedin",
                    "company": company,
                    "role": role,
                    "location": it.get("location") or loc,
                    "jd_snippet": (it.get("description") or it.get("descriptionText") or "")[:1500],
                    "url": it.get("url") or it.get("jobUrl") or "",
                })
            time.sleep(1)
    return all_jobs


def search_naukri(
    keywords: list[str],
    locations: list[str],
    max_per_query: int = 20,
) -> list[dict]:
    """Naukri jobs via Apify."""
    all_jobs = []
    seen = set()
    for kw in keywords:
        for loc in locations:
            log.info("Naukri: '%s' in '%s'", kw, loc)
            run_input = {
                "search": [{"keyword": kw, "location": loc, "experience": "12"}],
                "maxItems": max_per_query,
            }
            items = _run_actor(APIFY_NAUKRI_ACTOR, run_input)
            for it in items:
                company = (it.get("companyName") or it.get("company") or "").strip()
                role = (it.get("title") or it.get("jobTitle") or "").strip()
                if not company or not role:
                    continue
                key = (company.lower(), role.lower())
                if key in seen:
                    continue
                seen.add(key)
                all_jobs.append({
                    "source": "naukri",
                    "company": company,
                    "role": role,
                    "location": it.get("location") or loc,
                    "jd_snippet": (it.get("description") or "")[:1500],
                    "url": it.get("url") or it.get("jobUrl") or "",
                })
            time.sleep(1)
    return all_jobs


def search_and_score(
    existing_pipeline: list[dict],
    score_fn,
    min_score: int = 70,
    sources: tuple = ("linkedin", "naukri"),
    keywords: Optional[list[str]] = None,
    locations: Optional[list[str]] = None,
) -> list[dict]:
    """
    Run Apify scrapers, score each result via Claude, return new jobs above
    min_score not already in pipeline. Drop-in replacement for
    job_searcher.search_and_score.
    """
    from job_searcher import _ref_id, DEFAULT_KEYWORDS, DEFAULT_LOCATIONS_NAUKRI

    keywords = keywords or DEFAULT_KEYWORDS
    locations = locations or DEFAULT_LOCATIONS_NAUKRI

    existing_keys = {
        (j["company"].lower(), j["role"].lower()) for j in existing_pipeline
    }

    raw: list[dict] = []
    if "linkedin" in sources:
        raw += search_linkedin(keywords, locations)
    if "naukri" in sources:
        raw += search_naukri(keywords, locations)

    log.info("Total raw jobs from Apify: %d", len(raw))

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
            "source": job["source"],
            "source_url": job.get("url", ""),
        })
        existing_keys.add(key)
        log.info("  Score %d — %s @ %s", match_score, job["role"], job["company"])

    return new_jobs
