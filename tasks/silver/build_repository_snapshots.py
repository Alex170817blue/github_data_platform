import json
from pathlib import Path

import pandas as pd
from prefect import task

SILVER_PATH = Path("storage/silver/repository_snapshots.parquet")


@task
def build_repository_snapshots(bronze_dt: str) -> Path:
    repo_files = Path(f"storage/bronze/repositories/dt={bronze_dt}").glob("*.json")

    rows = []
    for file in repo_files:
        repositories = json.loads(file.read_text())

        for repo in repositories:
            rows.append({
                "snapshot_date": bronze_dt,
                "repo_id": repo["id"],
                "full_name": repo["full_name"],
                "primary_language": repo.get("language"),
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "open_issues": repo["open_issues_count"],
                "is_private": repo["private"],
                "pushed_at": repo["pushed_at"],
            })

    new_rows = pd.DataFrame(rows)

    if new_rows.empty:
        return SILVER_PATH

    _append_snapshot(SILVER_PATH, new_rows)

    return SILVER_PATH


def _append_snapshot(path: Path, new_rows: pd.DataFrame) -> None:
    """
    A differenza di upsert_parquet, qui NON deduplichiamo tra date diverse:
    lo storico è il valore. Deduplichiamo solo se la stessa (repo_id, snapshot_date)
    viene scritta due volte nello stesso giorno (es. rilancio manuale).
    """
    if path.exists():
        existing = pd.read_parquet(path)
        combined = pd.concat([existing, new_rows], ignore_index=True)
    else:
        combined = new_rows

    combined = combined.drop_duplicates(
        subset=["repo_id", "snapshot_date"], keep="last"
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(path, index=False)