# AGENTS.md

## Repo State

- Prompt-first product wrapped by a thin Python CLI, an idempotent skill installer, pre-commit + CI hooks, an MCP server, and a typed config loader. `SPEC.md` is the source of truth for phases, invariants (§V), interfaces (§I), and tasks (§T).
- Core product = Markdown prompts in `prompts/system/`, `prompts/partials/`, `prompts/tasks/`. Wrappers stay thin (C1); product logic lives in prompts.
- `src/codeforerunner/` exposes the `forerunner` console script with subcommands `init`, `scan`, `doc`, `check`, `mcp-server`, `install`.
- Agent distribution: canonical skill at `agent/codeforerunner.skill.md`; downstream copies in `plugins/codeforerunner/skills/codeforerunner/SKILL.md` and `skills/codeforerunner/SKILL.md` must preserve post-frontmatter body verbatim (V10).
- Hooks: `.pre-commit-hooks.yaml`, `.github/workflows/forerunner-check.yml`, `.github/workflows/codex-marketplace-publish.yml`. All gate on `forerunner.config.yaml` presence (silent no-op when absent).

## Current Sources Of Truth

- `SPEC.md` for phase/task/invariant tracking. Status edits are preferred to broad rewrites; flip rows via the spec skill, not freehand.
- `prompts/system/base.md` for base behavior and quality bar.
- `prompts/tasks/scan.md` for the first task in every doc-generation flow (V2 scan-first; MCP `tools/call` enforces this gate; CLI emits a stderr warning when `forerunner.config.yaml` is present and `FORERUNNER_SCAN_DONE` is not set).
- `forerunner.config.yaml.example` documents the schema parsed by `src/codeforerunner/config.py` (provider/model fields, `ignore_patterns`, `tasks.check`, `tasks.version_audit`).
- `agent/codeforerunner.skill.md` for the canonical skill; do not let `plugins/...` or `skills/...` SKILL.md bodies drift from it.

## High-Value Commands

- `python -m pip install -e .` — editable install of the CLI (PyYAML is the only runtime dep).
- `.venv/bin/pytest -q` — run the full test suite from repo root.
- `.venv/bin/forerunner doc <task>` — emit a resolved prompt bundle (base + partials + task) to stdout.
- `.venv/bin/forerunner init [--full | --agents-only]` — emit the agent-onboarding bundle (with optional scan prepended).
- `.venv/bin/forerunner mcp-server` — serve prompt bundles as MCP tools over stdio JSON-RPC; `tools/call` for non-exempt tasks requires a prior `scan` call.
- `.venv/bin/forerunner check` — run drift rules against tracked docs when `forerunner.config.yaml` is present.
- `.venv/bin/forerunner install <codex|claude|generic> [--check] [--marketplace]` — idempotent skill or marketplace install with body-parity check (V10) and managed-region markers (V12).
- `.venv/bin/python scripts/validate_skill_copies.py` — verify SKILL.md body parity.
- `.venv/bin/python scripts/validate_codex_marketplace.py` — verify the Codex marketplace manifest.

## Structural Notes

- The CLI is intentionally orchestration-only; resolution logic lives in `cmd_doc` and is reused by `cmd_init`, `cmd_scan`, and the MCP server's `resolve_bundle` helper.
- `forerunner check` rules live in `src/codeforerunner/check.py` (`_RULES`). Adding a rule = appending one tuple; the loader respects `tasks.check.enabled_rules` allowlists and `tasks.check.ignore_paths` globs.
- MCP state (`scan_called`) is per-process; the gate resets on every new subprocess.
- The installer refuses to overwrite a destination that exists without managed markers (V12) — surface this clearly when an install path aborts.

## Non-Obvious Constraints

- Never claim a surface exists in docs before the backing file is tracked (V1, V3, V4, V5, V11). `forerunner check` flags the inverse (docs claiming a surface is absent when its file exists).
- Per V10, downstream SKILL.md bodies must remain byte-identical to the canonical (post-frontmatter). Frontmatter may vary per agent.
- Per V12, the installer must be re-run safe and overlay-safe; do not regress the "skip when hash matches" or "preserve content outside markers" branches.
- The MCP server is stdlib-only and uses line-delimited JSON-RPC 2.0; no `mcp` package dependency.
- Names: product `codeforerunner`, CLI/config short name `forerunner`, example config `forerunner.config.yaml`.

## Verification Expectations

- Code changes: run `.venv/bin/pytest -q`; confirm green before flipping a §T row to `x`.
- Skill source changes: also run `.venv/bin/python scripts/validate_skill_copies.py`.
- Marketplace manifest changes: also run `.venv/bin/python scripts/validate_codex_marketplace.py`.
- Doc/prompt-only changes: re-read affected Markdown for consistency with `SPEC.md`; run `forerunner check` (with a temporary `forerunner.config.yaml`) to catch claim-vs-file drift.

## Agent skills

### Issue tracker

Local markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`), applied via a `Status:` line in each issue file. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.
