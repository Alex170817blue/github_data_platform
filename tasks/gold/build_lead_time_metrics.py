from pathlib import Path

import pandas as pd
from prefect import task

from tasks.gold.periods import add_period_columns

SILVER_PATH = Path("storage/silver/lead_times.parquet")
WEEKLY_PATH = Path("storage/gold/lead_time_weekly.parquet")
MONTHLY_PATH = Path("storage/gold/lead_time_monthly.parquet")


@task
def build_lead_time_metrics() -> None:
    if not SILVER_PATH.exists():
        return

    lead_times = pd.read_parquet(SILVER_PATH)
    lead_times = add_period_columns(lead_times, "merged_at")

    weekly = (
        lead_times.groupby(["repo_full_name", "week_start"])["lead_time_hours"]
        .agg(avg_lead_time_hours="mean", merged_prs_count="count")
        .reset_index()
    )
    monthly = (
        lead_times.groupby(["repo_full_name", "month_start"])["lead_time_hours"]
        .agg(avg_lead_time_hours="mean", merged_prs_count="count")
        .reset_index()
    )

    WEEKLY_PATH.parent.mkdir(parents=True, exist_ok=True)
    weekly.to_parquet(WEEKLY_PATH, index=False)
    monthly.to_parquet(MONTHLY_PATH, index=False)