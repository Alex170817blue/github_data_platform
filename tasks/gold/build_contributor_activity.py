from pathlib import Path

import pandas as pd
from prefect import task

from tasks.gold.periods import add_period_columns

SILVER_PATH = Path("storage/silver/commits.parquet")
WEEKLY_PATH = Path("storage/gold/contributor_activity_weekly.parquet")
MONTHLY_PATH = Path("storage/gold/contributor_activity_monthly.parquet")


@task
def build_contributor_activity() -> None:
    if not SILVER_PATH.exists():
        return

    commits = pd.read_parquet(SILVER_PATH)
    commits = add_period_columns(commits, "committed_at")

    # Se il commit non è collegato a un account GitHub (author_login nullo),
    # ricadiamo sul nome del committer preso dal commit stesso.
    commits["contributor"] = commits["author_login"].fillna(commits["author_name"])

    weekly = (
        commits.groupby(["repo_full_name", "contributor", "week_start"])
        .size()
        .reset_index(name="commits_count")
    )
    monthly = (
        commits.groupby(["repo_full_name", "contributor", "month_start"])
        .size()
        .reset_index(name="commits_count")
    )

    WEEKLY_PATH.parent.mkdir(parents=True, exist_ok=True)
    weekly.to_parquet(WEEKLY_PATH, index=False)
    monthly.to_parquet(MONTHLY_PATH, index=False)