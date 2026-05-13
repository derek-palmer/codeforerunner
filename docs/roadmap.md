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

Status: planned.

- Add a canonical skill source derived from the prompt pack.
- Add Codex plugin packaging for the prompt workflow.
- Add Claude skill/plugin packaging for the prompt workflow.
- Add an idempotent installer for owned agent artifacts.
- Keep packages thin: they should route agents to tracked prompts and docs, not duplicate product logic.
- Do not claim package install support until files exist.

## P5: Thin Runtime Wrappers

Status: planned.

Potential surfaces:

- CLI for assembling context and running tasks.
- MCP server for exposing prompt workflows to agents.
- Pre-commit hook for doc staleness checks.
- CI workflow for documentation drift reporting.

Do not add these until prompt contracts are stable enough to wrap.
