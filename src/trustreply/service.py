"""Deterministic retrieval and routing for the first vertical slice."""

from __future__ import annotations

import json
import re
from pathlib import Path
from time import perf_counter
from typing import Any

from trustreply.models import Evidence, QuestionResult

CORPUS_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "corpus"


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _load_documents() -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in CORPUS_DIRECTORY.glob("*.json")]


def _select_document(question: str, documents: list[dict[str, Any]]) -> dict[str, Any] | None:
    question_tokens = _tokens(question)
    matches = [
        (len(question_tokens & set(document["keywords"])), document)
        for document in documents
    ]
    score, document = max(matches, default=(0, None), key=lambda match: match[0])
    if document is None or score < document["minimum_match_count"]:
        return None
    return document


def _evidence_from(document: dict[str, Any]) -> Evidence:
    return Evidence(
        document_id=document["id"],
        title=document["title"],
        excerpt=document["excerpt"],
        approved=document["approved"],
        current=document["current"],
        shareable=document["shareable"],
    )


def answer_question(question: str) -> QuestionResult:
    """Return a safe structured result from the approved local corpus."""
    started_at = perf_counter()
    document = _select_document(question, _load_documents())

    if document is None:
        route = "insufficient_evidence"
        status = "safe_abstention"
        draft = None
        evidence = []
        justification = "No approved source directly supports a safe response."
        review_owner = None
    elif not all(document[key] for key in ("approved", "current", "shareable")):
        route = "human_review"
        status = "review_required"
        draft = None
        evidence = [_evidence_from(document)]
        justification = "The evidence is restricted, not current, or not approved for a direct response."
        review_owner = document["review_owner"]
    else:
        route = "auto_draft"
        status = "draft_ready_for_human_check"
        draft = document["response"]
        evidence = [_evidence_from(document)]
        justification = "Approved, current, shareable evidence directly covers the standard question."
        review_owner = None

    return QuestionResult(
        route=route,
        status=status,
        draft=draft,
        evidence=evidence,
        justification=justification,
        review_owner=review_owner,
        unsupported_claims=[],
        cost_usd=0.0,
        latency_ms=round((perf_counter() - started_at) * 1000, 3),
    )
