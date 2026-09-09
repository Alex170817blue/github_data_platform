from datetime import date
from pathlib import Path

import json
import pandas as pd
from fastapi import APIRouter, Query

router = APIRouter(prefix="/metrics", tags=["metrics"])

STORAGE_DIR = Path("storage")
BRONZE_DIR = STORAGE_DIR / "bronze"
SILVER_DIR = STORAGE_DIR / "silver"
GOLD_DIR = STORAGE_DIR / "gold"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_parquet(path: Path) -> pd.DataFrame:
    """Read a parquet file or return an empty DataFrame if it doesn't exist."""
    if not path.exists():
        return pd.DataFrame()

    return pd.read_parquet(path)


def read_bronze_pull_requests() -> list[dict]:
    """Read all Bronze pull-request JSON files."""
    rows = []

    prs_dir = BRONZE_DIR / "pull_requests"

    if not prs_dir.exists():
        return rows

    for path in prs_dir.glob("**/*.json"):
        try:
            payload = json.loads(path.read_text())

            # Historical files may contain a list directly.
            if isinstance(payload, list):
                data = payload

            elif isinstance(payload, dict):
                data = payload.get("data", [])

            else:
                continue

            if not isinstance(data, list):
                continue

            for pr in data:
                if isinstance(pr, dict):
                    rows.append(pr)

        except (json.JSONDecodeError, OSError):
            continue

    return rows


def empty_response(message: str) -> dict:
    return {
        "data": [],
        "count": 0,
        "message": message,
    }


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

@router.get("/summary")
def get_summary_metrics():
    """
    High-level engineering metrics calculated from real pipeline data.
    """

    commits = read_parquet(SILVER_DIR / "commits.parquet")
    prs = read_bronze_pull_requests()

    total_commits = len(commits)

    if not commits.empty and "author_login" in commits.columns:
        active_contributors = int(
            commits["author_login"]
            .dropna()
            .replace("", pd.NA)
            .nunique()
        )
    else:
        active_contributors = 0

    open_prs = sum(
        1
        for pr in prs
        if str(pr.get("state", "")).lower() == "open"
    )

    # Average commits per week from Gold weekly data.
    weekly = read_parquet(
        GOLD_DIR / "contributor_activity_weekly.parquet"
    )

    if (
        not weekly.empty
        and "week_start" in weekly.columns
        and "commits_count" in weekly.columns
    ):
        weekly_totals = (
            weekly.groupby("week_start")["commits_count"]
            .sum()
        )

        avg_commits_per_week = (
            round(float(weekly_totals.mean()), 1)
            if not weekly_totals.empty
            else 0
        )
    else:
        avg_commits_per_week = 0

    return {
        "total_commits": total_commits,
        "active_contributors": active_contributors,
        "open_prs": open_prs,
        "avg_commits_per_week": avg_commits_per_week,
    }

# ---------------------------------------------------------------------------
# Contributor activity
# ---------------------------------------------------------------------------

@router.get("/contributor-activity")
def get_contributor_activity(
    granularity: str = Query(
        default="weekly",
        pattern="^(weekly|monthly)$",
    )
):
    """
    Contributor activity from Gold layer.

    Returns one row per repository/contributor/period.
    """

    filename = (
        "contributor_activity_weekly.parquet"
        if granularity == "weekly"
        else "contributor_activity_monthly.parquet"
    )

    df = read_parquet(GOLD_DIR / filename)

    if df.empty:
        return []

    expected_columns = {
        "repo_full_name",
        "contributor",
        "commits_count",
    }

    if not expected_columns.issubset(df.columns):
        return []

    period_column = (
        "week_start"
        if granularity == "weekly"
        else "month_start"
    )

    if period_column not in df.columns:
        return []

    result = df[
        [
            "repo_full_name",
            "contributor",
            period_column,
            "commits_count",
        ]
    ].copy()

    result = result.rename(
        columns={
            period_column: "period_start",
        }
    )

    result["period_start"] = result["period_start"].astype(str)

    result = result.sort_values(
        ["period_start", "repo_full_name", "contributor"]
    )

    return result.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Activity trend
# ---------------------------------------------------------------------------

