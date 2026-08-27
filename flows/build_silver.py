from datetime import datetime, timezone

from prefect import flow

from tasks.silver.build_commit_events import build_commit_events
from tasks.silver.build_pull_request_events import build_pull_request_events
from tasks.silver.build_repository_snapshots import build_repository_snapshots


@flow(name="build-silver-layer")
def build_silver_flow(bronze_dt: str | None = None):
    dt = bronze_dt or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    commits_path = build_commit_events(dt)
    print(f"Commit events updated: {commits_path}")

    pr_events_path = build_pull_request_events(dt)
    print(f"Pull request events updated: {pr_events_path}")

    snapshots_path = build_repository_snapshots(dt)
    print(f"Repository snapshots updated: {snapshots_path}")


if __name__ == "__main__":
    build_silver_flow()