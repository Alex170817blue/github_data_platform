import json
from pathlib import Path

import pandas as pd
from prefect import task

from tasks.silver.upsert import upsert_parquet

SILVER_PATH = Path("storage/silver/pull_request_events.parquet")


@task
def build_pull_request_events(bronze_dt: str) -> Path:
    pr_files = Path(
        f"storage/bronze/pull_requests/dt={bronze_dt}"
    ).glob("*.json")

    rows = []

    for file in pr_files:
        payload = json.loads(file.read_text())

        if isinstance(payload, list):
            data = payload

            # Vecchio formato Bronze:
            # il repository è nel nome del file.
            repo_full_name = file.stem.replace("_", "/", 1)

        elif isinstance(payload, dict):
            data = payload.get("data", [])
            repo_full_name = payload.get("repo_full_name")

        else:
            continue

        for pr in data:
            if not isinstance(pr, dict):
                continue

            rows.extend(
                _derive_events(repo_full_name, pr)
            )

    new_rows = pd.DataFrame(rows)

    if new_rows.empty:
        return SILVER_PATH

    upsert_parquet(
        SILVER_PATH,
        new_rows,
        key_columns=[
            "repo_full_name",
            "pr_number",
            "event_type",
        ],
    )

    return SILVER_PATH


def _derive_events(
    repo_full_name: str,
    pr: dict,
) -> list[dict]:

    events = []

    base = {
        "repo_full_name": repo_full_name,
        "pr_number": pr["number"],
        "author_login": (pr.get("user") or {}).get("login"),
        "title": pr["title"],
    }

    events.append({
        **base,
        "event_type": "pr_opened",
        "event_at": pr["created_at"],
    })

    if pr.get("merged_at"):
        events.append({
            **base,
            "event_type": "pr_merged",
            "event_at": pr["merged_at"],
        })

    elif pr.get("closed_at"):
        events.append({
            **base,
            "event_type": "pr_closed",
            "event_at": pr["closed_at"],
        })

    return events