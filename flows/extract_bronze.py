import json
import os
from dotenv import load_dotenv
from prefect import flow

from tasks.bronze.extract_repositories import extract_repositories
from tasks.bronze.extract_commits import extract_commits
from tasks.bronze.extract_pull_requests import extract_pull_requests
from tasks.bronze.extract_pull_request_commits import extract_pull_request_commits
from tasks.bronze.extract_workflow_runs import extract_workflow_runs

load_dotenv()


@flow(name="extract-bronze-layer")
def extract_bronze_flow():
    username = os.getenv("GITHUB_USERNAME")

    repos_path = extract_repositories(username)
    repositories = json.loads(repos_path.read_text())

    print(f"Found {len(repositories)} repositories")

    for repo in repositories:
        full_name = repo["full_name"]

        print(f"Extracting data for {full_name}...")
        extract_commits(full_name)
        extract_workflow_runs(full_name)

        pr_path = extract_pull_requests(full_name)
        pr_payload = json.loads(pr_path.read_text())

        for pr in pr_payload["data"]:
            extract_pull_request_commits(full_name, pr["number"])

    print("Bronze extraction completed.")


if __name__ == "__main__":
    extract_bronze_flow()