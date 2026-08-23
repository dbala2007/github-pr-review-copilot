import json
import os
import re
from dotenv import load_dotenv

from src.github_pr_review_copilot.agents import build_review_agent
from src.github_pr_review_copilot.github_fetch import fetch_pull_request
from src.github_pr_review_copilot.models import ReviewResult

load_dotenv()

def clean_json_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*$", "", text)
    text = re.sub(r"^json\s*\n", "", text, flags=re.IGNORECASE)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text.strip()

async def run():
    owner = os.getenv("GITHUB_OWNER")
    repo = os.getenv("GITHUB_REPO")
    pr_number_text = os.getenv("PR_NUMBER", "").strip()

    if not owner or not repo:
        raise ValueError("GITHUB_OWNER and GITHUB_REPO must be set in .env")

    pr_number = int(pr_number_text) if pr_number_text else None

    try:
        pr = fetch_pull_request(owner, repo, pr_number)
    except ValueError as e:
        print(f"Nothing to review: {e}")
        return
    agent = build_review_agent()

    changed_files_text = "\n\n".join(
        [f"File: {f.path}\nDiff:\n{f.diff}" for f in pr.changed_files]
    )

    task = (
        f"PR Number: {pr.pr_number}\n"
        f"Title: {pr.title}\n"
        f"Body: {pr.body}\n"
        f"Author: {pr.author}\n"
        f"Base Branch: {pr.base_branch}\n"
        f"Head Branch: {pr.head_branch}\n\n"
        f"Changed Files:\n{changed_files_text}\n\n"
        "Return ONLY a raw JSON object.\n"
        "Do not wrap it in markdown fences.\n"
        "Do not prefix it with the word json.\n"
        "Do not add any extra text."
    )

    result = await agent.run(task=task)
    final_text = clean_json_text(result.messages[-1].content)
    review = ReviewResult.model_validate_json(final_text)

    print(review.model_dump_json(indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
