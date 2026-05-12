# Roadmap

Roadmap order follows `codeforerunner_spec.md`.

## P0: Repo Truth Cleanup

Status: in progress.

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

Status: in progress.

- Provide copyable instructions for common local agents.
- Keep configs thin and prompt-referencing.
- Avoid provider-specific assumptions.

## P3: Human Docs

Status: in progress.

- Explain manual prompt use.
- Document prompt composition.
- Document editor-agent setup.
- Keep roadmap honest about current vs future surfaces.

## P4: Thin Runtime Wrappers

Status: future.

Potential surfaces:

- CLI for assembling context and running tasks.
- MCP server for exposing prompt workflows to agents.
- Pre-commit hook for doc staleness checks.
- CI workflow for documentation drift reporting.

Do not add these until prompt contracts are stable enough to wrap.
