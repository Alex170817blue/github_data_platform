from datetime import date

from pydantic import BaseModel


class DeployFrequencyItem(BaseModel):
    repo_full_name: str
    period_start: date
    deploys_count: int


class LeadTimeItem(BaseModel):
    repo_full_name: str
    period_start: date
    avg_lead_time_hours: float
    merged_prs_count: int


class ContributorActivityItem(BaseModel):
    repo_full_name: str
    contributor: str
    period_start: date
    commits_count: int