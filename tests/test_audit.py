import asyncio
import hashlib
import hmac
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from trustreply.app import app
from trustreply.audit import (
    AuditEvent, JsonlAuditSink, MemoryAuditSink, evaluate_with_audit,
    fingerprint_question, get_audit_sink,
)
from trustreply import service


QUESTION = "Is customer data encrypted at rest?"


def request(method, path, **kwargs):
    async def send():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            return await client.request(method, path, **kwargs)
    return asyncio.run(send())


def test_hmac_normalization_and_key_separation():
    expected = hmac.new(b"test-key", b"hello world", hashlib.sha256).hexdigest()
    assert fingerprint_question("  HELLO\nWorld ", b"test-key") == "hmac-sha256:" + expected
    assert fingerprint_question("hello world", b"other-key") != "hmac-sha256:" + expected


def test_event_content_and_schema(monkeypatch):
    monkeypatch.setenv("TRUSTREPLY_AUDIT_HMAC_KEY", "test-key-never-for-production")
    sink = MemoryAuditSink()
    result, event = evaluate_with_audit(QUESTION, sink, channel="api")
    serialized = event.model_dump_json()
    assert QUESTION not in serialized
    assert result.draft not in serialized
    assert result.evidence[0].excerpt not in serialized
    assert "test-key-never-for-production" not in serialized
    assert event.input.fingerprint_key_id == "environment"
    assert event.decision.criteria.retrieval_match_count >= event.decision.criteria.retrieval_threshold
    assert event.decision.reason_codes == ["direct_evidence", "approved", "current", "shareable"]
    assert event.occurred_at.utcoffset().total_seconds() == 0
    assert AuditEvent.model_validate_json(serialized) == event
    raw = event.model_dump()
    raw["question"] = QUESTION
    with pytest.raises(ValidationError):
        AuditEvent.model_validate(raw)
    with pytest.raises(ValueError):
        evaluate_with_audit(QUESTION, sink, channel="api", scenario_id="untrusted")


def test_local_key_and_unique_traces(monkeypatch):
    monkeypatch.delenv("TRUSTREPLY_AUDIT_HMAC_KEY", raising=False)
    sink = MemoryAuditSink()
    _, first = evaluate_with_audit(QUESTION, sink, channel="api")
    _, second = evaluate_with_audit(QUESTION, sink, channel="api")
    assert first.input.fingerprint_key_id == "local-ephemeral"
    assert first.input.question_fingerprint == second.input.question_fingerprint
    assert first.trace_id != second.trace_id
    assert first.event_id != second.event_id


def test_jsonl_append_and_concurrent_writes(tmp_path):
    path = tmp_path / "nested" / "audit.jsonl"
    sink = JsonlAuditSink(path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda _: evaluate_with_audit(QUESTION, sink, channel="api"), range(12)))
    events = [AuditEvent.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(events) == 12
    assert len({event.event_id for event in events}) == 12


@pytest.mark.parametrize("question", [QUESTION, "Is all customer data stored exclusively in the European Union?", "Unknown topic"])
def test_sink_failure_preserves_http_result(question, caplog):
    class BrokenSink:
        def emit(self, event):
            raise PermissionError("confidential exception content")

    app.dependency_overrides[get_audit_sink] = BrokenSink
    response = request("POST", "/questions", json={"question": question})
    assert response.status_code == 200
    assert response.json()["route"] == service.answer_question(question).route
    assert "audit_write_failed" in caplog.text
    assert response.headers["X-Trace-ID"] in caplog.text
    assert "confidential exception content" not in caplog.text
    assert question not in caplog.text


def test_real_disk_failure_is_absorbed(tmp_path, caplog):
    # Opening a directory as a file fails on both Windows and Unix.
    result, _ = evaluate_with_audit(QUESTION, JsonlAuditSink(tmp_path), channel="api")
    assert result.route == "auto_draft"
    assert "audit_write_failed" in caplog.text


def test_http_trace_and_jsonl(tmp_path):
    path = tmp_path / "events.jsonl"
    app.dependency_overrides[get_audit_sink] = lambda: JsonlAuditSink(path)
    response = request("POST", "/", data={"question": QUESTION})
    event = AuditEvent.model_validate_json(path.read_text(encoding="utf-8"))
    assert response.status_code == 200
    assert str(event.trace_id) == response.headers["X-Trace-ID"]
    assert str(event.trace_id) in response.text
    assert event.context.channel == "web"
    assert event.context.scenario_id is None
    assert response.headers["Cache-Control"] == "no-store"
    assert "?" not in str(response.request.url)


def test_get_does_not_evaluate_and_invalid_posts_emit_nothing(audit_sink):
    page = request("GET", "/", params={"question": QUESTION})
    assert 'id="result"' not in page.text
    assert request("POST", "/", json={"question": QUESTION}).status_code == 415
    for body in ("", "question=", "question=a&question=b", "other=a", "question=%FF"):
        assert request("POST", "/", content=body, headers={"Content-Type": "application/x-www-form-urlencoded"}).status_code == 422
    assert request("POST", "/", data={"question": "x" * 9000}).status_code == 413
    assert request("POST", "/questions", json={"question": ""}).status_code == 422
    assert audit_sink.events == []


def test_corpus_version_changes_with_content_not_json_format(tmp_path, monkeypatch):
    documents = service._load_documents()
    monkeypatch.setattr(service, "CORPUS_DIRECTORY", tmp_path)
    def write(documents, indent):
        for i, document in enumerate(documents):
            (tmp_path / f"{i}.json").write_text(json.dumps(document, indent=indent), encoding="utf-8")
    write(documents, None)
    _, first = evaluate_with_audit(QUESTION, MemoryAuditSink(), channel="api")
    write(documents, 4)
    _, second = evaluate_with_audit(QUESTION, MemoryAuditSink(), channel="api")
    assert first.context.corpus_version == second.context.corpus_version
    documents[0]["current"] = not documents[0]["current"]
    write(documents, 4)
    _, third = evaluate_with_audit(QUESTION, MemoryAuditSink(), channel="api")
    assert first.context.corpus_version != third.context.corpus_version
