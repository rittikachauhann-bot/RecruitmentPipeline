"""Pipeline persistence — read/write pipeline.json."""

import json
import os
from datetime import date, datetime
from typing import Optional
from config import PIPELINE_DB, INITIAL_PIPELINE


def _today() -> str:
    return date.today().isoformat()


def load() -> list[dict]:
    if not os.path.exists(PIPELINE_DB):
        data = INITIAL_PIPELINE
        save(data)
        return data
    with open(PIPELINE_DB) as f:
        return json.load(f)


def save(data: list[dict]) -> None:
    with open(PIPELINE_DB, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get(ref_id: str) -> Optional[dict]:
    for job in load():
        if job["id"] == ref_id:
            return job
    return None


def upsert(job: dict) -> None:
    data = load()
    for i, existing in enumerate(data):
        if existing["id"] == job["id"]:
            data[i] = job
            save(data)
            return
    data.append(job)
    save(data)


def update_stage(ref_id: str, stage: str) -> None:
    data = load()
    for job in data:
        if job["id"] == ref_id:
            job["stage"] = stage
            if stage == "Applied" and not job.get("applied_date"):
                job["applied_date"] = _today()
            save(data)
            return
    print(f"[pipeline_db] ref_id {ref_id} not found")


def get_overdue_followups() -> list[dict]:
    today = _today()
    return [
        j for j in load()
        if j.get("followup_date") and j["followup_date"] <= today
        and j["stage"] not in ("Offer", "Rejected")
        and not j.get("followup_sent")
    ]


def mark_followup_sent(ref_id: str) -> None:
    data = load()
    for job in data:
        if job["id"] == ref_id:
            job["followup_sent"] = True
            save(data)
            return
