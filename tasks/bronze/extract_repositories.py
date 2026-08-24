import json
from datetime import datetime, timezone
from pathlib import Path

from prefect import task

from tasks.github_client import GithubClient


@task(retries=3, retry_delay_seconds=10)
def extract_repositories(username: str) -> Path:
    client = GithubClient()
    repositories = client.get_repositories(username)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = Path(f"storage/bronze/repositories/dt={today}")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{username}.json"
    output_path.write_text(json.dumps(repositories, indent=2))

    return output_path