# Implementation Decisions

## 2026-08-19: Context ownership and TrustReply scope

- Google Drive is the source of truth for TrustReply's long-form product,
  workflow, market, and career context.
- This repository is the source of truth for code, tests, synthetic data,
  configuration, and concise implementation documentation.
- Long-form Drive documents are linked from `docs/PROJECT.md`, not duplicated
  in Git.
- TrustReply is a controlled-assistance prototype for one residual B2B security
  or privacy question, not a questionnaire platform or compliance product.
- The MVP decision routes are `auto_draft`, `human_review`, and
  `insufficient_evidence`.

These decisions keep the project portable across local clones while avoiding
duplicate strategic documentation and premature product scope.

## 2026-09-09: First vertical slice and reproducible local environment

- The first slice uses a deterministic local policy over synthetic documents;
  it does not call an LLM or any external service.
- The three routes are demonstrated by `auto_draft`, restricted-evidence
  `human_review`, and `insufficient_evidence` scenarios.
- `requirements.txt` remains the small direct-dependency manifest.
  `requirements.lock` pins the complete environment validated on Python 3.12.7
  for reproducible installation on both PCs.
- A human still reviews any draft before sending it. A restricted source never
  produces a direct draft.

## 2026-09-09: Minimal interface before audit or model integration

- The first user interface is a server-rendered FastAPI page over the existing
  deterministic service and result models.
- It adds no frontend framework, client-side script, or production dependency.
- It exposes the three annotated examples and displays the decision, evidence,
  review owner, cost, latency, and human-review limitation.
- The API remains the machine-readable contract. Presentation logic does not
  make routing decisions.

## 2026-09-09: Golden Dataset before audit implementation

- Audit fields will be driven by evaluation needs rather than collected in
  advance without a metric.
- The reference set contains 18 scenarios across direct evidence, restricted,
  stale, ambiguous, contradictory, missing-evidence, and out-of-domain cases.
- The first fidelity check is deliberately extractive: every draft sentence
  must match a known cited excerpt, and every citation identifier must exist.
- Route accuracy, abstention and review recall, out-of-domain recall, citation
  compliance, unsupported claims, latency, and cost form the initial report.

## 2026-09-11: Minimal synchronous decision audit

- Emit one validated JSONL event per completed evaluation via a dedicated
  audit module and injectable sink; keep filesystem operations out of the
  deterministic service. The service supplies decision facts from the same
  corpus snapshot and lexical scores used for routing.
- Record trace/event IDs, UTC time, schema/policy/corpus versions, route,
  reason codes, evidence IDs, fidelity counts, processing latency and cost.
  Expected labels and forbidden-claim checks remain in the Golden Dataset runner.
- Pseudonymize questions with HMAC-SHA-256; never persist questions, drafts,
  excerpts or exception content. Use TRUSTREPLY_AUDIT_HMAC_KEY when configured,
  otherwise a random process-local key. No key manager or rotation mechanism.
- Write synchronously to logs/audit.jsonl, excluded from Git. A shared sink
  serializes threads in one process. Transport errors preserve the decision
  and emit a content-free error with the trace ID to operational logging.
  No queue, multi-worker guarantee, automatic retention or immutable storage.
- Submit both the web form and example buttons through POST, avoiding question
  content in generated URLs. Parse the single URL-encoded field with the
  standard library; no dependency is added. Return X-Trace-ID and no-store
  response headers and show the trace identifier on the result page.
- Keep the highest-scoring candidate's criteria even below threshold, so an
  abstention is explainable; citation_ids remains empty when none is selected.
  A sorted corpus traversal makes lexical ties reproducible between machines.
