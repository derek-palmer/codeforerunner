![codeForerunner — your codebase gets a Forerunner; your docs finally see the light](images/readme_banner.png)

# codeForerunner

CodeForerunner is a model-agnostic documentation agent that acts as overwatch for your repository, automatically analyzing code and maintaining docs, diagrams, and architecture knowledge as your codebase evolves over time.

The current repo is the prompt-first foundation for that agent: it ships prompt assets for understanding a codebase and generating developer docs. Thin delivery surfaces such as a CLI, MCP server, hooks, and CI checks are roadmap items, not implemented runtime features yet.

## Current State

- Core product: Markdown prompts in `prompts/`.
- Current config: `forerunner.config.yaml.example` documents intended options only.
- Current execution model: paste or attach prompts to your local agent/editor workflow.
- Not currently present: Python package, CLI, Docker image, Makefile, pre-commit hook, CI workflow, MCP server, or published package.

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
3. Run `prompts/tasks/scan.md` first.
4. Pass the scan result into one downstream task prompt, such as `prompts/tasks/readme.md` or `prompts/tasks/stack-docs.md`.
5. Apply generated docs only after checking that every claim is grounded in provided files.

## What The Prompts Do

| Prompt | Purpose |
| --- | --- |
| `prompts/system/base.md` | Defines the codeforerunner role, quality bar, Markdown rules, and accuracy constraints. |
| `prompts/tasks/scan.md` | Produces the first structured repo scan used by downstream tasks. |
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
- `docs/agent-distribution-design.md` designs future Claude/Codex skill and plugin packaging.

## Configuration

`forerunner.config.yaml.example` is a proposed config shape for future wrappers. It is safe to reference when designing integrations, but there is no repo code that loads it today.

## Roadmap

Near-term work should keep the repo lightweight:

| Status | Phase | Scope |
| --- | --- | --- |
| Done | P0 | Repo truth cleanup: README, spec, and AGENTS align with v2 prompt-first state. |
| Todo | P1 | Prompt pack hardening: make task prompts consistent, composable, and evidence-first. |
| Done | P2 | Agent config exports: Claude, Cursor, Copilot, Cline/Roo, and Windsurf scaffolds. |
| Done | P3 | Human docs: getting started, prompt guide, editor setup, and roadmap. |
| Todo | P4 | Skill/plugin distribution: package prompt workflow for Claude/Codex setup. |
| Later | P5 | Thin wrappers: CLI, MCP, hooks, and CI only after prompt contracts stabilize. |

See `SPEC.md` and `docs/roadmap.md` for the current phase plan.
