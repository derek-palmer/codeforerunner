![codeForerunner — your codebase gets a Forerunner; your docs finally see the light](images/readme_banner.png)

# codeForerunner

CodeForerunner is a model-agnostic documentation agent that acts as overwatch for your repository, automatically analyzing code and maintaining docs, diagrams, and architecture knowledge as your codebase evolves over time.

The current repo is the prompt-first foundation for that agent: it ships prompt assets for understanding a codebase and generating developer docs. A thin Python CLI, an idempotent skill installer, and pre-commit + CI hooks now wrap those prompts; an MCP server and a published package remain roadmap items.

## Current State

- Core product: Markdown prompts in `prompts/`.
- Agent package artifacts: Codex plugin files under `plugins/codeforerunner/` and Claude Code plugin files under `.claude-plugin/` plus `skills/codeforerunner/`.
- Python package: `pyproject.toml` + `src/codeforerunner/` expose a `forerunner` console script. `forerunner doc <task>` resolves the prompt bundle (base + partials + task) to stdout; `forerunner install <agent>` idempotently writes the canonical skill into agent-specific directories; `forerunner init`/`scan` are honest stubs (exit 2).
- Hooks: `.pre-commit-hooks.yaml` exposes a `forerunner-check` hook; `.github/workflows/forerunner-check.yml` mirrors it in CI. Both no-op when `forerunner.config.yaml` is absent.
- Current config: `forerunner.config.yaml.example` documents intended options only; no loader is wired yet.
- Not currently present: Docker image, Makefile, MCP server, published package.

## Prompt Layout

```text
prompts/
├── system/
│   └── base.md
├── partials/
│   ├── context-format.md
│   ├── output-rules.md
│   └── stack-hints.md
└── tasks/
    ├── scan.md
    ├── init-agent-onboarding.md
    ├── readme.md
    ├── api-docs.md
    ├── stack-docs.md
    ├── diagrams.md
    ├── flows.md
    ├── version-audit.md
    ├── check.md
    └── review.md
```

## Quick Start

1. Open `prompts/system/base.md` and use it as the agent system or project instruction.
2. Assemble repo context using the shape in `prompts/partials/context-format.md`.
3. For documentation generation, run `prompts/tasks/scan.md` first.
4. For agent onboarding only, run `prompts/tasks/init-agent-onboarding.md` directly.
5. Pass the scan result into one downstream documentation prompt, such as `prompts/tasks/readme.md` or `prompts/tasks/stack-docs.md`.
6. Apply generated docs only after checking that every claim is grounded in provided files.

## What The Prompts Do

| Prompt | Purpose |
| --- | --- |
| `prompts/system/base.md` | Defines the codeforerunner role, quality bar, Markdown rules, and accuracy constraints. |
| `prompts/tasks/scan.md` | Produces the first structured repo scan used by downstream tasks. |
| `prompts/tasks/init-agent-onboarding.md` | Generates or updates `AGENTS.md` from repo evidence plus files such as `CLAUDE.md`, `.cursor/rules/*`, `.cursorrules`, `.github/copilot-instructions.md`, and `opencode.json`. |
| `prompts/tasks/readme.md` | Generates or rewrites a top-level README from scan output and selected files. |
| `prompts/tasks/api-docs.md` | Documents public APIs when endpoints/interfaces are evident. |
| `prompts/tasks/stack-docs.md` | Documents stack-specific areas of a repo. |
| `prompts/tasks/diagrams.md` | Generates Mermaid architecture or flow diagrams. |
| `prompts/tasks/flows.md` | Documents user, request, job, or data flows. |
| `prompts/tasks/version-audit.md` | Audits pinned versions from manifests, lockfiles, Dockerfiles, workflows, or IaC. |
| `prompts/tasks/check.md` | Checks existing docs for staleness against a fresh scan. |
| `prompts/tasks/review.md` | Summarizes documentation impact for review. |

## Docs And Spec

- `SPEC.md` tracks phases, invariants, and tasks so future PRs can make small status updates instead of broad rewrites.
- `docs/getting-started.md` explains manual prompt use.
- `docs/prompt-guide.md` explains how system, partial, and task prompts compose.
- `docs/editor-agent-setup.md` explains how to adapt prompts to local agents.
- `docs/roadmap.md` separates current prompt assets from future wrappers.
- `docs/agent-distribution-design.md` explains current Codex/Claude package artifacts and future installer work.

## Configuration

`forerunner.config.yaml.example` is a proposed config shape. The current `forerunner check` only uses its presence as a hook gate; no loader consumes its contents yet.

## Roadmap

Near-term work should keep the repo lightweight:

| Status | Phase | Scope |
| --- | --- | --- |
| Done | P0 | Repo truth cleanup: README, spec, and AGENTS align with v2 prompt-first state. |
| Todo | P1 | Prompt pack hardening: make task prompts consistent, composable, and evidence-first. |
| Done | P2 | Agent config exports: Claude, Cursor, Copilot, Cline/Roo, and Windsurf scaffolds. |
| Done | P3 | Human docs: getting started, prompt guide, editor setup, and roadmap. |
| Done | P4 | Skill/plugin distribution: Codex plugin, Claude plugin, and `forerunner install` installer all present. |
| In progress | P5 | Thin wrappers: CLI + pre-commit/CI hooks runnable; MCP server still future. |

See `SPEC.md` and `docs/roadmap.md` for the current phase plan.
