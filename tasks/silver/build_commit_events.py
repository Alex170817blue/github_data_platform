import json
from pathlib import Path

import pandas as pd
from prefect import task

from tasks.silver.upsert import upsert_parquet

SILVER_PATH = Path("storage/silver/commits.parquet")


@task
def build_commit_events(bronze_dt: str) -> Path:
    commit_files = Path(f"storage/bronze/commits/dt={bronze_dt}").glob("*.json")

    rows = []
    for file in commit_files:
        payload = json.loads(file.read_text())
        repo_full_name = payload["repo_full_name"]

        for commit in payload["data"]:
            rows.append({
                "sha": commit["sha"],
                "repo_full_name": repo_full_name,
                "author_login": (commit.get("author") or {}).get("login"),
                "author_name": commit["commit"]["author"]["name"],
                "committed_at": commit["commit"]["author"]["date"],
                "message": commit["commit"]["message"].split("\n")[0],
            })

    new_rows = pd.DataFrame(rows)

    if new_rows.empty:
        return SILVER_PATH

    upsert_parquet(SILVER_PATH, new_rows, key_columns=["sha"])

    return SILVER_PATH