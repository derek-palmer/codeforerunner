# Getting Started

`codeforerunner` ships a prompt pack as the core product, wrapped by a `forerunner` CLI, MCP server, pre-commit/CI hook wiring, and a PyPI package. Use the CLI to assemble bundles and serve prompts over MCP — or use the prompts manually with your editor/agent.

## Install

```bash
pipx install codeforerunner   # recommended — isolated environment
pip install codeforerunner    # alternative
forerunner --help
```

From source:

```bash
git clone https://github.com/derek-palmer/codeforerunner
cd codeforerunner
python -m pip install -e .
```

## Use Manually

Prompts are in `src/codeforerunner/prompts/` (source) or retrieved via `forerunner doc <task>`.

1. Put `system/base.md` in your agent's system or project instructions.
2. Read `partials/context-format.md` for context shape.
3. Gather target repo file tree plus relevant config, manifest, entrypoint, and docs files.
4. Run `tasks/scan.md` first.
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
forerunner init                     # resolves init-agent-onboarding bundle
forerunner init --agents-only       # explicit: AGENTS.md onboarding bundle only
forerunner init --full              # prepends scan bundle before onboarding (scan-first per SPEC V2)
forerunner refresh                  # output scan + check + all doc-task bundles in sequence
forerunner doctor                   # health report: skill parity, config
forerunner doctor --fix             # write starter forerunner.config.yaml if absent
forerunner install codex --check    # dry-run the skill installer for Codex target
forerunner install claude           # idempotent write into ~/.claude/plugins/...
forerunner check                    # run drift rules; silent no-op without forerunner.config.yaml
forerunner mcp-server               # serve prompt bundles as MCP tools over stdio JSON-RPC
```

## Configuration

Generate a starter config:

```bash
forerunner doctor --fix
```

Or copy `forerunner.config.yaml.example` to `forerunner.config.yaml` at the repo root. When the file is absent, `forerunner check` exits 0 silently and the pre-commit/CI hooks do nothing. The schema has these groups:

- `approaching_eol_threshold_months`: integer (default 6).
- `ignore_patterns`: list of glob patterns.
- `tasks.version_audit`: `enabled`, `stale_after_days`, `fetch_live_eol_data`.
- `tasks.check`: `block_on` / `warn_on` severity lists, `enabled_rules` (allowlist of rule IDs; omit for all), and `ignore_paths` (fnmatch globs of docs to skip).

Invalid YAML or unknown severity levels surface as a `ConfigError` and `forerunner check` exits non-zero.

## What Not To Do

- Do not assume Docker or a Makefile exists in this repo.
- Do not accept generated docs until claims match target repo files.

## Next References

- Prompt composition: `docs/prompt-guide.md`
- Editor setup: `docs/editor-agent-setup.md`
- Issue tracker: `github.com/derek-palmer/codeforerunner/issues`
