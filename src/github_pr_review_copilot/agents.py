from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.github_pr_review_copilot.models import ReviewResult


def build_review_agent():
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini"
    )

    agent = AssistantAgent(
        name="review_agent",
        model_client=model_client,
        system_message=(
            "You are a GitHub pull/merge request review assistant. "
            "Review the changed files, identify risks, missing tests, "
            "possible bugs, and suggest fixes. "
            "Return ONLY a raw JSON object. "
            "Do not wrap it in markdown fences. "
            "Do not prefix it with the word json. "
            "Do not add any extra text."
            "Respond with risk_level, summary, issues_found, suggested_fixes, files_to_check as JSON matching to the Pydantic Response Model"
        ),
    )
    return agent
