import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from src.github_pr_review_copilot.models import ChangedFile, PullRequestInput

load_dotenv()


def _request_json(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-pr-review-copilot",
    }

    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)

    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_latest_pull_request(owner: str, repo: str) -> PullRequestInput:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open&sort=created&direction=desc&per_page=1"

    try:
        data = _request_json(url)
    except URLError as e:
        raise RuntimeError(f"Network error while fetching latest PR: {e}") from e

    if not data:
        raise ValueError(f"No open pull requests found in {owner}/{repo}.")

    pr = data[0]
    return fetch_pull_request(owner, repo, pr["number"])


def fetch_pull_request(owner: str, repo: str, pr_number: int | None = None) -> PullRequestInput:
    if pr_number is None:
        return fetch_latest_pull_request(owner, repo)

    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files?per_page=100"

    try:
        pr_data = _request_json(pr_url)
        files_data = _request_json(files_url)
    except HTTPError as e:
        if e.code == 404:
            raise ValueError(f"PR #{pr_number} not found in {owner}/{repo}.") from e
        raise
    except URLError as e:
        raise RuntimeError(f"Network error while fetching PR: {e}") from e

    changed_files = []
    for item in files_data:
        changed_files.append(
            ChangedFile(
                path=item["filename"],
                diff=item.get("patch", ""),
            )
        )

    return PullRequestInput(
        pr_number=pr_data["number"],
        title=pr_data["title"],
        body=pr_data.get("body", ""),
        author=pr_data["user"]["login"],
        base_branch=pr_data["base"]["ref"],
        head_branch=pr_data["head"]["ref"],
        changed_files=changed_files,
    )
