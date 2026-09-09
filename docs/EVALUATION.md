# Golden Dataset Evaluation

## Reference set

`data/scenarios/golden_dataset.json` contains 18 human-authored synthetic
scenarios: six `auto_draft`, six `human_review`, four in-domain
`insufficient_evidence`, and two out-of-domain questions that must also abstain.
Each scenario records its expected route, citations, review owner, forbidden
claims, tags, and rationale.

The five documents in `data/corpus/` cover direct evidence, restricted
evidence, stale evidence, ambiguity, contradiction, and missing evidence.

## Run the report

```powershell
.\.venv\Scripts\pytest.exe tests\eval -v -s
```

The report includes route accuracy, abstention recall, human-review recall,
out-of-domain recall, citation compliance, unsupported and forbidden claims,
invalid citations, mean latency, and estimated cost.

## Fidelity boundary

The current deterministic draft is extractive. Every sentence must exactly
match a sentence in a known cited excerpt after case and punctuation
normalization. Citation identifiers must exist in the corpus. This is a strict,
testable baseline, not semantic entailment detection: a future LLM paraphrase
will require a separately defined validation and evaluation policy.

Out-of-domain detection is intentionally small: a question is considered
out-of-domain when it shares no vocabulary with the synthetic corpus. The
Golden Dataset exposes the limits of this heuristic rather than presenting it
as a production classifier.
