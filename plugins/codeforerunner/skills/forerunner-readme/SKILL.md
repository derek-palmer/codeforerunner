---
name: forerunner-readme
description: Generate or rewrite README.md from a repository's actual code. Use when the user wants to create, refresh, or update the README.
---

# forerunner-readme

Generates or rewrites the top-level `README.md` from verified repo evidence. Every claim must be grounded in provided files — no placeholder text, no invented content.

## Activate when

User asks to: generate a README, write the README, refresh or update README.md, create project documentation.

## Collect this context

- Scan result (run `/forerunner-scan` first)
- Existing `README.md` (when updating)
- Entry-point files (up to 5)
- Key module files (up to 10)
- Build and test configuration

## Execute

Run `forerunner doc readme` to compose the full prompt with system rules, then execute it.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/readme.md`
- `src/codeforerunner/prompts/system/base.md`
- `src/codeforerunner/prompts/partials/output-rules.md`

## Required sections

Title + one-line description · Stack table · Prerequisites · Setup (copy-pasteable) · Configuration (env vars table) · Usage · Project structure (file tree snippet)

**Conditional:** Testing (if test framework detected) · Deployment (if CI/CD present) · Architecture (link to diagrams.md if exists) · Contributing (if open-source)

## Output

Write `README.md` to repo root. For existing files, produce a minimal reviewable diff. Append `## Gaps` for anything unverifiable.
