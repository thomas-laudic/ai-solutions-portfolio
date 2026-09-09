# First vertical slice

## Purpose

This slice makes one controlled decision for a residual B2B security or
privacy question. It uses only local synthetic documents; it neither calls a
model nor sends a response to a prospect.

## Decision policy

| Evidence condition | Route | Result |
| --- | --- | --- |
| Direct, approved, current, and shareable | `auto_draft` | Sourced draft; a human still checks it before sending. |
| Direct but restricted, unapproved, or stale | `human_review` | No draft; cite the evidence and name the review owner. |
| No direct approved evidence | `insufficient_evidence` | Explicit abstention; no draft or unsupported claim. |

## Scenario set

`data/scenarios/vertical_slice.json` defines the three representative
questions. The corpus has one directly shareable security baseline and one
restricted privacy source. The absence of a source for customer-managed keys
is intentional.

## API contract

`POST /questions` accepts `{ "question": "..." }` and returns `route`,
`status`, `draft`, `evidence`, `justification`, `review_owner`,
`unsupported_claims`, `cost_usd`, and `latency_ms`. Each evidence item records
the source identifier, excerpt, and approval/current/shareability flags.

## Minimal interface

`GET /` serves a local, server-rendered demonstration over the same service and
result models as the API. It includes the three annotated examples and makes
the route, evidence, review owner, cost, latency, and human-review boundary
visible. It uses no client-side script or external asset.

## Local use on Windows

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\pytest.exe -v
.\.venv\Scripts\uvicorn.exe trustreply.app:app --app-dir src --reload
```

Open `http://127.0.0.1:8000/` for the demonstration or
`http://127.0.0.1:8000/docs` for the machine-readable API documentation.

`requirements.txt` expresses the four direct dependencies. `requirements.lock`
pins the validated complete environment for both PCs. Regenerate the lock only
after an intentional dependency change and a passing test run.

Run the Golden Dataset report separately when changing retrieval, routing, or
evidence handling:

```powershell
.\.venv\Scripts\pytest.exe tests\eval -v -s
```

See [the evaluation guide](EVALUATION.md) for metric definitions and the
current fidelity boundary.
