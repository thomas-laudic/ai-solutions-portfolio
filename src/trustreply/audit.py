"""Small, content-free decision events and synchronous audit transports."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Literal, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from trustreply.models import QuestionResult, Route
from trustreply.service import answer_question


class AuditModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuditContext(AuditModel):
    channel: Literal["api", "web", "evaluation"]
    scenario_id: str | None = None
    application_version: str = "0.1.0"
    build_revision: str = "unknown"
    policy_version: str = "deterministic-v1"
    corpus_version: str


class AuditInput(AuditModel):
    question_fingerprint: str
    fingerprint_key_id: str
    question_length_bucket: Literal["1-50", "51-100", "101-500"]


class DecisionCriteria(AuditModel):
    candidate_document_id: str | None
    retrieval_match_count: int = Field(ge=0)
    retrieval_threshold: int | None
    approved: bool | None
    current: bool | None
    shareable: bool | None
    ambiguous: bool | None
    contradictory: bool | None


class AuditDecision(AuditModel):
    domain: Literal["in_domain", "out_of_domain"]
    route: Route
    status: str
    reason_codes: list[Literal[
        "no_direct_evidence", "contradictory", "ambiguous", "not_approved",
        "not_current", "restricted", "direct_evidence", "approved", "current", "shareable",
    ]]
    review_owner: str | None
    criteria: DecisionCriteria


class AuditOutput(AuditModel):
    draft_present: bool
    citation_ids: list[str]
    citation_count: int = Field(ge=0)
    unsupported_claim_count: int = Field(ge=0)
    invalid_citation_count: int = Field(ge=0)


class AuditPerformance(AuditModel):
    processing_latency_ms: float = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0)


class AuditEvent(AuditModel):
    schema_version: Literal["1.0"] = "1.0"
    event_type: Literal["trustreply.decision.completed"] = "trustreply.decision.completed"
    event_id: UUID = Field(default_factory=uuid4)
    trace_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: AuditContext
    input: AuditInput
    decision: AuditDecision
    output: AuditOutput
    performance: AuditPerformance


class AuditSink(Protocol):
    def emit(self, event: AuditEvent) -> None: ...


class JsonlAuditSink:
    """One shared sink per process; no multiprocess append guarantee."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()

    def emit(self, event: AuditEvent) -> None:
        line = event.model_dump_json() + "\n"
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(line)


class MemoryAuditSink:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def emit(self, event: AuditEvent) -> None:
        self.events.append(event)


_LOCAL_KEY = secrets.token_bytes(32)
_DEFAULT_SINK = JsonlAuditSink(Path(__file__).resolve().parents[2] / "logs" / "audit.jsonl")
logger = logging.getLogger(__name__)


def get_audit_sink() -> AuditSink:
    return _DEFAULT_SINK


def fingerprint_question(question: str, key: bytes) -> str:
    normalized = " ".join(question.casefold().split())
    return "hmac-sha256:" + hmac.new(key, normalized.encode("utf-8"), hashlib.sha256).hexdigest()


def evaluate_with_audit(
    question: str, sink: AuditSink, *, channel: Literal["api", "web", "evaluation"],
    scenario_id: str | None = None,
) -> tuple[QuestionResult, AuditEvent]:
    """Keep transport failure separate from decision and event validation failures."""
    if scenario_id is not None and channel != "evaluation":
        raise ValueError("Scenario IDs are reserved for the evaluation runner")
    details: dict = {}
    result = answer_question(question, decision_context=details)
    configured_key = os.environ.get("TRUSTREPLY_AUDIT_HMAC_KEY")
    key = configured_key.encode("utf-8") if configured_key else _LOCAL_KEY
    event = AuditEvent(
        context=AuditContext(
            channel=channel, scenario_id=scenario_id,
            corpus_version=details["corpus_version"],
            build_revision=os.environ.get("TRUSTREPLY_BUILD_REVISION", "unknown"),
        ),
        input=AuditInput(
            question_fingerprint=fingerprint_question(question, key),
            fingerprint_key_id="environment" if configured_key else "local-ephemeral",
            question_length_bucket="1-50" if len(question) <= 50 else "51-100" if len(question) <= 100 else "101-500",
        ),
        decision=AuditDecision(
            domain=details["domain"], route=result.route, status=result.status,
            reason_codes=details["reason_codes"], review_owner=result.review_owner,
            criteria=DecisionCriteria(**details["criteria"]),
        ),
        output=AuditOutput(
            draft_present=result.draft is not None,
            citation_ids=[item.document_id for item in result.evidence],
            citation_count=len(result.evidence),
            unsupported_claim_count=len(result.unsupported_claims),
            invalid_citation_count=details["invalid_citation_count"],
        ),
        performance=AuditPerformance(
            processing_latency_ms=result.latency_ms, estimated_cost_usd=result.cost_usd,
        ),
    )
    try:
        sink.emit(event)
    except Exception:
        # Never include the exception text: a transport may echo confidential data.
        logger.error("audit_write_failed trace_id=%s", event.trace_id)
    return result, event
