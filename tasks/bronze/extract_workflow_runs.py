import json
from datetime import datetime, timezone
from pathlib import Path

from prefect import task

from tasks.github_client import GithubClient


@task(retries=3, retry_delay_seconds=10)
def extract_workflow_runs(full_name: str) -> Path:
    client = GithubClient()
    workflow_runs = client.get_workflow_runs(full_name)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = Path(f"storage/bronze/workflow_runs/dt={today}")
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = full_name.replace("/", "_")
    output_path = output_dir / f"{safe_name}.json"

    payload = {
        "repo_full_name": full_name,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "data": workflow_runs,
    }
    output_path.write_text(json.dumps(payload, indent=2))

    return output_path