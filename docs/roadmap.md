# Roadmap

Roadmap order follows `SPEC.md`.

## P0: Repo Truth Cleanup

Status: complete.

- Replace stale v1 README claims.
- Add compact spec for phased work.
- Add AGENTS guidance for future OpenCode sessions.
- Keep docs aligned with tracked files.

## P1: Prompt Pack Hardening

Status: planned.

- Normalize task input contracts.
- Tighten output markers and gap handling.
- Review prompt overlap and remove duplicated rules.
- Add examples only when they improve prompt execution.
- Add prompt-first init onboarding flow for generating/updating `AGENTS.md` from repo evidence.

## P2: Agent Config Exports

Status: complete.

- Provide copyable instructions for common local agents.
- Keep configs thin and prompt-referencing.
- Avoid provider-specific assumptions.

## P3: Human Docs

Status: complete.

- Explain manual prompt use.
- Document prompt composition.
- Document editor-agent setup.
- Keep roadmap honest about current vs future surfaces.

## P4: Skill/Plugin Distribution

Status: complete.

- Canonical skill source derived from the prompt pack (`agent/codeforerunner.skill.md`).
- Codex plugin packaging for the prompt workflow.
- Claude skill/plugin packaging for the prompt workflow.
- Idempotent `forerunner install <agent>` for Codex, Claude, and generic targets, with body-parity check (SPEC V10) and managed-region markers (SPEC V12).
- Marketplace publishing for Codex remains a follow-up.

## P5: Thin Runtime Wrappers

Status: in progress.

Landed:

- CLI (`forerunner`) for resolving prompt bundles and routing to the installer (`src/codeforerunner/cli.py`).
- Pre-commit hook (`.pre-commit-hooks.yaml`) + GitHub Actions workflow (`.github/workflows/forerunner-check.yml`) that no-op without `forerunner.config.yaml`.

Still future:

- MCP server for exposing prompt workflows to agents.
- Real `forerunner check` rules (current stub exits 0; gate is presence of `forerunner.config.yaml`).
- Wiring `init`/`scan` subcommands to the prompt pack (currently honest stubs).
