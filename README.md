![codeForerunner — your codebase gets a Forerunner; your docs finally see the light](images/readme_banner.png)

# codeForerunner

CodeForerunner is a model-agnostic documentation agent that acts as overwatch for your repository, automatically analyzing code and maintaining docs, diagrams, and architecture knowledge as your codebase evolves over time.

The current repo is the prompt-first foundation for that agent: it ships prompt assets for understanding a codebase and generating developer docs. A thin Python CLI (including `forerunner mcp-server` and a scoped `forerunner init --full / --agents-only`), an idempotent skill installer, pre-commit + CI hooks, and a PyPI publish workflow now wrap those prompts; the first published PyPI release remains pending.

## Current State

- Core product: Markdown prompts in `prompts/`.
- Agent package artifacts: Codex plugin files under `plugins/codeforerunner/` and Claude Code plugin files under `.claude-plugin/` plus `skills/codeforerunner/`.
- Python package: `pyproject.toml` + `src/codeforerunner/` expose a `forerunner` console script. `forerunner doc <task>` resolves the prompt bundle (base + partials + task) to stdout; `forerunner install <agent>` idempotently writes the canonical skill into agent-specific directories; `forerunner init` resolves the agent-onboarding bundle (with `--full` to prepend a scan or `--agents-only` for the default scope); `forerunner scan` resolves the scan bundle; `forerunner mcp-server` serves prompt bundles as MCP tools over stdio.
- Hooks: `.pre-commit-hooks.yaml` exposes a `forerunner-check` hook; `.github/workflows/forerunner-check.yml` mirrors it in CI. Both no-op when `forerunner.config.yaml` is absent.
- Current config: `forerunner.config.yaml.example` documents the schema now parsed by `src/codeforerunner/config.py`; see "Configuration" below.
- Not currently present: Docker image, Makefile, published PyPI release.

## Install

After the first PyPI release:

```bash
pipx install codeforerunner   # recommended; isolated environment
pip install codeforerunner    # alternative
```

From source:

```bash
git clone https://github.com/derek-palmer/codeForerunner
cd codeForerunner
python -m pip install -e .
```

Then `forerunner --help` should print the subcommand list.

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
- `docs/roadmap.md` mirrors the `SPEC.md` phase status in human-readable form.
- `docs/agent-distribution-design.md` records the design that backs the Codex/Claude packages and `forerunner install`.

## Configuration

`forerunner.config.yaml.example` documents the loaded schema. Copy it to `forerunner.config.yaml` to opt in; without that file, `forerunner check` is a silent no-op. The schema has top-level provider/model fields (`provider`, `model`, `api_key_env`, `output_dir`, `context_max_files`, `context_max_lines_per_file`, `approaching_eol_threshold_months`), `ignore_patterns`, `tasks.version_audit`, and `tasks.check`. `forerunner check` honors `tasks.check.enabled_rules` (allowlist of rule IDs, default all) and `tasks.check.ignore_paths` (fnmatch globs applied to scanned docs). Invalid YAML, unknown providers, unknown `api_key_env` providers, or unknown severities surface as a `ConfigError` and exit non-zero.

### MCP Server

`forerunner mcp-server` speaks JSON-RPC 2.0 over stdio and exposes one tool per `prompts/tasks/*.md` (tool name = filename stem). Each `tools/call` returns the resolved `base + partials + task` bundle as text. A scan-first gate enforces SPEC V2: any tool other than `scan` or `init-agent-onboarding` returns an error until `scan` has been called in the same session. Point any MCP-compatible client at `forerunner mcp-server` as a stdio server (running from the target repo so `prompts/tasks/` resolves).

See `examples/mcp/` for Claude Desktop and mcp-cli wiring examples.

## Roadmap

See `SPEC.md` for the canonical phase/task tracker and `docs/roadmap.md` for the human-readable roadmap.
