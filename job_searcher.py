"""
Job search agent — scrapes Naukri.com and LinkedIn public job search pages.

Limitations (honest):
- Both sites use bot-protection; requests may be blocked or return empty results.
- LinkedIn is significantly more aggressive about blocking scrapers.
- This is for personal use only; rate-limited to avoid abuse.
- If blocked, the agent logs a clear warning and returns what it can.
"""

import re
import time
import hashlib
import logging
from typing import Optional
from datetime import date

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Search keywords tuned to Ritika's profile
DEFAULT_KEYWORDS = [
    "Director AI Strategy",
    "Director Digital Transformation",
    "Principal Consultant AI Cloud",
    "Director BFSI Consulting",
    "Head AI Governance",
]

DEFAULT_LOCATIONS_NAUKRI = ["Delhi NCR", "Bengaluru", "Mumbai", "Hyderabad"]
DEFAULT_LOCATIONS_LINKEDIN = ["Delhi, India", "Bengaluru, India", "Mumbai, India"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def _ref_id(company: str, role: str) -> str:
    """Generate a deterministic ref ID from company+role."""
    slug = re.sub(r"[^a-z0-9]", "", (company + role).lower())[:8].upper()
    h = hashlib.md5((company + role).encode()).hexdigest()[:4].upper()
    year = date.today().year
    return f"RC-{slug[:4]}-{h}-{year}"


def _safe_get(url: str, params: Optional[dict] = None, timeout: int = 12) -> Optional[requests.Response]:
    try:
        r = SESSION.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r
        log.warning("HTTP %s for %s", r.status_code, url)
        return None
    except requests.RequestException as e:
        log.warning("Request failed for %s: %s", url, e)
        return None


# ---------------------------------------------------------------------------
# Naukri.com
# ---------------------------------------------------------------------------

def _search_naukri_keyword(keyword: str, location: str) -> list[dict]:
    """
    Uses Naukri's internal JSON API (unofficial, no auth required).
    Returns a list of raw job dicts.
    """
    url = "https://www.naukri.com/jobapi/v3/search"
    params = {
        "noOfResults": 20,
        "urlType": "search_by_keyword",
        "searchType": "adv",
        "keyword": keyword,
        "location": location,
        "experience": 12,
        "pageNo": 1,
    }
    extra_headers = {
        "Appid": "109",
        "SystemId": "109",
        "Accept": "application/json",
    }
    try:
        r = SESSION.get(url, params=params, headers={**HEADERS, **extra_headers}, timeout=12)
        if r.status_code != 200:
            log.warning("Naukri API returned HTTP %s (possibly blocked)", r.status_code)
            return []
        data = r.json()
        jobs_raw = data.get("jobDetails", [])
        results = []
        for j in jobs_raw:
            title = j.get("title", "").strip()
            company = j.get("companyName", "").strip()
            loc = ", ".join(j.get("placeholders", [{}])[0].get("label", location).split(",")[:2])
            jd_snippet = j.get("jobDescription", "")
            job_url = j.get("jdURL", "")
            if title and company:
                results.append({
                    "source": "naukri",
                    "company": company,
                    "role": title,
                    "location": loc or location,
                    "jd_snippet": jd_snippet,
                    "url": f"https://www.naukri.com{job_url}" if job_url.startswith("/") else job_url,
                })
        log.info("Naukri: %d jobs for '%s' in '%s'", len(results), keyword, location)
        return results
    except Exception as e:
        log.warning("Naukri parse error: %s", e)
        return []


def search_naukri(
    keywords: list[str] = DEFAULT_KEYWORDS,
    locations: list[str] = DEFAULT_LOCATIONS_NAUKRI,
) -> list[dict]:
    seen = set()
    jobs = []
    for kw in keywords:
        for loc in locations:
            batch = _search_naukri_keyword(kw, loc)
            for j in batch:
                key = (j["company"].lower(), j["role"].lower())
                if key not in seen:
                    seen.add(key)
                    jobs.append(j)
            time.sleep(1.2)  # polite rate limit
    return jobs


# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------

def _search_linkedin_keyword(keyword: str, location: str) -> list[dict]:
    """
    Scrapes LinkedIn public job search (no login required for listings).
    LinkedIn aggressively blocks bots — results may be empty.
    """
    url = "https://www.linkedin.com/jobs/search/"
    params = {
        "keywords": keyword,
        "location": location,
        "f_TPR": "r604800",  # past week
        "f_E": "4,5",        # Director / Executive seniority
        "start": 0,
    }
    r = _safe_get(url, params=params)
    if r is None:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    cards = soup.select("div.base-card")
    if not cards:
        # LinkedIn may serve a Captcha or empty page
        log.warning(
            "LinkedIn returned 0 job cards for '%s' in '%s' — likely bot-blocked. "
            "Try running with a real browser session or LinkedIn API credentials.",
            keyword, location,
        )
        return []

    results = []
    for card in cards[:15]:
        title_el = card.select_one("h3.base-search-card__title")
        company_el = card.select_one("h4.base-search-card__subtitle")
        loc_el = card.select_one("span.job-search-card__location")
        link_el = card.select_one("a.base-card__full-link")

        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        loc = loc_el.get_text(strip=True) if loc_el else location
        url_ = link_el["href"].split("?")[0] if link_el else ""

        if title and company:
            results.append({
                "source": "linkedin",
                "company": company,
                "role": title,
                "location": loc,
                "jd_snippet": "",
                "url": url_,
            })

    log.info("LinkedIn: %d jobs for '%s' in '%s'", len(results), keyword, location)
    return results


def search_linkedin(
    keywords: list[str] = DEFAULT_KEYWORDS,
    locations: list[str] = DEFAULT_LOCATIONS_LINKEDIN,
) -> list[dict]:
    seen = set()
    jobs = []
    for kw in keywords:
        for loc in locations:
            batch = _search_linkedin_keyword(kw, loc)
            for j in batch:
                key = (j["company"].lower(), j["role"].lower())
                if key not in seen:
                    seen.add(key)
                    jobs.append(j)
            time.sleep(2.0)  # LinkedIn needs a longer pause
    return jobs


# ---------------------------------------------------------------------------
# Orchestrator: search → score → deduplicate against pipeline
# ---------------------------------------------------------------------------

def search_and_score(
    existing_pipeline: list[dict],
    score_fn,  # claude_agents.score_job
    min_score: int = 70,
    sources: list[str] = ("naukri", "linkedin"),
) -> list[dict]:
    """
    Search both platforms, score each job via Claude, return new jobs above
    min_score that are not already in the pipeline.

    Args:
        existing_pipeline: current pipeline list (to avoid duplicates)
        score_fn: claude_agents.score_job(company, role, location, jd_text) -> dict
        min_score: minimum match score to include
        sources: which platforms to search

    Returns:
        List of scored job dicts ready for pipeline.upsert()
    """
    existing_keys = {
        (j["company"].lower(), j["role"].lower()) for j in existing_pipeline
    }

    raw_jobs: list[dict] = []
    if "naukri" in sources:
        log.info("Searching Naukri.com...")
        raw_jobs += search_naukri()
    if "linkedin" in sources:
        log.info("Searching LinkedIn...")
        raw_jobs += search_linkedin()

    log.info("Total unique raw jobs found: %d", len(raw_jobs))

    new_jobs = []
    for job in raw_jobs:
        key = (job["company"].lower(), job["role"].lower())
        if key in existing_keys:
            log.info("Skipping duplicate: %s @ %s", job["role"], job["company"])
            continue

        log.info("Scoring: %s @ %s ...", job["role"], job["company"])
        try:
            score_data = score_fn(
                company=job["company"],
                role=job["role"],
                location=job["location"],
                jd_text=job.get("jd_snippet") or f"{job['role']} at {job['company']}",
            )
        except Exception as e:
            log.warning("Scoring failed for %s @ %s: %s", job["role"], job["company"], e)
            continue

        match_score = score_data.get("match_score", 0)
        if match_score < min_score:
            log.info("  Score %d < %d, skipping.", match_score, min_score)
            continue

        pipeline_entry = {
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
        }
        new_jobs.append(pipeline_entry)
        existing_keys.add(key)  # prevent intra-batch duplicates
        log.info("  Score %d — added to results.", match_score)
        time.sleep(0.5)  # small pause between Claude calls

    return new_jobs
