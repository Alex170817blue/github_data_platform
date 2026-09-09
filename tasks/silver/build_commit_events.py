import json
from pathlib import Path

import pandas as pd
from prefect import task

from tasks.silver.upsert import upsert_parquet

SILVER_PATH = Path("storage/silver/commits.parquet")


@task
def build_commit_events(bronze_dt: str) -> Path:
    commit_files = Path(
        f"storage/bronze/commits/dt={bronze_dt}"
    ).glob("*.json")

    rows = []

    for file in commit_files:
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

        for commit in data:
            if not isinstance(commit, dict):
                continue

            author = commit.get("author") or {}
            commit_author = commit.get("commit", {}).get("author") or {}

            author_login = author.get("login")
            author_name = commit_author.get("name")

            contributor = author_login or author_name or "unknown"

            rows.append({
                "sha": commit["sha"],
                "repo_full_name": repo_full_name,
                "author_login": contributor,
                "author_name": author_name,
                "committed_at": commit_author.get("date"),
                "message": (
                    commit.get("commit", {})
                    .get("message", "")
                    .split("\n")[0]
                ),
            })

    new_rows = pd.DataFrame(rows)

    if new_rows.empty:
        return SILVER_PATH

    upsert_parquet(
        SILVER_PATH,
        new_rows,
        key_columns=["sha"],
    )

    return SILVER_PATH