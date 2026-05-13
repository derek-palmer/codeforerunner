# AGENTS.md

## Repo State

- This repo is in the `v2-overhaul` prompt-first transition; read `codeforerunner_v2_handoff.md` before trusting README claims.
- Treat prompts as the core product: `prompts/system/base.md`, `prompts/partials/`, and `prompts/tasks/`.
- `README.md`, `SPEC.md`, `docs/`, and `agent-configs/` should stay aligned; update the spec when phase/task scope changes.
- Do not reintroduce the old analyzer-heavy architecture unless explicitly requested.

## Current Sources Of Truth

- `prompts/system/base.md` defines the base behavior and quality bar.
- `prompts/tasks/scan.md` is the first task in every intended run; downstream task prompts expect its output.
- `forerunner.config.yaml.example` is example config only; there is no implemented loader or CLI in this branch.
- `SPEC.md` tracks phased work via invariants and task rows; prefer status edits over broad rewrites.
- There is no `src/`, tests, package manifest, Dockerfile, Makefile, hooks, or CI workflow in this branch.

## Work Direction

- Keep the MVP prompt-first and lightweight: prompts, docs, editor-agent config scaffolds, and honest roadmap text.
- Do not claim working CLI, MCP, package publishing, Docker, pre-commit hooks, or CI unless corresponding files are actually added.
- Use names consistently: repo/product `codeforerunner`, short CLI/config name `forerunner`, example config `forerunner.config.yaml`.
- If adding legacy-style files such as `src/`, `tests/`, `Dockerfile`, `Makefile`, `pyproject.toml`, or `uv.lock`, make them directly support the prompt-first strategy.
- Keep `docs/roadmap.md` and `SPEC.md` honest about current vs future surfaces.

## Verification

- There are currently no repo-defined build, lint, typecheck, test, or format commands.
- For doc/prompt changes, verify by reading affected Markdown for consistency with the handoff and checking that claims match tracked files.
