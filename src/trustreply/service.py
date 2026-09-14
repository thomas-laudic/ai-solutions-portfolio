"""Deterministic retrieval and routing for the first vertical slice."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path
from time import perf_counter
from typing import Any

from trustreply.fidelity import assess_result_fidelity
from trustreply.models import Evidence, QuestionResult

CORPUS_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "corpus"


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _load_documents() -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(CORPUS_DIRECTORY.glob("*.json"))]


def _document_scores(question: str, documents: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    question_tokens = _tokens(question)
    return [
        (len(question_tokens & set(document["keywords"])), document)
        for document in documents
    ]


def _select_document(matches: list[tuple[int, dict[str, Any]]]) -> dict[str, Any] | None:
    score, document = max(matches, default=(0, None), key=lambda match: match[0])
    if document is None or score < document["minimum_match_count"]:
        return None
    return document


def classify_question_domain(question: str) -> str:
    """Classify a question as in-domain when it has any corpus vocabulary signal."""
    scores = _document_scores(question, _load_documents())
    return "in_domain" if any(score > 0 for score, _ in scores) else "out_of_domain"


def _evidence_from(document: dict[str, Any]) -> Evidence:
    return Evidence(
        document_id=document["id"],
        title=document["title"],
        excerpt=document["excerpt"],
        approved=document["approved"],
        current=document["current"],
        shareable=document["shareable"],
    )


def answer_question(question: str, *, decision_context: dict[str, Any] | None = None) -> QuestionResult:
    """Return a safe structured result from the approved local corpus."""
    started_at = perf_counter()
    documents = _load_documents()
    scores = _document_scores(question, documents)
    document = _select_document(scores)

    if document is None:
        route = "insufficient_evidence"
        status = "safe_abstention"
        draft = None
        evidence = []
        justification = "No approved source directly supports a safe response."
        review_owner = None
    elif document["contradictory"]:
        route = "human_review"
        status = "review_required"
        draft = None
        evidence = [_evidence_from(document)]
        justification = "The matching evidence is contradictory and requires expert review."
        review_owner = document["review_owner"]
    elif document["ambiguous"]:
        route = "human_review"
        status = "review_required"
        draft = None
        evidence = [_evidence_from(document)]
        justification = "The matching evidence is ambiguous and requires expert review."
        review_owner = document["review_owner"]
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

    result = QuestionResult(
        route=route,
        status=status,
        draft=draft,
        evidence=evidence,
        justification=justification,
        review_owner=review_owner,
        unsupported_claims=[],
        cost_usd=0.0,
        latency_ms=0.0,
    )
    fidelity = assess_result_fidelity(result, {item["id"] for item in documents})
    if decision_context is not None:
        score, candidate = max(scores, default=(0, None), key=lambda match: match[0])
        if document is None:
            reasons = ["no_direct_evidence"]
        elif document["contradictory"]:
            reasons = ["contradictory"]
        elif document["ambiguous"]:
            reasons = ["ambiguous"]
        else:
            reasons = [code for flag, code in (
                ("approved", "not_approved"), ("current", "not_current"), ("shareable", "restricted")
            ) if not document[flag]] or ["direct_evidence", "approved", "current", "shareable"]
        canonical = json.dumps(sorted(documents, key=lambda item: item["id"]), sort_keys=True, separators=(",", ":"))
        decision_context.update(
            corpus_version="sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            domain="in_domain" if score > 0 else "out_of_domain",
            reason_codes=reasons,
            invalid_citation_count=len(fidelity.invalid_citation_ids),
            criteria={
                "candidate_document_id": candidate["id"] if candidate is not None else None,
                "retrieval_match_count": score,
                "retrieval_threshold": candidate["minimum_match_count"] if candidate is not None else None,
                **{flag: candidate[flag] if candidate is not None else None
                   for flag in ("approved", "current", "shareable", "ambiguous", "contradictory")},
            },
        )
    return result.model_copy(update={
        "unsupported_claims": list(fidelity.unsupported_claims),
        "latency_ms": round((perf_counter() - started_at) * 1000, 3),
    })
