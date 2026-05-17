# Getting Started

`codeforerunner` ships prompts as the core product, plus a thin `forerunner` CLI, an idempotent skill installer, and pre-commit/CI hook wiring. Use the prompts directly with your editor/agent, or use the CLI to assemble bundles.

## Install The CLI (optional)

```bash
python -m pip install -e .
forerunner --help
```

The CLI is a thin orchestration layer; product logic lives in `prompts/`.

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

## Use The CLI

```bash
forerunner doc scan                 # prints base + partials + tasks/scan.md to stdout
forerunner install codex --check    # dry-run the skill installer for Codex target
forerunner install claude           # idempotent write into ~/.claude/plugins/...
forerunner check                    # hook entry point; no-op without forerunner.config.yaml
```

`init` and `scan` subcommands are honest stubs (exit 2) until the orchestration is wired.

## What Not To Do

- Do not assume Docker, Make, or a published package exists yet.
- Do not assume an MCP server exists; it is still future.
- Do not accept generated docs until claims match target repo files.

## Next References

- Prompt composition: `docs/prompt-guide.md`
- Editor setup: `docs/editor-agent-setup.md`
- Phase tracker: `SPEC.md`
