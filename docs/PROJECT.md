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
and acceptance and evaluation tests. It has no external model call, persistence
layer, or client-side application.

## Current milestone

Use the Golden Dataset metrics to define the minimal audit boundary before
considering any model integration.

## Active tasks

1. Keep the Golden Dataset and deterministic decision policy covered by the
   evaluation report.
2. Define the minimal audit record from the metrics already measured, including
   its treatment of question content.
3. Specify and test a fail-closed generation boundary before adding any model
   dependency or external call.

## Success criteria

The first usable version succeeds when an interviewer can understand the user,
risk, evidence, decision, and result in under three minutes; reproduce the
demonstration locally; and inspect the supporting tests and stated limits.
