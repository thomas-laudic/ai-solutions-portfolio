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
Phase 1 (Deterministic Guardrails & Audit Engine) is ready for integration from
codex/vertical-slice into main. The showcase README and LLM boundary remain
separate delivery steps; no merge or public release is recorded yet.

## Current milestone

Integrate Phase 1 into main, then prepare its public showcase before starting
the fail-closed generation boundary.

## Active tasks

1. Keep the Golden Dataset and deterministic decision policy covered by the
   evaluation report.
2. Review and merge the Phase 1 pull request from codex/vertical-slice into main.
   Automated POST and disk checks pass; browser-based manual review remains
   available through the audit guide.
3. Create codex/github-showcase from merged main: phase-based README, Mermaid
   architecture, key-free Quickstart, measured results and explicit limitations.
4. Specify and test a fail-closed generation boundary before adding any model
   dependency or external call.

## Success criteria

The first usable version succeeds when an interviewer can understand the user,
risk, evidence, decision, and result in under three minutes; reproduce the
demonstration locally; and inspect the supporting tests and stated limits.
