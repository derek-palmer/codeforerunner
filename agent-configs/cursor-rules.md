# Cursor Rules

`codeforerunner` is prompt-first. Use the CLI (`forerunner doc <task>`) to get assembled prompt bundles, or read `src/codeforerunner/prompts/` directly from the source repo.

## Workflow

1. Apply the system prompt (`forerunner doc scan` emits it as part of the scan bundle, or read `src/codeforerunner/prompts/system/base.md`).
2. Build context using `src/codeforerunner/prompts/partials/context-format.md`.
3. Run `forerunner doc scan` (or the `scan` task directly) before any generation/check task.
4. Use the scan result as input to the selected task prompt.

## Constraints

- Prefer executable repo evidence over prose.
- Never document behavior absent from files.
- Never guess versions; use manifests, lockfiles, Dockerfiles, workflows, or IaC only.
- Put uncertainty in `## Gaps`.
- Keep output concise and Markdown-only.
