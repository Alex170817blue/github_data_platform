from typing import Literal

from fastapi import APIRouter, Query

from api.data import read_gold_table
from api.schemas import ContributorActivityItem, DeployFrequencyItem, LeadTimeItem

router = APIRouter(prefix="/metrics", tags=["metrics"])

Granularity = Literal["weekly", "monthly"]


def _period_column(granularity: Granularity) -> str:
    return "week_start" if granularity == "weekly" else "month_start"


@router.get("/deploy-frequency", response_model=list[DeployFrequencyItem])
def get_deploy_frequency(
    granularity: Granularity = Query("weekly"),
    repo: str | None = Query(None, description="Filter by repo_full_name"),
):
    table_name = f"deploy_frequency_{granularity}"
    df = read_gold_table(table_name)

    if df.empty:
        return []

    if repo:
        df = df[df["repo_full_name"] == repo]

    period_col = _period_column(granularity)
    df = df.rename(columns={period_col: "period_start"})

    return df.to_dict(orient="records")


@router.get("/lead-time", response_model=list[LeadTimeItem])
def get_lead_time(
    granularity: Granularity = Query("weekly"),
    repo: str | None = Query(None, description="Filter by repo_full_name"),
):
    table_name = f"lead_time_{granularity}"
    df = read_gold_table(table_name)

    if df.empty:
        return []

    if repo:
        df = df[df["repo_full_name"] == repo]

    period_col = _period_column(granularity)
    df = df.rename(columns={period_col: "period_start"})

    return df.to_dict(orient="records")


@router.get("/contributor-activity", response_model=list[ContributorActivityItem])
def get_contributor_activity(
    granularity: Granularity = Query("weekly"),
    repo: str | None = Query(None, description="Filter by repo_full_name"),
    contributor: str | None = Query(None, description="Filter by contributor"),
):
    table_name = f"contributor_activity_{granularity}"
    df = read_gold_table(table_name)

    if df.empty:
        return []

    if repo:
        df = df[df["repo_full_name"] == repo]
    if contributor:
        df = df[df["contributor"] == contributor]

    period_col = _period_column(granularity)
    df = df.rename(columns={period_col: "period_start"})

    return df.to_dict(orient="records")