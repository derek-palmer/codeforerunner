# AGENTS.md

<!-- output: AGENTS.md -->

## Repo State

- Prompt-first product wrapped by a thin Python CLI, an idempotent skill installer, pre-commit + CI hooks, an MCP server, a typed config loader, a composite GitHub Action, and four provider adapters. Work items are tracked as GitHub Issues in `derek-palmer/codeforerunner`.
- Core product = Markdown prompts in `src/codeforerunner/prompts/` (bundled in the pip package; retrieve via `forerunner doc <task>`). Wrappers stay thin (C1); product logic lives in prompts.
- `src/codeforerunner/` exposes the `forerunner` console script with subcommands `init`, `scan`, `doc`, `check`, `generate`, `doctor`, `mcp-server`, `install`.
- Agent distribution: canonical skill at `agent/codeforerunner.skill.md`; downstream copies in `plugins/codeforerunner/skills/codeforerunner/SKILL.md` and `skills/codeforerunner/SKILL.md` must preserve post-frontmatter body verbatim (V10).
- Hooks: `.pre-commit-hooks.yaml`, `.github/workflows/forerunner-check.yml`, `.github/workflows/codex-marketplace-publish.yml`. All gate on `forerunner.config.yaml` presence (silent no-op when absent).
- `action.yml` composite GitHub Action: `uses: derek-palmer/codeforerunner@vX.Y.Z` installs and runs `forerunner check`; no-op without `forerunner.config.yaml`.
- Four provider adapters in `src/codeforerunner/providers/`: `anthropic`, `openai`, `google`, `ollama`. All implement `generate()` and `stream()` from `base.py` Protocol. Provider selection via `forerunner.config.yaml` (`provider`, `model`, `api_key_env` fields).

## Current Sources Of Truth

- `src/codeforerunner/prompts/system/base.md` for base behavior and quality bar (or `forerunner doc scan` for the assembled bundle).
- `src/codeforerunner/prompts/tasks/scan.md` for the first task in every doc-generation flow (V2 scan-first; MCP `tools/call` enforces this gate; CLI blocks non-exempt tasks when `forerunner.config.yaml` is present and neither `.forerunner/scan.md` nor `FORERUNNER_SCAN_DONE=1` is found; `forerunner scan` prints a hint to write `.forerunner/scan.md`).
- `forerunner.config.yaml.example` documents the schema parsed by `src/codeforerunner/config.py` (provider/model fields, `ignore_patterns`, `tasks.check`, `tasks.version_audit`).
- `agent/codeforerunner.skill.md` for the canonical skill; do not let `plugins/...` or `skills/...` SKILL.md bodies drift from it.

## High-Value Commands

- `python -m pip install -e .` — editable install of the CLI (PyYAML is the only runtime dep).
- `.venv/bin/pytest -q` — run the full test suite from repo root.
- `.venv/bin/forerunner doc <task>` — emit a resolved prompt bundle (base + partials + task) to stdout.
- `.venv/bin/forerunner init [--full | --agents-only]` — emit the agent-onboarding bundle (with optional scan prepended).
- `.venv/bin/forerunner mcp-server` — serve prompt bundles as MCP tools over stdio JSON-RPC; `tools/call` for non-exempt tasks requires a prior `scan` call.
- `.venv/bin/forerunner check` — run drift rules against tracked docs when `forerunner.config.yaml` is present.
- `.venv/bin/forerunner generate <task> [--stream]` — resolve bundle and call configured provider; stream output token-by-token with `--stream`.
- `.venv/bin/forerunner doctor [--fix]` — health report; `--fix` writes starter `forerunner.config.yaml` if absent.
- `.venv/bin/forerunner install <codex|claude|generic> [--check] [--marketplace]` — idempotent skill or marketplace install with body-parity check (V10) and managed-region markers (V12). `generic` requires `--path <dest>`.
- `.venv/bin/python scripts/validate_skill_copies.py` — verify SKILL.md body parity.
- `.venv/bin/python scripts/validate_codex_marketplace.py` — verify the Codex marketplace manifest.

## Structural Notes

- The CLI is intentionally orchestration-only; resolution logic lives in `cmd_doc` and is reused by `cmd_init`, `cmd_scan`, and the MCP server's `resolve_bundle` helper.
- `forerunner check` rules live in `src/codeforerunner/check.py` (`_RULES`). Adding a rule = appending a `_Rule` dataclass instance; the loader respects `tasks.check.enabled_rules` allowlists and `tasks.check.ignore_paths` globs. Inverse rules (`invert=True`) fire when the trigger file is absent.
- Version-pin drift rule (`RV1`) flags `codeforerunner==X.Y.Z` pins in docs that differ from `pyproject.toml`; skips `CHANGELOG.md`.
- MCP state (`scan_called`) is seeded at startup from `.forerunner/scan.md` (relative to cwd / `repo_root`); if the artifact is present the gate is pre-satisfied for the lifetime of that process. Without the artifact, the gate resets on every new subprocess.
- The installer refuses to overwrite a destination that exists without managed markers (V12) — surface this clearly when an install path aborts.
- Provider adapters are stdlib-only (no SDK deps); they use `urllib.request` with SSE parsing for Anthropic/OpenAI/Google and NDJSON for Ollama. Adding a provider = new file in `providers/` implementing the `base.py` Protocol.

## Non-Obvious Constraints

- Never claim a surface exists in docs before the backing file is tracked (V1, V3, V4, V5, V11). `forerunner check` flags contradiction drift (docs deny a surface that exists) and inverse drift (docs claim a surface that is absent), plus version-pin drift (RV1).
- Per V10, downstream SKILL.md bodies must remain byte-identical to the canonical (post-frontmatter). Frontmatter may vary per agent.
- Per V12, the installer must be re-run safe and overlay-safe; do not regress the "skip when hash matches" or "preserve content outside markers" branches.
- The MCP server is stdlib-only and uses line-delimited JSON-RPC 2.0; no `mcp` package dependency.
- Names: product `codeforerunner`, CLI/config short name `forerunner`, example config `forerunner.config.yaml`.
- Drift rules trigger on exact regex phrases. When documenting the rules themselves (e.g. in README tables), use paraphrase language ("doc denies having a CLI") rather than the exact trigger phrases to avoid self-referential false positives.

## Verification Expectations

- Code changes: run `.venv/bin/pytest -q`; confirm green before closing the relevant GitHub Issue.
- Skill source changes: also run `.venv/bin/python scripts/validate_skill_copies.py`.
- Marketplace manifest changes: also run `.venv/bin/python scripts/validate_codex_marketplace.py`.
- Doc/prompt-only changes: re-read affected Markdown; run `forerunner check` (with a temporary `forerunner.config.yaml`) to catch claim-vs-file drift.

## Agent skills

### Issue tracker

GitHub Issues in `derek-palmer/codeforerunner`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) applied as GitHub issue labels. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.
