---
name: forerunner-check
description: Check whether existing documentation is stale relative to the current codebase. Use when the user wants to detect doc drift before a commit, PR, or release.
---

# forerunner-check

Evaluates documentation staleness against a fresh scan. Classifies each doc section as CURRENT, STALE, MISSING, or UNVERIFIABLE. Designed for pre-commit hooks, CI gates, and on-demand runs.

## Activate when

User asks to: check docs, detect stale documentation, verify README accuracy, find doc drift, validate docs before a PR/release. Also triggers when `forerunner check` exits non-zero.

## Collect this context

- Scan result — run fresh, not cached (run `/forerunner-scan` first)
- Existing documentation files: `README.md`, `docs/*.md`
- `.forerunner/state.json` (last-run checksums, if present)
- Git diff of changed files (for pre-commit mode)

## Execute

Run `forerunner generate --prompt-only check` — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, also available as `forerunner check` (automated rule-based drift detection using `forerunner.config.yaml`).

Get the manual-agent prompt from:
- `src/codeforerunner/prompts/tasks/check.md`
- `src/codeforerunner/prompts/system/base.md`

## What to check

README accuracy · API docs accuracy · Diagram accuracy · Version audit currency (stale after 30 days) · Undocumented new modules · Docs referencing removed files

## Output

Staleness report with file-level classification. STALE findings include specific mismatch descriptions. Write to stdout or `.forerunner/check-report.md`. Exit non-zero when STALE or MISSING findings exceed threshold.
