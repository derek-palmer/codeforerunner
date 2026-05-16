# Codeforerunner Init Specification

## Goal

Define a consistent initialization workflow for repo onboarding that:

- Analyzes repository structure, stack, commands, and constraints from evidence.
- Generates or updates `AGENTS.md` with compact, high-signal instructions.
- Optionally generates per-agent guidance files for local agent setups.
- Can later be wrapped by a thin CLI surface without changing core logic.

This spec is prompt-first and wrapper-agnostic.

## Current State vs Future Wrapper

- Current state: onboarding is manual/prompt-driven.
- Future state: thin wrapper command (for example `forerunner init`) may orchestrate the same steps.
- Constraint: do not claim runnable init CLI until wrapper files exist in the repo.

## Core Concepts

- Init pass: read-first repo analysis plus focused docs/instruction updates.
- AGENTS contract: repo-wide canonical onboarding rules for future agent sessions.
- Agent overlays: optional tool-specific instructions derived from the same repo analysis.
- Voice mode: concise communication defaults are configurable per project; they are not universal product requirements.

## Init Workflow (Prompt-First)

1. Repository analysis
   - Detect languages/frameworks/tooling from manifests, lockfiles, workflows, and infra files.
   - Determine likely dev/test/lint/format commands from executable sources.
   - Classify topology: single-project vs monorepo; identify key boundaries and entrypoints.

2. Update `AGENTS.md`
   - If missing, create from evidence.
   - If present, update in place and preserve useful custom constraints.
   - Keep only high-signal content likely to prevent agent mistakes.

3. Optional per-agent guidance
   - Create or update repo-owned agent guidance files when requested.
   - Reuse same facts as `AGENTS.md`; avoid contradictory command sets.

4. Stop after onboarding artifacts by default
   - Default init scope is agent onboarding only.
   - Full documentation generation is a separate task flow.

## Optional Full Mode (Future Wrapper)

When a future wrapper supports full mode, it may run onboarding first and then chain documentation tasks (README, stack docs, diagrams, flows, review/check) using scan output.

## AGENTS.md Requirements

Required sections should stay compact:

1. Repo reality and scope boundaries
2. Highest-value commands (dev/test/lint/format/release checks when present)
3. Structural notes that change agent behavior
4. Non-obvious constraints and anti-claims (what is planned but not implemented)
5. Verification expectations for doc/prompt-only changes

Rules:

- Prefer executable truth over prose when conflicts exist.
- Omit generic advice.
- Avoid speculative claims.
- Keep names consistent: `codeforerunner`, `forerunner`, `forerunner.config.yaml`.

## Non-Destructive Update Rules

For existing onboarding files:

- Preserve user-authored constraints unless they conflict with verifiable repo state.
- Replace stale command claims with verified commands.
- Keep deltas minimal and easy to review.

## Future Wrapper Interface (Design Only)

Potential command surface (not currently implemented):

```text
forerunner init
forerunner init --full
forerunner init --agents-only
```

Wrapper responsibility should be orchestration only; product logic remains in prompt contracts and repo docs.

## Acceptance Criteria

- Onboarding output reflects current repo state and avoids overclaims.
- `AGENTS.md` updates are compact, specific, and materially useful.
- Prompt-first workflow remains source of truth; wrapper behavior is documented as future.
