---
name: forerunner-review
description: Summarize documentation impact of pending changes for reviewer approval. Use when the user wants a doc-impact review before merging a PR.
---

# forerunner-review

Produces a human-readable summary of documentation impact for a pending change. Tells reviewers: which docs are affected, what's now stale, what needs updating before merge.

## Activate when

User asks to: review docs impact, summarize documentation changes, check what docs need updating for this PR, generate a doc review summary.

## Collect this context

- Check report from `.forerunner/check-report.md` (or run `/forerunner-check` first)
- Git diff of staged or PR files (`git diff --staged` or `git diff main...HEAD`)
- Existing documentation files affected by the diff

## Execute

Run `forerunner generate --prompt-only review` — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/review.md`
- `src/codeforerunner/prompts/system/base.md`

## Output

Review summary with: list of affected docs, staleness classification per doc, recommended actions (update / skip / flag for later), and an overall merge-readiness verdict. Formatted for inclusion in a PR description or review comment.
