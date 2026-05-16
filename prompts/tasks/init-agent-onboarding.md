# Task: Init Agent Onboarding

Generates or updates repo onboarding instructions for coding agents.
Prompt-first workflow for manual use today; future wrappers may orchestrate it.

## Input

- File tree (full)
- Highest-value config/manifests/lockfiles/workflows
- Existing instruction files if present:
  - `AGENTS.md`
  - `CLAUDE.md`, `.cursor/rules/*`, `.cursorrules`, `.github/copilot-instructions.md`, `opencode.json`
- Key docs describing current state (`README.md`, `SPEC.md`, handoff/roadmap docs)
- Optional prior scan result from `prompts/tasks/scan.md`

## Objectives

1. Build or refine `AGENTS.md` so future agent sessions ramp quickly.
2. Keep only high-signal, repo-specific guidance likely to prevent mistakes.
3. Reconcile instruction drift across files without deleting valid custom constraints.

## Method

1. Prefer executable truth over prose when conflicts exist.
2. Verify every command before including it.
3. Keep sections short and scannable.
4. Remove stale or generic guidance.
5. Preserve useful constraints that remain true.

## Required Output Sections

1. Repo state and scope boundaries
2. Source-of-truth files and task ordering constraints
3. Verified commands (only commands that exist now)
4. Structure notes that affect implementation choices
5. Verification expectations and anti-claims

## Rules

- Never invent runnable surfaces (CLI, CI, hooks, Docker, package publish) if files do not exist.
- Never copy broad best-practice text that is not repo-specific.
- If uncertain, omit.
- Keep naming consistent with repo conventions.

## Output

<!-- output: AGENTS.md -->