@router.get("/activity-trend")
def get_activity_trend(
    granularity: str = Query(
        default="weekly",
        pattern="^(weekly|monthly)$",
    )
):
    """
    Total commit activity aggregated by time period.

    Aggregation is performed from the Gold contributor-activity dataset,
    so the frontend receives presentation-ready data.
    """

    filename = (
        "contributor_activity_weekly.parquet"
        if granularity == "weekly"
        else "contributor_activity_monthly.parquet"
    )

    df = read_parquet(GOLD_DIR / filename)

    if df.empty:
        return []

    period_column = (
        "week_start"
        if granularity == "weekly"
        else "month_start"
    )

    required_columns = {
        period_column,
        "commits_count",
    }

    if not required_columns.issubset(df.columns):
        return []

    result = (
        df.groupby(period_column, as_index=False)["commits_count"]
        .sum()
        .sort_values(period_column)
    )

    result = result.rename(
        columns={
            period_column: "period_start",
        }
    )

    result["period_start"] = result["period_start"].astype(str)
    result["commits_count"] = result["commits_count"].astype(int)

    return result.to_dict(orient="records")

# ---------------------------------------------------------------------------
# Contributors
# ---------------------------------------------------------------------------

@router.get("/contributors")
def get_contributors():
    """
    Contributor statistics calculated from Silver commits.
    """

    commits = read_parquet(SILVER_DIR / "commits.parquet")

    if commits.empty:
        return []

    required = {"author_login"}

    if not required.issubset(commits.columns):
        return []

    df = commits.copy()

    df["author_login"] = (
        df["author_login"]
        .fillna("unknown")
        .replace("", "unknown")
    )

    contributor_stats = (
        df.groupby("author_login")
        .size()
        .reset_index(name="commits")
    )

    contributor_stats["prs"] = 0

    contributor_stats = contributor_stats.sort_values(
        "commits",
        ascending=False,
    )

    return [
        {
            "login": row["author_login"],
            "name": row["author_login"],
            "commits": int(row["commits"]),
            "prs": int(row["prs"]),
        }
        for _, row in contributor_stats.iterrows()
    ]


# ---------------------------------------------------------------------------
# Pull requests
# ---------------------------------------------------------------------------

@router.get("/pull-requests")
def get_pull_requests():
    """
    Pull-request counts from real Bronze data.
    """

    prs = read_bronze_pull_requests()

    counts = {
        "open": 0,
        "closed": 0,
        "merged": 0,
    }

    for pr in prs:
        state = str(pr.get("state", "")).lower()

        # GitHub represents merged PRs as closed + merged_at != null.
        if pr.get("merged_at"):
            counts["merged"] += 1
        elif state == "open":
            counts["open"] += 1
        elif state == "closed":
            counts["closed"] += 1

    return [
        {"status": "open", "count": counts["open"]},
        {"status": "closed", "count": counts["closed"]},
        {"status": "merged", "count": counts["merged"]},
    ]


# ---------------------------------------------------------------------------
# Deploy frequency
# ---------------------------------------------------------------------------

@router.get("/deploy-frequency")
def get_deploy_frequency(
    granularity: str = Query(
        default="weekly",
        pattern="^(daily|weekly|monthly)$",
    )
):
    """
    Successful deployments calculated from Silver deploy_events.

    At the moment the pipeline may legitimately have no successful
    deployments. In that case the endpoint returns an empty list.
    """

    deploys = read_parquet(SILVER_DIR / "deploy_events.parquet")

    if deploys.empty:
        return []

    required = {
        "repo_full_name",
        "event_at",
    }

    if not required.issubset(deploys.columns):
        return []

    df = deploys.copy()

    df["event_at"] = pd.to_datetime(
        df["event_at"],
        errors="coerce",
    )

    df = df.dropna(subset=["event_at"])

    if df.empty:
        return []

    if granularity == "daily":
        df["period_start"] = df["event_at"].dt.date

    elif granularity == "weekly":
        df["period_start"] = (
            df["event_at"]
            .dt.to_period("W-MON")
            .dt.start_time
            .dt.date
        )

    else:
        df["period_start"] = (
            df["event_at"]
            .dt.to_period("M")
            .dt.start_time
            .dt.date
        )

    result = (
        df.groupby(
            ["repo_full_name", "period_start"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "deploys_count"})
    )

    result["period_start"] = result["period_start"].astype(str)

    return result.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Lead time
# ---------------------------------------------------------------------------

