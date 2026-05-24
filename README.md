![codeForerunner — your codebase gets a Forerunner; your docs finally see the light](images/readme_banner.png)

# codeForerunner

Model-agnostic repository documentation tooling. Ships a prompt pack for codebase analysis and doc generation, a thin Python CLI, an MCP server, a Codex marketplace plugin, and drift-detection rules that keep docs honest.

## Install

```bash
pipx install codeforerunner   # recommended — isolated environment
pip install codeforerunner    # alternative
```

From source:

```bash
git clone https://github.com/derek-palmer/codeforerunner
cd codeforerunner
python -m pip install -e .
```

Verify: `forerunner --help`

## CLI

| Command | Purpose |
|---------|---------|
| `forerunner init` | Resolve agent-onboarding bundle to stdout (`--full` prepends scan; `--agents-only` is the default scope). |
| `forerunner scan` | Resolve scan bundle to stdout. |
| `forerunner doc <task>` | Resolve `base + partials + task` bundle to stdout. |
| `forerunner check` | Run drift-detection rules; silent no-op without `forerunner.config.yaml`. |
| `forerunner generate <task>` | Resolve bundle for `<task>` and call the configured provider. Add `--stream` to stream output token-by-token. |
| `forerunner doctor` | Single-screen health report: skill parity, marketplace validation, installed destinations, config, provider key. Add `--fix` to write a starter `forerunner.config.yaml` if absent. |
| `forerunner mcp-server` | Serve prompt bundles as MCP tools over stdio (JSON-RPC 2.0). |
| `forerunner install <agent>` | Idempotently write the canonical skill into agent-specific directories. |

## Prompt Pack

Prompts are bundled inside the package at `src/codeforerunner/prompts/`.

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
    ├── review.md
    ├── audit.md
    └── changelog.md
```

| Task | Purpose |
|------|---------|
| `scan` | Structured repo scan used by downstream tasks. |
| `init-agent-onboarding` | Generates or updates `AGENTS.md` from repo evidence. |
| `readme` | Generates or rewrites a top-level README. |
| `api-docs` | Documents public APIs. |
| `stack-docs` | Documents stack-specific areas. |
| `diagrams` | Generates Mermaid architecture or flow diagrams. |
| `flows` | Documents user, request, job, or data flows. |
| `version-audit` | Audits pinned versions from manifests, lockfiles, workflows, IaC. |
| `check` | Checks existing docs for staleness against a fresh scan. |
| `review` | Summarizes documentation impact for review. |
| `audit` | Security and dependency audit report. |
| `changelog` | Generates a Keep-a-Changelog entry from git log. |

## Quick Start

```bash
# 1. Point your agent at the scan prompt
forerunner scan

# 2. Generate or update docs for a task
export FORERUNNER_SCAN_DONE=1
forerunner doc readme

# 3. Direct model call (needs provider config)
forerunner generate readme --stream
```

## GitHub Action

Use forerunner check as a reusable action in any workflow:

```yaml
- uses: derek-palmer/codeforerunner@v0.3.2
```

With a pinned version:

```yaml
- uses: derek-palmer/codeforerunner@v0.3.2
  with:
    version: '0.3.2'
```

No-op when `forerunner.config.yaml` is absent.

## Configuration

Copy `forerunner.config.yaml.example` to `forerunner.config.yaml` to opt in. Without that file, `forerunner check` is a silent no-op. Generate a starter config with:

```bash
forerunner doctor --fix
```

### Config fields

```yaml
provider: anthropic          # anthropic | openai | google | ollama
model: claude-opus-4-7
api_key_env:
  anthropic: ANTHROPIC_API_KEY   # override per-provider env var name

tasks:
  check:
    enabled_rules:
      - R1-no-cli
      - R2-no-pre-commit
      - R3-no-ci
      - R4-no-installer
      - R5-no-python-package
      - R7-no-mcp
      - R8-no-marketplace
      - RI1-missing-cli          # inverse: doc claims CLI but file absent
      - RI5-missing-python-package
      - RI7-missing-mcp
      - RV1-version-drift        # pinned version in docs ≠ pyproject.toml
    ignore_paths:
      - docs/legacy/**/*.md
```

### Drift rules

| Rule | Fires when |
|------|-----------|
| `R1-no-cli` | Doc denies having a CLI, but `cli.py` is present |
| `R2-no-pre-commit` | Doc denies having pre-commit hooks, but `.pre-commit-hooks.yaml` present |
| `R3-no-ci` | Doc denies having CI, but `.github/workflows/*.yml` present |
| `R4-no-installer` | Doc denies having an installer, but `installer.py` present |
| `R5-no-python-package` | Doc denies having a Python package, but `pyproject.toml` present |
| `R6-no-docker` | Doc denies having Docker, but `Dockerfile`/`compose.yml` present |
| `R7-no-mcp` | Doc denies having an MCP server, but `mcp_server.py` present |
| `R8-no-marketplace` | Doc denies having a marketplace, but `marketplace.json` present |
| `RI1-missing-cli` | Doc references `forerunner` subcommands but `cli.py` absent |
| `RI5-missing-python-package` | Doc shows `pip install codeforerunner` but `pyproject.toml` absent |
| `RI7-missing-mcp` | Doc references `forerunner mcp-server` but `mcp_server.py` absent |
| `RV1-version-drift` | Doc pins `codeforerunner==X.Y.Z` differing from current version |

### MCP Server

`forerunner mcp-server` speaks JSON-RPC 2.0 over stdio and exposes one tool per `prompts/tasks/*.md`. A scan-first gate enforces SPEC V2: any tool except `scan` or `init-agent-onboarding` returns an error until `scan` has been called in the same session.

See `examples/mcp/` for Claude Desktop and mcp-cli wiring examples.

## Providers

`forerunner generate` supports four providers. Set the appropriate env var before calling:

| Provider | Env var | Default model |
|----------|---------|---------------|
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-opus-4-7` |
| `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| `google` | `GOOGLE_API_KEY` | `gemini-2.5-pro` |
| `ollama` | `OLLAMA_HOST` (optional) | `llama3` |

## Codex Plugin

```bash
forerunner install codex --marketplace
```

Installs the Codex marketplace entry and skill. Or install manually:
`forerunner install <agent>` copies the canonical skill into the agent-specific directory.

## Docs and Spec

- `SPEC.md` — canonical phase/task tracker
- `docs/getting-started.md` — manual prompt use
- `docs/prompt-guide.md` — how system, partial, and task prompts compose
- `docs/editor-agent-setup.md` — adapting prompts to local agents
- `docs/roadmap.md` — human-readable roadmap
- `docs/agent-distribution-design.md` — design backing Codex/Claude packages
