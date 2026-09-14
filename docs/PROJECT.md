# TrustReply Project Brief

## Objective

Build a small, reproducible portfolio prototype for AI Solutions Engineer, AI
Integration Engineer, and related applied-AI roles. It demonstrates controlled
assistance for one residual B2B security or privacy question received by a
Sales Engineer after the Trust Center and public documentation have not fully
resolved it.

## Detailed product context

The detailed business research, workflow mapping, portfolio framing, and
market analysis are maintained in Google Drive:
[TrustReply portfolio context](https://drive.google.com/drive/folders/1qAhrxY1NV6Y-uHIFjYqIbPuzNIbr2wto).

Google Drive is the source of truth for that long-form context. This document
contains only the operational summary needed to build the repository.

## MVP boundary

Input: one question and a small approved synthetic corpus.

Processing: retrieve relevant evidence, assess its coverage and risk, then
apply an explicit decision policy.

Output: a structured result with cited excerpts, a justification, a status,
the relevant review owner when needed, and basic cost and latency data.

Routes:

- `auto_draft`: direct, approved, current evidence for a standard question;
- `human_review`: ambiguity, sensitivity, contradiction, or restricted source;
- `insufficient_evidence`: no direct evidence supports a safe response.

The first version must evaluate route selection, citations, and unsupported
claims using a small annotated scenario set.

## Explicit exclusions

- Full questionnaires, OCR, and enterprise connectors.
- Authentication, collaboration workflows, and a Trust Center.
- Legal or compliance advice, real security guarantees, and automatic sending.
- Multi-agent systems, fine-tuning, MLOps, complex cloud infrastructure, and
  a multi-model router.

## Current state

The first local vertical slice is implemented: five synthetic documents, an
18-scenario Golden Dataset, a Python API, a minimal server-rendered interface,
and acceptance and evaluation tests. A synchronous JSONL decision audit is now
connected to the API and POST web form, with HMAC question fingerprints and
fail-open transport. Tests use memory collectors or temporary files.
The 2026-09-14 validation passed all 27 tests and all 18 Golden Dataset scenarios
(100% routing/recall/citations; zero unsupported, invalid or forbidden claims).
It has no external model call, database, or client-side application.
See [the audit guide](AUDIT.md) for local configuration and known limits.
Phase 1 (Deterministic Guardrails & Audit Engine) was merged into main through
PR #1, merge commit aa0d016. The phase-based showcase README is prepared on
codex/github-showcase, created from that merged main. Phase 2 is in design;
no LLM integration is implemented. Linux Quickstart commands are documented
but have not yet been verified on Linux.

## Current milestone

Review and publish the Phase 1 showcase before implementing the fail-closed
generation boundary.

## Active tasks

1. Keep the Golden Dataset and deterministic decision policy covered by the
   evaluation report.
2. Review the README on codex/github-showcase, then commit and publish when
   requested. It includes Mermaid, platform-specific Quickstarts and limits.
3. Specify and test a fail-closed generation boundary before adding any model
   dependency or external call.
4. Phase 3: evaluate hybrid retrieval with an expanded reference set after
   Phase 2; choose dependencies and implementation scope separately.

## Success criteria

The first usable version succeeds when an interviewer can understand the user,
risk, evidence, decision, and result in under three minutes; reproduce the
demonstration locally; and inspect the supporting tests and stated limits.
