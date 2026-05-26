---
name: codeforerunner
description: Routes a coding agent through the tracked codeforerunner prompt pack to keep repository documentation in sync with code. Use when the user asks to generate, refresh, audit, or review README, API docs, stack docs, diagrams, flow docs, version audits, stale-doc checks, security audits, changelog entries, or AGENTS onboarding files.
---

# codeforerunner Skill

The authoritative canonical source for this skill body is `agent/codeforerunner.skill.md` (see the `SPEC.md` I.agent-skill entry). Distribution copies are not independent sources; maintainers should edit the canonical file, then sync the post-frontmatter body into Codex and Claude copies. Downstream packages must preserve this post-frontmatter Markdown content verbatim (`SPEC.md` V10); per-agent YAML frontmatter may differ, but the body cannot.

This skill does not bundle a runtime. It routes the host agent into the codeforerunner prompt pack (`src/codeforerunner/prompts/` in the source repo, or retrieved via `forerunner doc <task>` from the installed CLI). The `forerunner` CLI, MCP server, pre-commit hook, CI workflow, and PyPI package are all live. Docker image and Makefile are not present.

The host agent is always the model — no API key or external provider needed. Use `forerunner doc <task>` to output the assembled prompt bundle, then act on it directly.

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
- Run a security and dependency audit.
- Generate a Keep-a-Changelog entry from git history.

Do not activate for general coding assistance, refactoring, bug fixing, or non-documentation tasks.

## Required Inputs

Before running any task, gather from the target repo:

- Full file tree, respecting ignore rules and the `forerunner.config.yaml` exclusion list when present.
- Root manifests and lockfiles (e.g. `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `package-lock.json`, `poetry.lock`).
- Entry-point files (up to 5).
- Build, test, lint, and CI configuration files.
- Existing documentation when updating, checking, or reviewing it.

If inputs are missing, the host agent may ask once **before starting** a task to collect them. This pre-task collection is the explicit exception to the base prompt's "do not ask clarifying questions mid-task" rule — once a task is running, that rule applies. Do not invent file contents.

## Context Layers

These compose once into the prompt sent to the host model. They are not per-task steps. Retrieve each via `forerunner doc <task>` or read directly from `src/codeforerunner/prompts/`.

- **System rules.** `system/base.md` — governing role and accuracy contract. Every output must obey it.
- **Context shape.** `partials/context-format.md` — target-repo context shape and file-selection rules.
- **Output rules.** `partials/output-rules.md` — Markdown standards, file output marker, diagram rules, length targets.
- **Stack hints.** `partials/stack-hints.md` — repo stack classification heuristics.

## Workflow

Per-run, in this order:

1. **Scan first.** Run `forerunner doc scan` and capture its YAML output. All documentation-generation and check workflows depend on the scan result. **Exception:** `init-agent-onboarding` may run without a prior scan because it derives onboarding guidance directly from repo evidence and existing instruction files.
2. **Run the matching task prompt.** See `docs/prompt-guide.md` section 3 for the authoritative task → input → output table. Run `forerunner doc <task>` to get the assembled prompt bundle, then execute it. Pass the scan result plus any task-specific inputs.
3. **Honor task output contracts.** When a task prompt specifies `<!-- output: path/to/file.md -->`, write the artifact to that path. When it does not, return Markdown for the user to place. Append a `## Gaps` section whenever evidence was insufficient — never silently invent content.

To refresh all docs in one pass, run `forerunner refresh` — it outputs scan + check + all doc task bundles in sequence. Check drift with `forerunner check`. Health report via `forerunner doctor`.

## Safety And Scope Rules

- **Ground every claim in repo evidence.** Never document an endpoint, function, integration, version, or environment variable that is not present in the provided files. Unverifiable items go under `## Gaps`.
- **Inspect the target repo before producing output.** Do not generate documentation from training-data assumptions.
- **Respect `forerunner.config.yaml`.** Treat it as the canonical config filename. Use `forerunner doctor --fix` to generate a starter config.
- **No destructive overwrites.** Stop before overwriting existing documentation unless the task prompt's output gives an explicit managed-section strategy. Prefer minimal, reviewable diffs.
- **Report stale-doc failures clearly.** When `check.md` flags drift, surface the failure with file paths and reasons — do not paper over it.
- **Do not duplicate prompt content.** Route the host agent to the tracked prompt files; do not paste their contents into the skill, plugin metadata, or generated artifacts beyond what the host agent strictly needs.

## Naming Convention

- Repo and product name: `codeforerunner`.
- CLI and config namespace: `forerunner`.
- Canonical config filename: `forerunner.config.yaml`.

Use these names consistently across any generated documentation, agent metadata, and instruction text.

## Ownership Boundary

The canonical file owns the skill's instruction content. Generated or copied skill files include the Codex distribution (`plugins/codeforerunner/.codex-plugin/plugin.json` + `plugins/codeforerunner/skills/codeforerunner/SKILL.md`) and the implemented Claude distribution (`.claude-plugin/plugin.json` + `skills/codeforerunner/SKILL.md`). The proposed generic distribution in T15 reuses that same root `skills/codeforerunner/SKILL.md` path rather than a separate generic-only skill file. See the `docs/agent-distribution-design.md` Package Layout section.

- Preserve this file's post-frontmatter Markdown content verbatim (frontmatter may differ per agent).
- Add only agent-specific metadata around it.
- Stay routed to the tracked prompt pack — never embed a second copy of product logic.

See `docs/agent-distribution-design.md` for the full packaging and installer design, the `SPEC.md` I.agent-skill entry that pins this file as canonical and the V10 verbatim-preservation rule.
