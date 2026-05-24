# Roadmap

Roadmap order follows `SPEC.md`. Phase statuses below mirror `SPEC.md §P`; if they diverge, treat `SPEC.md` as the source of truth.

## P0: Repo Truth Cleanup

Status: complete.

- Replace stale v1 README claims.
- Add compact spec for phased work.
- Add AGENTS guidance for follow-up agent sessions.
- Keep docs aligned with tracked files.

## P1: Prompt Pack Hardening

Status: complete.

- Normalize task input contracts (evidence rules + gaps convention added to every task prompt; T8).
- Prompt-first init onboarding flow for generating/updating `AGENTS.md` from repo evidence (`prompts/tasks/init-agent-onboarding.md`; T16).

## P2: Agent Config Exports

Status: complete.

- Copyable instructions for common local agents under `agent-configs/`.
- Configs reference prompt files; no provider-specific assumptions.

## P3: Human Docs

Status: complete.

- Manual prompt use, prompt composition, editor-agent setup, roadmap.

## P4: Skill/Plugin Distribution

Status: complete.

- Canonical skill source at `agent/codeforerunner.skill.md`.
- Codex plugin packaging (`plugins/codeforerunner/`).
- Claude plugin packaging (`.claude-plugin/`, `skills/codeforerunner/`).
- Idempotent `forerunner install <agent>` with body-parity check (SPEC V10) and managed-region markers (SPEC V12).
- Codex marketplace manifest at `plugins/codex/marketplace.json` plus `forerunner install codex --marketplace` (T24).
- CI workflow `.github/workflows/codex-marketplace-publish.yml` publishes the manifest on tagged release (T28).

## P5: Thin Runtime Wrappers

Status: complete.

- CLI (`forerunner`) with subcommands `init` / `scan` / `doc` / `check` / `mcp-server` / `install`.
- `init` accepts `--full` (prepend scan bundle) and `--agents-only` (explicit alias for the default scope).
- `check` runs drift rules when `forerunner.config.yaml` is present; silent no-op otherwise.
- `mcp-server` serves prompt bundles as MCP tools over stdio JSON-RPC; enforces scan-first per SPEC V2.
- Pre-commit hook (`.pre-commit-hooks.yaml`) + GitHub Actions workflow (`.github/workflows/forerunner-check.yml`) call `forerunner check` and no-op without the config.

## P6: Polish

Status: complete.

- `forerunner.config.yaml` schema + loader (`src/codeforerunner/config.py`); `check` honors `tasks.check.enabled_rules` and `tasks.check.ignore_paths`.
- MCP scan-first gate on `tools/call`.
- `init --full / --agents-only` flag wiring.
- Codex marketplace publishing CI.

## P7: Surface Parity

Status: complete.

- README + `docs/getting-started.md` document the post-P5/P6 surfaces (mcp-server, init flags, config schema).
- `AGENTS.md` refreshed against the current repo state.
- `forerunner doc <task>` emits a stderr warning when config is present and the task is not scan-exempt (CLI parity with the MCP V2 gate).
- `forerunner check` rules extended with R6 (Docker/Makefile), R7 (MCP), R8 (marketplace); optional actionlint smoke test for workflows.

## P8: Doc Backfill

Status: complete.

- Sweep this file and `docs/agent-distribution-design.md` for "future"/"planned" labels that no longer match current `SPEC.md` phase statuses.
- Reword the README reference to `docs/agent-distribution-design.md` so it no longer implies installer work is outstanding.

## P9: Tool Ergonomics

Status: complete.

- `forerunner --version` reports package version.
- `forerunner doctor` reports skill body parity, marketplace validation, installed destinations, config loadability, and provider API key status.
- Workflow YAML parse test catches simple CI syntax issues without requiring `actionlint`.
- `CHANGELOG.md` records release-ready surfaces.

## P10: Model Runtime

Status: complete.

- Provider abstraction under `src/codeforerunner/providers/`.
- `forerunner generate <task>` resolves a prompt bundle and calls the configured provider.
- `forerunner.config.yaml` supports per-provider `api_key_env` overrides.
- `forerunner doctor` warns when the configured provider key is missing.

## P11: Release

Status: complete.

- `.github/workflows/publish.yml` builds and publishes on `v*.*.*` tags with PyPI trusted publishing/OIDC.
- README and CHANGELOG document `pipx` / `pip` install commands for use after the first PyPI release.

## P12: MCP Example

Status: complete.

- `examples/mcp/README.md` shows Claude Desktop and mcp-cli wiring for `forerunner mcp-server`.
- `examples/mcp/claude-desktop.json` provides a copyable Claude Desktop config shape.

## P13: Drift Hardening + Streaming + GitHub Action

Status: complete.

- Inverse drift rules (RI1, RI5, RI7): fire when docs claim a feature that is absent from the repo.
- Version-pin drift rule (RV1): flags `codeforerunner==X.Y.Z` pins in docs that differ from `pyproject.toml`; skips `CHANGELOG.md`.
- `forerunner doctor --fix`: writes a starter `forerunner.config.yaml` (R1–R5, R7, R8 enabled) when none exists.
- `forerunner generate --stream`: streams output token-by-token for all four providers (Anthropic SSE, OpenAI SSE, Google `streamGenerateContent?alt=sse`, Ollama NDJSON).
- `action.yml` composite GitHub Action: `uses: derek-palmer/codeforerunner@vX.Y.Z` installs and runs `forerunner check`; no-op without `forerunner.config.yaml`.
