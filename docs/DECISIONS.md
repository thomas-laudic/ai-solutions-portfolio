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
