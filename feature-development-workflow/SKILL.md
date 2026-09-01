---
name: feature-development-workflow
description: >-
  Standard test-first workflow for adding a new feature to a project: read
  project rules, analyze requirements and impact, locate relevant files, design
  a minimal change, write tests first, implement, run regression tests, review
  the diff, and output an implementation report. Use when adding a new feature,
  implementing a new capability, or extending project functionality.
---

# Feature Development Workflow

Follow this workflow when adding a new feature or capability to a project. The
goal is a correct, minimal, well-tested change that matches the project's
existing conventions and rules.

## Guardrails

- Stay within the requested feature's scope. Do not refactor unrelated code,
  change unrelated configuration, or add unrequested capabilities.
- This workflow does not grant extra permissions. Request approval before
  risky or externally visible actions.
- If a requirement is ambiguous, record the assumption you chose in the
  implementation report instead of guessing silently.

## Workflow

Work through the steps in order.

### 1. Read project rules

Before writing code, find and read the project's conventions and constraints:

- `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `README.md`, and any
  `.cursor/rules/`, `.cursor/skills/`, `.codex/`, or `docs/` guidance.
- Build and package config (`package.json`, `pyproject.toml`, `Makefile`,
  `Cargo.toml`, etc.) for the canonical test, lint, format, and build commands.
- Existing tests and similar features to learn established patterns.

Treat these as authoritative and note any that directly affect the feature.

### 2. Analyze requirements and impact scope

Define what "done" means and the blast radius:

- Behavior: inputs, outputs, edge cases, error handling, and acceptance
  criteria.
- Impact: which layers or modules are affected (UI, API, data model, config,
  docs, dependencies).
- Risk: migrations, backward compatibility, performance, and integration
  points.
- Assumptions: record any interpretation of the requirement that is not fully
  specified.

If scope is unclear, choose the smallest reasonable interpretation; do not
inflate scope.

### 3. Locate relevant files

Use `rg` / `rg --files` to map the change surface:

- Entry points and call sites the feature must touch.
- Existing helpers and abstractions that should be reused.
- Where tests for the affected areas live.

### 4. Design a minimal change solution

Choose the smallest change that satisfies the requirement and matches existing
patterns:

- Reuse existing helpers, types, and conventions.
- Introduce a new abstraction only when it is genuinely needed.
- Avoid rewriting or reformatting unrelated code.
- State the plan (files to change and tests to add) before editing.

### 5. Write tests first

Add or adjust test cases that capture the expected behavior before
implementing:

- Cover the happy path, edge cases, and error paths where applicable.
- Follow the project's test framework and naming conventions.
- Run the new tests and confirm they fail for the expected reason.

Tests define the contract; implementation follows them.

### 6. Implement the feature

Implement the minimal change that makes the new tests pass:

- Stay focused on the plan from step 4.
- Follow the project's style, lint, and type conventions.
- Update docs or config only when project rules require it.

### 7. Run regression tests

Run the project's relevant test suite, not only the new tests:

- Use the canonical command found in step 1.
- If the full suite is slow or impractical, run the affected modules at
  minimum and the full suite when feasible.
- Confirm the new tests pass and no existing tests regress.

### 8. Check the diff

Before finishing, review the complete diff with `git diff`:

- No unintended, unrelated, or debug changes.
- No formatting noise, leftover comments, or TODO placeholders.
- Tests cover the new behavior, with no security or performance issues.
- The change matches project conventions.

Fix anything that does not belong before continuing.

### 9. Output an implementation report

Summarize the result using the template in
[references/report-template.md](references/report-template.md): requirement and
design, files changed, tests added and run, results, assumptions, risks, and
how to verify.

## References

- [references/report-template.md](references/report-template.md) — template for
  the step 9 implementation report.
