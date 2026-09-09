import json
from pathlib import Path

from trustreply.fidelity import assess_result_fidelity
from trustreply.service import answer_question, classify_question_domain


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DATASET_PATH = REPOSITORY_ROOT / "data" / "scenarios" / "golden_dataset.json"
CORPUS_DIRECTORY = REPOSITORY_ROOT / "data" / "corpus"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_golden_dataset() -> None:
    scenarios = _load_json(GOLDEN_DATASET_PATH)
    assert isinstance(scenarios, list)
    assert len(scenarios) == 18
    assert len({scenario["id"] for scenario in scenarios}) == 18

    known_document_ids = {
        _load_json(path)["id"]
        for path in CORPUS_DIRECTORY.glob("*.json")
    }
    route_matches = 0
    citation_matches = 0
    expected_abstentions = 0
    correct_abstentions = 0
    expected_reviews = 0
    correct_reviews = 0
    expected_out_of_domain = 0
    correct_out_of_domain = 0
    unsupported_claim_count = 0
    invalid_citation_count = 0
    forbidden_claim_count = 0
    total_cost_usd = 0.0
    latencies_ms: list[float] = []
    failures: list[str] = []

    for scenario in scenarios:
        result = answer_question(scenario["question"])
        actual_evidence_ids = [item.document_id for item in result.evidence]
        route_matches += result.route == scenario["expected_route"]
        citation_matches += actual_evidence_ids == scenario["expected_evidence_ids"]
        total_cost_usd += result.cost_usd
        latencies_ms.append(result.latency_ms)

        if scenario["expected_route"] == "insufficient_evidence":
            expected_abstentions += 1
            correct_abstentions += result.route == "insufficient_evidence"
        if scenario["expected_route"] == "human_review":
            expected_reviews += 1
            correct_reviews += result.route == "human_review"
        if scenario["category"] == "out_of_domain":
            expected_out_of_domain += 1
            correct_out_of_domain += classify_question_domain(scenario["question"]) == "out_of_domain"

        fidelity = assess_result_fidelity(result, known_document_ids)
        unsupported_claim_count += len(fidelity.unsupported_claims)
        invalid_citation_count += len(fidelity.invalid_citation_ids)
        draft_text = (result.draft or "").casefold()
        forbidden_claim_count += sum(
            forbidden.casefold() in draft_text
            for forbidden in scenario["forbidden_claims"]
        )

        if result.route != scenario["expected_route"]:
            failures.append(f'{scenario["id"]}: expected {scenario["expected_route"]}, got {result.route}')
        if actual_evidence_ids != scenario["expected_evidence_ids"]:
            failures.append(
                f'{scenario["id"]}: expected citations {scenario["expected_evidence_ids"]}, got {actual_evidence_ids}'
            )
        if result.review_owner != scenario["expected_review_owner"]:
            failures.append(
                f'{scenario["id"]}: expected owner {scenario["expected_review_owner"]}, got {result.review_owner}'
            )
        if fidelity.unsupported_claims or fidelity.invalid_citation_ids:
            failures.append(f'{scenario["id"]}: failed fidelity checks')

    scenario_count = len(scenarios)
    route_accuracy = route_matches / scenario_count
    citation_compliance = citation_matches / scenario_count
    abstention_recall = correct_abstentions / expected_abstentions
    review_recall = correct_reviews / expected_reviews
    out_of_domain_recall = correct_out_of_domain / expected_out_of_domain
    mean_latency_ms = sum(latencies_ms) / scenario_count

    print("\nGolden Dataset Evaluation")
    print(f"Scenarios: {scenario_count}")
    print(f"Route accuracy: {route_accuracy:.1%}")
    print(f"Abstention recall: {abstention_recall:.1%}")
    print(f"Human-review recall: {review_recall:.1%}")
    print(f"Out-of-domain recall: {out_of_domain_recall:.1%}")
    print(f"Citation compliance: {citation_compliance:.1%}")
    print(f"Unsupported claims: {unsupported_claim_count}")
    print(f"Invalid citations: {invalid_citation_count}")
    print(f"Forbidden claims: {forbidden_claim_count}")
    print(f"Mean latency: {mean_latency_ms:.3f} ms")
    print(f"Estimated cost: ${total_cost_usd:.4f}")

    assert not failures, "\n".join(failures)
    assert route_accuracy == 1.0
    assert abstention_recall == 1.0
    assert review_recall == 1.0
    assert out_of_domain_recall == 1.0
    assert citation_compliance == 1.0
    assert unsupported_claim_count == 0
    assert invalid_citation_count == 0
    assert forbidden_claim_count == 0
