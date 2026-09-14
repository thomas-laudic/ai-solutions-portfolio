import asyncio

from httpx import ASGITransport, AsyncClient
from trustreply.app import app


def test_direct_approved_evidence_returns_a_sourced_auto_draft() -> None:
    async def submit_question() -> object:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/questions", json={"question": "Is customer data encrypted at rest?"})

    response = asyncio.run(submit_question())

    assert response.status_code == 200
    result = response.json()
    assert result["route"] == "auto_draft"
    assert result["status"] == "draft_ready_for_human_check"
    assert result["draft"] == "Customer data is encrypted at rest using AES-256."
    assert result["evidence"] == [{
        "document_id": "security-baseline-2026",
        "title": "Synthetic security baseline",
        "excerpt": "Customer data is encrypted at rest using AES-256.",
        "approved": True,
        "current": True,
        "shareable": True,
    }]
    assert result["unsupported_claims"] == []
    assert result["cost_usd"] == 0.0
    assert result["latency_ms"] >= 0
