---
name: forerunner-init
description: Bootstrap or refresh AGENTS.md and per-agent instruction overlays from repo evidence. Use when the user wants to create or update onboarding instructions for coding agents.
---

# forerunner-init

Generates or updates `AGENTS.md` (and per-agent overlays like `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/`) from direct inspection of the repo. No scan required — derives everything from file tree evidence.

## Activate when

User asks to: create AGENTS.md, update agent onboarding, refresh coding agent instructions, generate CLAUDE.md, set up agent configuration for this repo.

## Collect this context

- Full file tree (respecting `.gitignore`)
- Root manifests and lockfiles
- Entry-point files
- Existing `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/` (when updating)
- Build and test commands
- CI configuration

## Execute

Run `forerunner generate --prompt-only init-agent-onboarding` (or `forerunner init`) — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/init-agent-onboarding.md`
- `src/codeforerunner/prompts/system/base.md`

## Output

`AGENTS.md` at repo root with: project overview, build/test commands, repo structure, agent-specific guidance. Optionally produces per-agent overlays. Minimal diff when updating existing files.
