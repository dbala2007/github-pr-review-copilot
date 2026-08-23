from pydantic import BaseModel
from typing import List


class ChangedFile(BaseModel):
    path: str
    diff: str


class PullRequestInput(BaseModel):
    pr_number: int
    title: str
    body: str
    author: str
    base_branch: str
    head_branch: str
    changed_files: List[ChangedFile]


class ReviewResult(BaseModel):
    risk_level: str
    summary: str
    issues_found: List[str] = []
    suggested_fixes: List[str] = []
    files_to_check: List[str] = []
