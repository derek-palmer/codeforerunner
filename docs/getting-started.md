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
forerunner scan                     # shortcut for `forerunner doc scan`
forerunner init                     # resolves init-agent-onboarding bundle (alias of --agents-only)
forerunner init --agents-only       # explicit: AGENTS.md onboarding bundle only
forerunner init --full              # prepends the scan bundle before onboarding (scan-first per SPEC V2)
forerunner install codex --check    # dry-run the skill installer for Codex target
forerunner install claude           # idempotent write into ~/.claude/plugins/...
forerunner check                    # hook entry point; silent no-op without forerunner.config.yaml
forerunner mcp-server               # serve prompt bundles as MCP tools over stdio JSON-RPC
```

## Configuration

Copy `forerunner.config.yaml.example` to `forerunner.config.yaml` at the repo root to opt in. When the file is absent, `forerunner check` exits 0 silently and the pre-commit/CI hooks do nothing. The schema has these groups:

- Provider/model fields: `provider`, `model`, `api_key_env`, `output_dir`, `context_max_files`, `context_max_lines_per_file`, `approaching_eol_threshold_months`.
- `ignore_patterns`: list of glob patterns.
- `tasks.version_audit`: `enabled`, `stale_after_days`, `fetch_live_eol_data`.
- `tasks.check`: `block_on` / `warn_on` severity lists, `enabled_rules` (allowlist of rule IDs; omit for all), and `ignore_paths` (fnmatch globs of docs to skip).

Invalid YAML, unknown providers, unknown `api_key_env` providers, or unknown severity levels surface as a `ConfigError` and `forerunner check` exits non-zero.

## What Not To Do

- Do not assume Docker, Make, or a published PyPI release exists yet.
- Do not accept generated docs until claims match target repo files.

## Next References

- Prompt composition: `docs/prompt-guide.md`
- Editor setup: `docs/editor-agent-setup.md`
- Phase tracker: `SPEC.md`
