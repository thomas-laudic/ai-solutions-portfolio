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

The first local vertical slice is implemented: a small synthetic corpus, three
annotated scenarios, a Python API, and acceptance tests for each route. It has
no external model call, persistence layer, or user interface beyond local API
documentation.

## Current milestone

Complete and document the first end-to-end vertical slice before adding an
interface or any model integration.

## Active tasks

1. Keep the three-route scenario set and deterministic decision policy covered
   by acceptance tests.
2. Improve the corpus only when it supports a stated evaluation case.
3. Decide whether a minimal interface or a model integration is justified by
   the completed local slice.

## Success criteria

The first usable version succeeds when an interviewer can understand the user,
risk, evidence, decision, and result in under three minutes; reproduce the
demonstration locally; and inspect the supporting tests and stated limits.
