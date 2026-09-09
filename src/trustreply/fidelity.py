"""Deterministic checks for citations and extractive draft claims."""

from __future__ import annotations

import re
from dataclasses import dataclass

from trustreply.models import QuestionResult


@dataclass(frozen=True)
class FidelityAssessment:
    unsupported_claims: tuple[str, ...]
    invalid_citation_ids: tuple[str, ...]


def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text.strip()) if sentence.strip()]


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def assess_result_fidelity(result: QuestionResult, known_document_ids: set[str]) -> FidelityAssessment:
    """Require every draft sentence to occur in a known cited excerpt."""
    invalid_citation_ids = tuple(
        evidence.document_id
        for evidence in result.evidence
        if evidence.document_id not in known_document_ids
    )
    supported_claims = {
        _normalize(sentence)
        for evidence in result.evidence
        if evidence.document_id in known_document_ids
        for sentence in _sentences(evidence.excerpt)
    }
    unsupported_claims = tuple(
        sentence
        for sentence in _sentences(result.draft or "")
        if _normalize(sentence) not in supported_claims
    )
    return FidelityAssessment(
        unsupported_claims=unsupported_claims,
        invalid_citation_ids=invalid_citation_ids,
    )
