import json
from pathlib import Path

import pandas as pd
from prefect import task

from tasks.silver.upsert import upsert_parquet

SILVER_PATH = Path("storage/silver/deploy_events.parquet")


@task
def build_deploy_events(bronze_dt: str) -> Path:
    run_files = Path(f"storage/bronze/workflow_runs/dt={bronze_dt}").glob("*.json")

    rows = []
    for file in run_files:
        payload = json.loads(file.read_text())
        repo_full_name = payload["repo_full_name"]

        for run in payload["data"]:
            if run["status"] != "completed" or run["conclusion"] != "success":
                continue

            rows.append({
                "repo_full_name": repo_full_name,
                "run_id": run["id"],
                "workflow_name": run["name"],
                "event_at": run["updated_at"],
                "branch": run["head_branch"],
            })

    new_rows = pd.DataFrame(rows)

    if new_rows.empty:
        return SILVER_PATH

    upsert_parquet(SILVER_PATH, new_rows, key_columns=["run_id"])

    return SILVER_PATH