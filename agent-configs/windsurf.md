# Windsurf Instructions

Use `codeforerunner` prompts to produce repo-grounded documentation.

## Prompt Stack

- System: `prompts/system/base.md`
- Shared rules: `prompts/partials/`
- First task: `prompts/tasks/scan.md`
- Downstream tasks: `prompts/tasks/*.md`

## Required Behavior

- Scan first, then generate/check/review.
- Use only facts visible in provided files.
- Keep docs concise and developer-facing.
- Emit Markdown with fenced code language tags.
- Mark missing evidence in `## Gaps`.

## Current Repo Boundary

There is no implemented runtime wrapper yet. Treat CLI, MCP, hooks, and CI as roadmap surfaces unless corresponding files are added.
