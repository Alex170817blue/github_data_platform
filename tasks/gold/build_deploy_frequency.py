from pathlib import Path

import pandas as pd
from prefect import task

from tasks.gold.periods import add_period_columns

SILVER_PATH = Path("storage/silver/deploy_events.parquet")
WEEKLY_PATH = Path("storage/gold/deploy_frequency_weekly.parquet")
MONTHLY_PATH = Path("storage/gold/deploy_frequency_monthly.parquet")


@task
def build_deploy_frequency() -> None:
    if not SILVER_PATH.exists():
        return

    events = pd.read_parquet(SILVER_PATH)
    events = add_period_columns(events, "event_at")

    weekly = (
        events.groupby(["repo_full_name", "week_start"])
        .size()
        .reset_index(name="deploys_count")
    )
    monthly = (
        events.groupby(["repo_full_name", "month_start"])
        .size()
        .reset_index(name="deploys_count")
    )

    WEEKLY_PATH.parent.mkdir(parents=True, exist_ok=True)
    weekly.to_parquet(WEEKLY_PATH, index=False)
    monthly.to_parquet(MONTHLY_PATH, index=False)