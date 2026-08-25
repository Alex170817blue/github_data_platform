import os
import httpx

GITHUB_API_BASE = "https://api.github.com"


class GithubClient:
    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self._client = httpx.Client(
            base_url=GITHUB_API_BASE,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=30.0,
        )

    def get_repositories(self, username: str) -> list[dict]:
        response = self._client.get(f"/users/{username}/repos", params={"per_page": 100})
        response.raise_for_status()
        return response.json()

    def get_commits(self, full_name: str, since: str | None = None) -> list[dict]:
        params = {"per_page": 100}
        if since:
            params["since"] = since

        response = self._client.get(f"/repos/{full_name}/commits", params=params)

        if response.status_code == 409:
            # Repository vuoto (nessun commit) GitHub restituisce 409 invece di lista vuota
            return []

        response.raise_for_status()
        return response.json()

    def get_pull_requests(self, full_name: str, state: str = "all") -> list[dict]:
        response = self._client.get(
            f"/repos/{full_name}/pulls",
            params={"state": state, "per_page": 100},
        )
        response.raise_for_status()
        return response.json()