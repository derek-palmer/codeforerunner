---
name: codeforerunner
description: Routes a coding agent through the tracked codeforerunner prompt pack to keep repository documentation in sync with code. Use when the user asks to generate, refresh, audit, or review README, API docs, stack docs, diagrams, flow docs, version audits, stale-doc checks, or AGENTS onboarding files.
---

# codeforerunner Skill — Canonical Source

This file is the **canonical instruction source** for any codeforerunner agent package (Codex plugin, Claude skill/plugin, or generic Markdown skill). Downstream packages must preserve this file's post-frontmatter Markdown content verbatim (`SPEC.md` §V10); per-agent YAML frontmatter may differ, but the body cannot.

This skill does not bundle a runtime. It routes the host agent into the codeforerunner prompt pack tracked in the repository (`prompts/system/`, `prompts/partials/`, `prompts/tasks/`). No `forerunner` CLI, MCP server, hook, Docker image, Makefile target, or PyPI package is shipped yet — do not claim or assume any of them exist.

## When To Activate

Trigger this skill when the user asks for any of:

- Generate or refresh `README.md` from a repo's actual state.
- Generate or refresh API documentation.
- Generate or refresh stack / runtime / dependency documentation.
- Produce or refresh architecture or flow Mermaid diagrams.
- Audit pinned versions across manifests, lockfiles, Dockerfiles, IaC, workflows.
- Check whether existing docs are stale relative to current code.
- Review a doc-change diff for accuracy and over-claiming.
- Bootstrap or refresh `AGENTS.md` (or per-agent overlay files) from repo evidence.

Do not activate for general coding assistance, refactoring, bug fixing, or non-documentation tasks.

## Required Inputs

Before running any task, gather from the target repo:

- Full file tree, respecting ignore rules and the `forerunner.config.yaml` exclusion list when present.
- Root manifests and lockfiles (e.g. `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `package-lock.json`, `poetry.lock`).
- Entry-point files (up to 5).
- Build, test, lint, and CI configuration files.
- Existing documentation when updating, checking, or reviewing it.

If inputs are missing, the host agent may ask once **before starting** a task to collect them. This pre-task collection is the explicit exception to `prompts/system/base.md`'s "do not ask clarifying questions mid-task" rule — once a task is running, that rule applies. Do not invent file contents.

## Context Layers

These compose once into the prompt sent to the host model. They are not per-task steps.

- **System rules.** `prompts/system/base.md` — governing role and accuracy contract. Every output must obey it.
- **Context shape.** `prompts/partials/context-format.md` — target-repo context shape and file-selection rules.
- **Output rules.** `prompts/partials/output-rules.md` — Markdown standards, file output marker, diagram rules, length targets.
- **Stack hints.** `prompts/partials/stack-hints.md` — repo stack classification heuristics.

## Workflow

Per-run, in this order:

1. **Scan first.** Run `prompts/tasks/scan.md` and capture its YAML output. All documentation-generation and check workflows depend on the scan result. **Exception:** `prompts/tasks/init-agent-onboarding.md` may run without a prior scan because it derives onboarding guidance directly from repo evidence and existing instruction files.
2. **Run the matching task prompt.** See `docs/prompt-guide.md` §3 for the authoritative task → input → output table. Pick the task that matches the user's request and pass the scan result plus any task-specific inputs.
3. **Honor task output contracts.** When a task prompt specifies `<!-- output: path/to/file.md -->`, write the artifact to that path. When it does not, return Markdown for the user to place. Append a `## Gaps` section whenever evidence was insufficient — never silently invent content.

## Safety And Scope Rules

- **Ground every claim in repo evidence.** Never document an endpoint, function, integration, version, or environment variable that is not present in the provided files. Unverifiable items go under `## Gaps`.
- **Inspect the target repo before producing output.** Do not generate documentation from training-data assumptions.
- **Respect `forerunner.config.yaml`.** Treat it as the canonical config filename. The repo currently ships `forerunner.config.yaml.example` as the example shape; no loader exists yet. Do not send paths excluded by that config (or by common secret-file patterns) to external model providers.
- **No destructive overwrites.** Stop before overwriting existing documentation unless the task prompt's output gives an explicit managed-section strategy. Prefer minimal, reviewable diffs.
- **Report stale-doc failures clearly.** When `check.md` flags drift, surface the failure with file paths and reasons — do not paper over it.
- **Do not claim runtime surfaces exist.** There is no runnable `forerunner` CLI, MCP server, pre-commit hook, CI workflow, Docker image, Makefile, or PyPI install. Treat any mention of those in documentation as future-tense roadmap items only.
- **Do not duplicate prompt content.** Route the host agent to the tracked prompt files; do not paste their contents into the skill, plugin metadata, or generated artifacts beyond what the host agent strictly needs.

## Naming Convention

- Repo and product name: `codeforerunner`.
- CLI and config namespace (planned, not yet runnable): `forerunner`.
- Canonical config filename: `forerunner.config.yaml`.

Use these names consistently across any generated documentation, agent metadata, and instruction text.

## Ownership Boundary

This file owns the skill's instruction content. Generated or copied skill files (Codex `plugins/codeforerunner/.codex-plugin/plugin.json` + `plugins/codeforerunner/skills/codeforerunner/SKILL.md`, Claude `.claude-plugin/plugin.json` + `skills/codeforerunner/SKILL.md`, generic `skills/codeforerunner/SKILL.md` — see `docs/agent-distribution-design.md` §"Package Layout") downstream of T13, T14, and T15 must:

- Preserve this file's post-frontmatter Markdown content verbatim (frontmatter may differ per agent).
- Add only agent-specific metadata around it.
- Stay routed to the tracked prompt pack — never embed a second copy of product logic.

See `docs/agent-distribution-design.md` for the full packaging and installer design, `SPEC.md` §I.agent-skill for the spec entry that pins this file as canonical, and §V10 for the verbatim-preservation rule.
