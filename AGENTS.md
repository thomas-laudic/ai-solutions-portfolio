# AGENTS.md

## Purpose

TrustReply is a job-search portfolio project for applied AI, automation, and
AI Solutions Engineering roles. It demonstrates controlled assistance for a
residual B2B security or privacy question.

Optimize for clear, presentable work that can be completed and explained in an
interview. Build the smallest useful version.

## Context and scope

Before an important change, read:

1. `README.md`
2. `docs/PROJECT.md`
3. `docs/DECISIONS.md`

`docs/PROJECT.md` links to the detailed TrustReply context in Google Drive.
Read that source when a task affects product scope, workflow, or a material
technical decision. Do not copy its long-form documents into this repository.

The MVP boundary is defined in `docs/PROJECT.md`. Do not expand it or change
its exclusions without explicit approval.

## Working mode

- For an answer, analysis, review, or plan, inspect the relevant materials and
  report the result. Do not edit files unless the request also asks for a
  change.
- For a requested in-scope change, build, or fix, make the local changes and
  run relevant non-destructive checks.
- Ask for confirmation before adding a production dependency, deleting files,
  making an external change such as a commit or push, materially expanding the
  MVP, or restructuring a substantial part of the repository.

## Implementation rules

- Prefer the simplest maintainable solution.
- Use clear Python, explicit names, and small functions when useful.
- Keep deterministic guarantees, such as route rules and output validation, in
  code rather than delegating them blindly to a model.
- Do not create an abstraction for a single use.
- Avoid frameworks, complex agents, enterprise architecture, and unnecessary
  infrastructure.
- Never version secrets. Read local `.env` files when needed and keep
  `.env.example` free of secret values.

## Verification and reporting

- Run available tests, linting, and relevant checks after changes.
- Add proportionate verification when adding code: a test, example, or
  documented manual check.
- Report changed files, checks run, limitations, and material risks.
