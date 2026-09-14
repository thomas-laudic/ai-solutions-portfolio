# TrustReply

TrustReply is a portfolio prototype for controlled assistance with residual B2B
security and privacy questions. It helps a Sales Engineer find approved
evidence, prepare a sourced response when appropriate, and make uncertainty
visible when a human expert must review the case or evidence is missing.

## Why it matters

A plausible but unsupported answer can create a commercial commitment, slow a
deal, or disclose information at the wrong level. The project focuses on the
decision around a response, not on generating text alone.

## MVP

For one question at a time, the prototype will:

- search a small approved synthetic corpus;
- return a structured result with evidence, justification, status, review
  owner, cost, and latency;
- choose one route: `auto_draft`, `human_review`, or
  `insufficient_evidence`;
- evaluate routing, citations, and unsupported-claim behavior against a small
  annotated set.

The final prototype will use four to five synthetic documents and roughly 15
to 20 annotated questions. A human remains responsible for review and sending
any response.

## Out of scope

TrustReply is not a full security questionnaire platform, Trust Center,
compliance product, legal advisor, multi-user application, or multi-agent
system. It will not send responses automatically or claim real-world security
or compliance guarantees.

## Status

The first local vertical slice is implemented. Its minimal web interface routes
three representative synthetic scenarios to `auto_draft`, `human_review`, or
`insufficient_evidence`, with acceptance tests for each route and presentation.
See the [vertical-slice guide](docs/VERTICAL_SLICE.md) for the API contract, run
commands, and stated limits. A separate [evaluation guide](docs/EVALUATION.md)
documents the 18-scenario Golden Dataset and its metrics.
The [local audit guide](docs/AUDIT.md) covers synchronous JSONL events, HMAC
pseudonymization, POST submissions and local troubleshooting.

See [the operational project brief](docs/PROJECT.md) and
[implementation decisions](docs/DECISIONS.md) for the current state.

## Repository layout

```text
docs/   Current scope and durable implementation decisions
src/    Application code
tests/  Automated checks
```
