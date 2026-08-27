import json
from pathlib import Path

import pandas as pd
from prefect import task

from tasks.silver.upsert import upsert_parquet

SILVER_PATH = Path("storage/silver/lead_times.parquet")


@task
def build_lead_times(bronze_dt: str) -> Path:
    commit_files = Path(f"storage/bronze/pull_request_commits/dt={bronze_dt}").glob("*.json")
    pr_events_path = pd.read_parquet("storage/silver/pull_request_events.parquet")

    if not commit_files or not pr_events_path.exists():
        return SILVER_PATH

    pr_events = pd.read_parquet(pr_events_path)
    merged_prs = pr_events[pr_events["event_type"] == "pr_merged"]

    rows = []
    for file in commit_files:
        payload = json.loads(file.read_text())
        repo_full_name = payload["repo_full_name"]
        pr_number = payload["pr_number"]
        commits = payload["data"]

        if not commits:
            continue

        merged_match = merged_prs[
            (merged_prs["repo_full_name"] == repo_full_name)
            & (merged_prs["pr_number"] == pr_number)
        ]

        if merged_match.empty:
            continue

        merged_at = merged_match.iloc[0]["event_at"]
        first_commit_at = min(c["commit"]["author"]["date"] for c in commits)

        lead_time_hours = (
            pd.Timestamp(merged_at) - pd.Timestamp(first_commit_at)
        ).total_seconds() / 3600

        rows.append({
            "repo_full_name": repo_full_name,
            "pr_number": pr_number,
            "first_commit_at": first_commit_at,
            "merged_at": merged_at,
            "lead_time_hours": round(lead_time_hours, 2),
        })

    new_rows = pd.DataFrame(rows)

    if new_rows.empty:
        return SILVER_PATH

    upsert_parquet(SILVER_PATH, new_rows, key_columns=["repo_full_name", "pr_number"])

    return SILVER_PATH