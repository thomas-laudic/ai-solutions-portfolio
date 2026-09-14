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

The runner also validates one memory audit event per scenario: route, domain,
citations, review owner, reason codes, draft presence, fidelity counts and
performance fields. Scenario IDs are supplied internally, never by HTTP clients.
The report's labels and forbidden-claim checks remain evaluation-only.
Latency is service processing time, including decision metadata preparation,
but excluding event construction, HMAC and synchronous disk writes.

Run all acceptance, audit and evaluation tests with:

```powershell
.\.venv\Scripts\pytest.exe tests/ tests/eval -v -s
```

HTTP tests override the sink with a memory collector. Disk tests use tmp_path;
pytest does not create the application's logs/audit.jsonl.

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
