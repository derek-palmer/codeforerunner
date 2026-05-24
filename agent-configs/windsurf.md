# Windsurf Instructions

Use `codeforerunner` prompts to produce repo-grounded documentation.

## Prompt Stack

- System: `src/codeforerunner/prompts/system/base.md` (or `forerunner doc scan` for the assembled bundle)
- Shared rules: `src/codeforerunner/prompts/partials/`
- First task: `forerunner doc scan`
- Downstream tasks: `forerunner doc <task>`

## Required Behavior

- Scan first, then generate/check/review.
- Use only facts visible in provided files.
- Keep docs concise and developer-facing.
- Emit Markdown with fenced code language tags.
- Mark missing evidence in `## Gaps`.

## Current Repo Boundary

`forerunner` CLI, MCP server, pre-commit hook, CI, and PyPI package are all live. Docker image and Makefile are not present.
