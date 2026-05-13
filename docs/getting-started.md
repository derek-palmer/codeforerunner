# Getting Started

`codeforerunner` currently ships prompts, not a runnable CLI.

## Use Manually

1. Put `prompts/system/base.md` in your agent's system or project instructions.
2. Read `prompts/partials/context-format.md` for context shape.
3. Gather target repo file tree plus relevant config, manifest, entrypoint, and docs files.
4. Run `prompts/tasks/scan.md` first.
5. Feed the scan result into one downstream task prompt.

## Example Flow

```text
base.md + context-format.md + target repo context + scan.md
→ scan result
→ readme.md or stack-docs.md or check.md
→ Markdown output
```

## What To Include In Context

- Full file tree, respecting ignore rules.
- Root manifests and lockfiles.
- Build/test/lint config.
- Entry points and key modules.
- Existing docs when updating or checking documentation.

## What Not To Do

- Do not run `forerunner`; no CLI exists yet.
- Do not assume Docker, Make, pre-commit, CI, or package publishing exists.
- Do not accept generated docs until claims match target repo files.

## Next References

- Prompt composition: `docs/prompt-guide.md`
- Editor setup: `docs/editor-agent-setup.md`
- Phase tracker: `SPEC.md`
