"""Validated API contracts for TrustReply's first vertical slice."""

from typing import Literal

from pydantic import BaseModel


Route = Literal["auto_draft", "human_review", "insufficient_evidence"]


class Evidence(BaseModel):
    document_id: str
    title: str
    excerpt: str
    approved: bool
    current: bool
    shareable: bool


class QuestionResult(BaseModel):
    route: Route
    status: str
    draft: str | None
    evidence: list[Evidence]
    justification: str
    review_owner: str | None
    unsupported_claims: list[str]
    cost_usd: float
    latency_ms: float
