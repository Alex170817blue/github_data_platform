import json
import os
from dotenv import load_dotenv
from prefect import flow

from tasks.bronze.extract_repositories import extract_repositories
from tasks.bronze.extract_commits import extract_commits
from tasks.bronze.extract_pull_requests import extract_pull_requests

load_dotenv()


@flow(name="extract-bronze-layer")
def extract_bronze_flow():
    username = os.getenv("GITHUB_USERNAME")

    repos_path = extract_repositories(username)
    repositories = json.loads(repos_path.read_text())

    print(f"Found {len(repositories)} repositories")

    for repo in repositories:
        full_name = repo["full_name"]

        print(f"Extracting commits and PRs for {full_name}...")
        extract_commits(full_name)
        extract_pull_requests(full_name)

    print("Bronze extraction completed.")


if __name__ == "__main__":
    extract_bronze_flow()