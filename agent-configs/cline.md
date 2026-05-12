# Cline / Roo Instructions

Use this repo as prompt source for documentation tasks.

## Steps

1. Load `prompts/system/base.md` as role/instructions.
2. Read `prompts/partials/output-rules.md` and `prompts/partials/context-format.md`.
3. Collect target repo file tree plus high-value files.
4. Run `prompts/tasks/scan.md`.
5. Run exactly one downstream task prompt with scan output.

## Guardrails

- Do not run imaginary `forerunner` commands.
- Do not create broad rewrites when a focused doc update is enough.
- Preserve real paths, commands, versions, env vars, and identifiers exactly.
- If target repo evidence conflicts with README prose, trust executable/config files.
