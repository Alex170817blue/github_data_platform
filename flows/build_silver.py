from datetime import datetime, timezone

from prefect import flow

from tasks.silver.build_commit_events import build_commit_events
from tasks.silver.build_pull_request_events import build_pull_request_events
from tasks.silver.build_repository_snapshots import build_repository_snapshots
from tasks.silver.build_deploy_events import build_deploy_events
from tasks.silver.build_lead_times import build_lead_times


@flow(name="build-silver-layer")
def build_silver_flow(bronze_dt: str | None = None):
    dt = bronze_dt or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    build_commit_events(dt)
    build_pull_request_events(dt)  
    build_repository_snapshots(dt)
    build_deploy_events(dt)
    build_lead_times(dt)           # dipende da pull_request_events

    print("Silver layer build completed.")


if __name__ == "__main__":
    build_silver_flow()