@router.get("/lead-time")
def get_lead_time(
    granularity: str = Query(
        default="weekly",
        pattern="^(daily|weekly|monthly)$",
    )
):
    """
    Lead-time metrics.

    Requires a Silver lead_times dataset generated from PR data.
    """

    lead_times = read_parquet(SILVER_DIR / "lead_times.parquet")

    if lead_times.empty:
        return []

    required = {
        "repo_full_name",
        "merged_at",
    }

    if not required.issubset(lead_times.columns):
        return []

    df = lead_times.copy()

    df["merged_at"] = pd.to_datetime(
        df["merged_at"],
        errors="coerce",
    )

    if "lead_time_hours" not in df.columns:
        return []

    df["lead_time_hours"] = pd.to_numeric(
        df["lead_time_hours"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["merged_at", "lead_time_hours"]
    )

    if df.empty:
        return []

    if granularity == "daily":
        df["period_start"] = df["merged_at"].dt.date

    elif granularity == "weekly":
        df["period_start"] = (
            df["merged_at"]
            .dt.to_period("W-MON")
            .dt.start_time
            .dt.date
        )

    else:
        df["period_start"] = (
            df["merged_at"]
            .dt.to_period("M")
            .dt.start_time
            .dt.date
        )

    result = (
        df.groupby(
            ["repo_full_name", "period_start"],
            as_index=False,
        )
        .agg(
            avg_lead_time_hours=(
                "lead_time_hours",
                "mean",
            ),
            merged_prs_count=(
                "lead_time_hours",
                "count",
            ),
        )
    )

    result["avg_lead_time_hours"] = result[
        "avg_lead_time_hours"
    ].round(2)

    result["period_start"] = result[
        "period_start"
    ].astype(str)

    return result.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------

@router.get("/repositories")
def get_repository_metrics():
    snapshots = read_parquet(
        SILVER_DIR / "repository_snapshots.parquet"
    )
    commits = read_parquet(
        SILVER_DIR / "commits.parquet"
    )

    if snapshots.empty:
        return {
            "total_repositories": 0,
            "repositories": [],
        }

    if "full_name" not in snapshots.columns:
        return {
            "total_repositories": 0,
            "repositories": [],
        }

    # Keep only the latest snapshot for each repository.
    latest = snapshots.copy()

    if "snapshot_date" in latest.columns:
        latest["snapshot_date"] = pd.to_datetime(
            latest["snapshot_date"],
            errors="coerce",
        )

        latest = (
            latest
            .sort_values("snapshot_date")
            .groupby("full_name", as_index=False)
            .tail(1)
        )

    # Count real commits from Silver.
    if (
        not commits.empty
        and "repo_full_name" in commits.columns
    ):
        commit_counts = (
            commits
            .groupby("repo_full_name")
            .size()
            .reset_index(name="commits")
        )
    else:
        commit_counts = pd.DataFrame(
            columns=["repo_full_name", "commits"]
        )

    result = latest.merge(
        commit_counts,
        left_on="full_name",
        right_on="repo_full_name",
        how="left",
    )

    # Numeric metrics.
    result["commits"] = (
        pd.to_numeric(result["commits"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    for column in [
        "stars",
        "forks",
        "open_issues",
    ]:
        if column in result.columns:
            result[column] = (
                pd.to_numeric(
                    result[column],
                    errors="coerce",
                )
                .fillna(0)
                .astype(int)
            )

    # Normalize language.
    if "primary_language" in result.columns:
        result["primary_language"] = (
            result["primary_language"]
            .replace(0, pd.NA)
            .replace("", pd.NA)
            .fillna("Unknown")
        )

    # Keep is_private as a boolean.
    if "is_private" in result.columns:
        result["is_private"] = (
            result["is_private"]
            .fillna(False)
            .astype(bool)
        )

    columns = [
        "full_name",
        "commits",
    ]

    optional_columns = [
        "primary_language",
        "stars",
        "forks",
        "open_issues",
        "is_private",
        "pushed_at",
    ]

    for column in optional_columns:
        if column in result.columns:
            columns.append(column)

    result = result[columns].copy()

    result = result.rename(
        columns={
            "full_name": "name",
        }
    )

    # Convert timestamps to JSON-compatible strings.
    for column in result.columns:
        if pd.api.types.is_datetime64_any_dtype(
            result[column]
        ):
            result[column] = result[column].astype(str)

    repositories = result.to_dict(orient="records")

    return {
        "total_repositories": len(repositories),
        "repositories": repositories,
    }
