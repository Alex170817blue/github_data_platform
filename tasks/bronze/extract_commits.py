import json
from datetime import datetime, timezone
from pathlib import Path

from prefect import task

from tasks.github_client import GithubClient


@task(retries=3, retry_delay_seconds=10)
def extract_commits(full_name: str) -> Path:
    client = GithubClient()
    commits = client.get_commits(full_name)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = Path(f"storage/bronze/commits/dt={today}")
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = full_name.replace("/", "_")
    output_path = output_dir / f"{safe_name}.json"

    payload = {
        "repo_full_name": full_name,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "data": commits,
    }
    output_path.write_text(json.dumps(payload, indent=2))

    return output_path