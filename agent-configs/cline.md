# Cline / Roo Instructions

Use this repo as prompt source for documentation tasks.

## Steps

1. Load `src/codeforerunner/prompts/system/base.md` as role/instructions (or run `forerunner doc scan` to get the fully assembled bundle).
2. Read `partials/output-rules.md` and `partials/context-format.md`.
3. Collect target repo file tree plus high-value files.
4. Run the `scan` task (`forerunner doc scan`).
5. Run exactly one downstream task prompt with scan output.

## Guardrails

- Use `forerunner doc <task>` to get assembled prompt bundles; install via `pip install codeforerunner`.
- Do not create broad rewrites when a focused doc update is enough.
- Preserve real paths, commands, versions, env vars, and identifiers exactly.
- If target repo evidence conflicts with README prose, trust executable/config files.
