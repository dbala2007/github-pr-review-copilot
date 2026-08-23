# GitHub PR Review Copilot

GitHub PR Review Copilot fetches a pull request and its changed-file diffs from GitHub, sends them to an AutoGen review agent backed by OpenAI, and prints a structured JSON review.

The reviewer reports:

- Risk level
- Summary
- Issues found
- Suggested fixes
- Files to check

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for environment and dependency management
- An OpenAI API key
- A GitHub repository with an open pull request

## Setup

Create a virtual environment and install the dependencies:

```powershell
uv venv
uv pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the required values:

```dotenv
OPENAI_API_KEY=your_openai_api_key
GITHUB_OWNER=your_username_or_org
GITHUB_REPO=your_repo_name
PR_NUMBER=12
```

`GITHUB_TOKEN` is optional for public repositories, but recommended because it provides authenticated GitHub API requests and higher rate limits. Leave `PR_NUMBER` empty to review the newest open pull request in the repository.

Do not commit `.env` or API keys. They are excluded by `.gitignore`.

## Run Locally

Run the reviewer from the repository root:

```powershell
uv run python -m src.github_pr_review_copilot.main
```

The result is printed as formatted JSON. For example:

```json
{
	"risk_level": "medium",
	"summary": "The change refreshes expired credentials before sending mail.",
	"issues_found": [],
	"suggested_fixes": [],
	"files_to_check": ["src/gmail_sender.py"]
}
```

If the selected pull request does not exist, or if the repository has no open pull requests when `PR_NUMBER` is empty, the program reports that there is nothing to review.

## GitHub Actions

The workflow in `.github/workflows/pr-review.yml` runs when a pull request is opened, synchronized, reopened, or marked ready for review. It supplies the pull request number and repository details automatically.

Add this repository secret before enabling the workflow:

```text
OPENAI_API_KEY
```

The workflow uses GitHub's built-in `GITHUB_TOKEN` with read-only access to repository contents and pull requests.

## Project Layout

```text
src/github_pr_review_copilot/
	agents.py       # AutoGen review agent and OpenAI model configuration
	github_fetch.py # GitHub API requests and pull request mapping
	main.py         # Application entry point and review orchestration
	models.py       # Pydantic request and response models
data/
	sample_pr.json  # Example pull request payload for reference
.env.example      # Environment variable template
```

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | API key used by the OpenAI model client |
| `GITHUB_OWNER` | Yes | GitHub user or organization that owns the repository |
| `GITHUB_REPO` | Yes | Repository name |
| `PR_NUMBER` | No | Pull request number; empty means newest open PR |
| `GITHUB_TOKEN` | No | GitHub API token for authenticated requests |

## Notes

- The review agent uses the `gpt-4o-mini` model.
- GitHub file patches are limited by the GitHub API response and the configured `per_page=100` request.
- `data/sample_pr.json` documents the expected pull request data shape but is not currently read by the command-line entry point.
