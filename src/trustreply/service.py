"""Deterministic retrieval and routing for the first vertical slice."""

from __future__ import annotations

import json
import re
from pathlib import Path
from time import perf_counter
from typing import Any


CORPUS_PATH = Path(__file__).resolve().parents[2] / "data" / "corpus" / "security_baseline.json"


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _load_document() -> dict[str, Any]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def answer_question(question: str) -> dict[str, Any]:
    """Return a safe structured result from the approved local corpus."""
    started_at = perf_counter()
    document = _load_document()
    matched_keywords = _tokens(question) & set(document["keywords"])
    direct_evidence = len(matched_keywords) >= 4

    if direct_evidence and all(document[key] for key in ("approved", "current", "shareable")):
        route = "auto_draft"
        status = "draft_ready_for_human_check"
        draft = document["response"]
        evidence = [{"document_id": document["id"], "title": document["title"], "excerpt": document["excerpt"]}]
        justification = "Approved, current, shareable evidence directly covers the standard question."
    else:
        route = "insufficient_evidence"
        status = "safe_abstention"
        draft = None
        evidence = []
        justification = "No approved source directly supports a safe response."

    return {
        "route": route,
        "status": status,
        "draft": draft,
        "evidence": evidence,
        "justification": justification,
        "review_owner": None,
        "unsupported_claims": [],
        "cost_usd": 0.0,
        "latency_ms": round((perf_counter() - started_at) * 1000, 3),
    }
