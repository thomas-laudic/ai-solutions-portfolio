import asyncio

from httpx import ASGITransport, AsyncClient

from trustreply.app import app


async def _submit(question: str) -> object:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post("/questions", json={"question": question})


def test_restricted_evidence_requires_privacy_review() -> None:
    response = asyncio.run(_submit("Is all customer data stored exclusively in the European Union?"))

    assert response.status_code == 200
    result = response.json()
    assert result["route"] == "human_review"
    assert result["status"] == "review_required"
    assert result["draft"] is None
    assert result["review_owner"] == "Privacy"
    assert result["evidence"][0]["document_id"] == "data-residency-internal-2026"
    assert result["evidence"][0]["shareable"] is False
    assert result["unsupported_claims"] == []


def test_missing_evidence_returns_safe_abstention_without_a_draft() -> None:
    response = asyncio.run(_submit("Do you provide customer-managed encryption keys?"))

    assert response.status_code == 200
    result = response.json()
    assert result["route"] == "insufficient_evidence"
    assert result["status"] == "safe_abstention"
    assert result["draft"] is None
    assert result["evidence"] == []
    assert result["review_owner"] is None
    assert result["unsupported_claims"] == []
