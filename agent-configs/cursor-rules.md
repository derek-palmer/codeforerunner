# Cursor Rules

`codeforerunner` is prompt-first. Use tracked prompts directly; do not assume a CLI or package exists.

## Workflow

1. Apply `prompts/system/base.md` as the documentation agent role.
2. Build context with `prompts/partials/context-format.md`.
3. Run `prompts/tasks/scan.md` before any generation/check task.
4. Use the scan result as input to the selected task prompt.

## Constraints

- Prefer executable repo evidence over prose.
- Never document behavior absent from files.
- Never guess versions; use manifests, lockfiles, Dockerfiles, workflows, or IaC only.
- Put uncertainty in `## Gaps`.
- Keep output concise and Markdown-only.
