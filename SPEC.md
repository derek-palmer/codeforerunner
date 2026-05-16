# codeforerunner Spec

## §G Goal

G1: `codeforerunner` → model-agnostic doc guardian; analyze repo, maintain docs/diagrams/architecture knowledge as code evolves.

## §C Constraints

C1: prompts = core product; wrappers thin.
C2: no analyzer-heavy v1 rebuild unless explicit.
C3: no claims for working CLI, MCP, hooks, CI, Docker, PyPI until files exist.
C4: model/provider agnostic; provider-specific config optional.
C5: docs must distinguish current state vs roadmap.
C6: future legacy-style files (`src/`, `tests/`, `Dockerfile`, `Makefile`, `pyproject.toml`, `uv.lock`) must support prompt-first strategy directly.
C7: skill/plugin packages ! route to prompt pack/current files until runtime wrappers exist.

## §I Interfaces

I.prompts: `prompts/system/base.md` + `prompts/partials/*.md` + `prompts/tasks/*.md` → reusable prompt pack.
I.init-onboarding: `prompts/tasks/init-agent-onboarding.md` → onboarding task for creating/updating `AGENTS.md` from repo evidence.
I.config: `forerunner.config.yaml.example` → example config only; no loader yet.
I.agent-configs: `agent-configs/*.md` → copyable editor-agent instructions.
I.docs: `docs/*.md` → human setup, prompt guide, editor setup, roadmap.
I.spec: `SPEC.md` → canonical phase/task tracker.
I.future-skill-plugin: skill/plugin packages ? future surface; not implemented.
I.future-cli: `forerunner` CLI ? future surface; not implemented.
I.future-mcp: MCP server ? future surface; not implemented.
I.future-hooks: pre-commit/CI checks ? future surface; not implemented.

## §V Invariants

V1: README current-state claims ! match tracked files.
V2: prompt workflow ! run `prompts/tasks/scan.md` before downstream task prompts.
V3: roadmap surfaces ! labeled future until executable/scaffold files exist.
V4: no doc says install/run `forerunner` until CLI exists.
V5: no doc says Docker/Makefile/PyPI/CI/pre-commit exists until corresponding files exist.
V6: spec ! updated when phases/tasks shift.
V7: agent configs ! reference prompt files, not imaginary package install.
V8: skill/plugin design ! avoid manual prompt discovery but must not claim installed package support before files exist.
V9: init onboarding docs must not claim runnable `forerunner init` until wrapper files exist.

## §P Phases

id|status|phase|exit
P0|x|repo truth cleanup|README/spec/AGENTS align with v2 state
P1|.|prompt pack hardening|task prompts consistent, composable, evidence-first
P2|x|agent config exports|editor-agent configs usable from tracked prompts
P3|x|human docs|setup, prompt guide, editor setup, roadmap present
P4|.|skill/plugin distribution design|simple agent setup planned without runtime claims
P5|.|thin wrappers|CLI/MCP/hooks only after prompt contract stable

## §T Tasks

id|status|phase|task|cites
T1|x|P0|replace stale `README.md` with prompt-first current state|V1,V3,V4,V5
T2|x|P0|move phase/task tracker to `SPEC.md`|V6,I.spec
T3|x|P2|add `agent-configs/` scaffolds|V7,I.agent-configs
T4|x|P3|add `docs/getting-started.md`|I.docs,V1
T5|x|P3|add `docs/prompt-guide.md`|I.prompts,V2
T6|x|P3|add `docs/editor-agent-setup.md`|I.agent-configs,V7
T7|x|P3|add `docs/roadmap.md`|V3,I.future-cli,I.future-mcp,I.future-hooks
T8|.|P1|review task prompts for shared input/output contracts|I.prompts,V2
T16|x|P1|add prompt-first init onboarding task for AGENTS generation/update|I.init-onboarding,V9
T9|.|P5|design CLI only after prompt workflow stabilizes|I.future-cli,C1
T10|.|P5|design hooks/CI only after check/review prompts stabilize|I.future-hooks,C1
T11|x|P4|write skill/plugin distribution design|I.future-skill-plugin,V8
T12|.|P4|add canonical skill source from prompt pack|I.prompts,I.future-skill-plugin,C7
T13|.|P4|add Codex plugin package for prompt workflow|I.future-skill-plugin,V8
T14|.|P4|add Claude skill/plugin package for prompt workflow|I.future-skill-plugin,V8
T15|.|P4|add idempotent installer for owned agent artifacts|I.future-skill-plugin,V8

## §B Bugs

id|date|cause|fix
