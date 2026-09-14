from trustreply.fidelity import assess_result_fidelity
from trustreply.service import answer_question


KNOWN_DOCUMENT_IDS = {
    "security-baseline-2026",
    "data-residency-internal-2026",
    "retention-policy-2024",
    "product-capabilities-guidance-2026",
    "incident-response-notes-2026",
}


def test_fidelity_accepts_an_exact_cited_claim() -> None:
    result = answer_question("Is customer data encrypted at rest?")

    assessment = assess_result_fidelity(result, KNOWN_DOCUMENT_IDS)

    assert assessment.unsupported_claims == ()
    assert assessment.invalid_citation_ids == ()


def test_fidelity_flags_an_added_claim_and_unknown_citation() -> None:
    result = answer_question("Is customer data encrypted at rest?")
    altered_evidence = result.evidence[0].model_copy(update={"document_id": "unknown-document"})
    altered_result = result.model_copy(update={
        "draft": f"{result.draft} The service is certified for every regulated industry.",
        "evidence": [altered_evidence],
    })

    assessment = assess_result_fidelity(altered_result, KNOWN_DOCUMENT_IDS)

    assert assessment.unsupported_claims == (
        "Customer data is encrypted at rest using AES-256.",
        "The service is certified for every regulated industry.",
    )
    assert assessment.invalid_citation_ids == ("unknown-document",)
