import asyncio

import pytest
from httpx import ASGITransport, AsyncClient, Response

from trustreply.app import app


AUTO_DRAFT_QUESTION = "Is customer data encrypted at rest?"
HUMAN_REVIEW_QUESTION = "Is all customer data stored exclusively in the European Union?"
INSUFFICIENT_EVIDENCE_QUESTION = "Do you provide customer-managed encryption keys?"


async def _request(method: str, path: str, **kwargs: object) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, path, **kwargs)


def test_demo_page_exposes_question_form_and_scope_notice() -> None:
    response = asyncio.run(_request("GET", "/"))

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<form method="post"' in response.text
    assert '/?question=' not in response.text
    assert '<label for="question">Question</label>' in response.text
    assert 'name="question"' in response.text
    assert "Synthetic corpus" in response.text
    assert "A human must review any draft before sending" in response.text


def test_auto_draft_page_displays_draft_and_citation() -> None:
    response = asyncio.run(_request("POST", "/", data={"question": AUTO_DRAFT_QUESTION}))

    assert response.status_code == 200
    assert 'data-route="auto_draft"' in response.text
    assert "Customer data is encrypted at rest using AES-256." in response.text
    assert "Synthetic security baseline" in response.text
    assert "Approved: yes" in response.text
    assert "Current: yes" in response.text
    assert "Shareable: yes" in response.text


def test_human_review_page_displays_owner_without_draft() -> None:
    response = asyncio.run(_request("POST", "/", data={"question": HUMAN_REVIEW_QUESTION}))

    assert response.status_code == 200
    assert 'data-route="human_review"' in response.text
    assert "Review owner: Privacy" in response.text
    assert "Synthetic data residency guidance" in response.text
    assert "Shareable: no" in response.text
    assert 'id="draft"' not in response.text


def test_insufficient_evidence_page_displays_safe_abstention() -> None:
    response = asyncio.run(_request("POST", "/", data={"question": INSUFFICIENT_EVIDENCE_QUESTION}))

    assert response.status_code == 200
    assert 'data-route="insufficient_evidence"' in response.text
    assert "Safe abstention" in response.text
    assert "No approved source directly supports a safe response." in response.text
    assert 'id="draft"' not in response.text
    assert 'id="evidence"' not in response.text


def test_demo_page_escapes_question_html() -> None:
    unsafe_question = '<script>alert("unsafe")</script>'
    response = asyncio.run(_request("POST", "/", data={"question": unsafe_question}))

    assert response.status_code == 200
    assert unsafe_question not in response.text
    assert "&lt;script&gt;alert(&quot;unsafe&quot;)&lt;/script&gt;" in response.text


@pytest.mark.parametrize("question", ["", "x" * 501])
def test_demo_rejects_invalid_question_length(question: str) -> None:
    response = asyncio.run(_request("POST", "/", data={"question": question}))

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("question", "expected_route"),
    [
        (AUTO_DRAFT_QUESTION, "auto_draft"),
        (HUMAN_REVIEW_QUESTION, "human_review"),
        (INSUFFICIENT_EVIDENCE_QUESTION, "insufficient_evidence"),
    ],
)
def test_demo_route_matches_api_result(question: str, expected_route: str) -> None:
    page_response = asyncio.run(_request("POST", "/", data={"question": question}))
    api_response = asyncio.run(_request("POST", "/questions", json={"question": question}))

    assert api_response.json()["route"] == expected_route
    assert f'data-route="{expected_route}"' in page_response.text
