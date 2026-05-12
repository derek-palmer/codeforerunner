# codeforerunner v2 handoff

## Goal

Refactor `codeforerunner` from the previous analyzer-heavy implementation into a prompt-first repo. The core product should be a set of well-tuned prompts plus lightweight supporting docs and scaffolding for future CLI, MCP, hooks, and editor-agent integrations.

## Current state

- The old repo previously contained Python packaging, Docker, tests, docs, and a `src/` implementation for a more complex documentation platform.
- The intended v2 direction is to simplify that into prompts as the main asset, with thin wrappers around them instead of building a full analysis platform first.
- A gist script is being used locally to generate the initial prompt tree and `forerunner.config.yaml.example`.
- Local work is happening on the `v2-overhaul` branch.

## Product framing

Treat `codeforerunner` as:

- A prompt-first documentation toolkit.
- Agent-agnostic and model-agnostic.
- Designed to support multiple future surfaces: CLI, MCP server, editor instructions, hooks, and CI.
- Focused first on repo understanding, README generation, stack docs, diagrams, flow docs, and review/check workflows.

Do **not** rebuild the original complex analyzer architecture right now.

## Desired root structure

After the prompt-generation script runs, the repo should be moving toward this shape:

```text
codeforerunner/
├── LICENSE.md
├── README.md
├── codeforerunner_spec.md
├── forerunner.config.yaml.example
├── prompts/
│   ├── system/
│   │   └── base.md
│   ├── partials/
│   │   ├── context-format.md
│   │   ├── output-rules.md
│   │   └── stack-hints.md
│   └── tasks/
│       ├── scan.md
│       ├── readme.md
│       ├── api-docs.md
│       ├── stack-docs.md
│       ├── diagrams.md
│       ├── flows.md
│       ├── version-audit.md
│       ├── check.md
│       └── review.md
├── agent-configs/
│   ├── claude-project.md
│   ├── cursor-rules.md
│   ├── copilot-instructions.md
│   ├── cline.md
│   └── windsurf.md
├── hooks/
│   ├── pre-commit
│   └── pre-commit-install.sh
└── docs/
    ├── getting-started.md
    ├── prompt-guide.md
    ├── editor-agent-setup.md
    └── roadmap.md
```

## Immediate tasks

### 1. Replace the top-level README

Write a new `README.md` that:

- Explains the v2 prompt-first direction clearly.
- Positions prompts as the core product.
- Mentions future surfaces like CLI, MCP, hooks, and editor configs without pretending they are fully implemented if they are not.
- Includes a short quick-start for using the prompts in a local agent/editor workflow.
- Removes old Python-package-first and Docker-first framing unless those surfaces actually exist in the branch.

### 2. Replace the spec

Write a new `codeforerunner_spec.md` that:

- Frames the product as prompt-first.
- Defines prompt architecture first.
- Describes future delivery surfaces second: editor agent configs, MCP, CLI, hooks.
- Keeps the underlying repo-documentation use cases.
- Avoids reintroducing large custom analyzer/detector architecture as MVP scope.

### 3. Add agent config exports

Create `agent-configs/` files that adapt the base prompt for:

- Claude Project style instructions.
- Cursor rules.
- GitHub Copilot instructions.
- Cline / Roo style agent usage.
- Windsurf usage.

These can be early scaffolds, but they should be coherent and usable.

### 4. Add docs for humans

Create `docs/` content for:

- `getting-started.md`: what this repo is and how to use the prompts.
- `prompt-guide.md`: how prompts are organized and how task prompts compose with partials.
- `editor-agent-setup.md`: how to point local editor agents at these prompts/configs.
- `roadmap.md`: future phases for hooks, CLI, MCP, and packaging.

### 5. Keep cleanup intentional

Do not re-add old repo artifacts unless they serve the new direction.

Avoid bringing back these legacy areas unless there is a concrete reason:

- `src/`
- `tests/` for the old architecture
- `Dockerfile`
- `compose.yml`
- `Makefile`
- `pyproject.toml`
- `uv.lock`
- old CI or publishing workflows built around the removed Python package

If any of these are reintroduced later, they should support the new prompt-first strategy directly.

## Prompt architecture guidance

The prompts should be the source of truth.

### System prompt

`prompts/system/base.md`

Responsibilities:

- Define the role of codeforerunner.
- Establish output quality bar.
- Define documentation style rules.
- Instruct the agent to reason over repo structure, stack boundaries, interfaces, flows, and docs.

### Partials

`prompts/partials/`

Purpose:

- Reusable prompt fragments shared by task prompts.
- Keep repeated rules out of individual tasks.

Expected files:

- `context-format.md`
- `output-rules.md`
- `stack-hints.md`

### Task prompts

`prompts/tasks/`

Each task prompt should be focused and single-purpose.

Expected tasks:

- `scan.md`
- `readme.md`
- `api-docs.md`
- `stack-docs.md`
- `diagrams.md`
- `flows.md`
- `version-audit.md`
- `check.md`
- `review.md`

Each task prompt should define:

- Inputs expected from the caller.
- Output contract.
- Guardrails.
- When to be concise vs detailed.
- What not to invent.

## Recommended work order

1. Verify the prompt tree generated by the script is correct.
2. Write the new `README.md`.
3. Write the new `codeforerunner_spec.md`.
4. Create `agent-configs/` scaffolds.
5. Create `docs/` scaffolds and fill first-pass content.
6. Do a cleanup pass for stray legacy files and mismatched language in docs.
7. Review the repo top to bottom for naming consistency.

## Naming rules

Use these consistently:

- Repository/project name: `codeforerunner`
- Short CLI/product name: `forerunner`
- Example config file: `forerunner.config.yaml`

Avoid introducing alternate names unless there is a very good reason.

## Guardrails

- Do not over-engineer the MVP.
- Do not claim working CLI, MCP, or package publishing unless actual scaffolding exists.
- Do not reintroduce provider-specific logic as a core product concept.
- Do not frame this as a hosted SaaS.
- Do keep docs honest about current state versus future roadmap.
- Do optimize for portability into local editor agents.

## Definition of done for this phase

This phase is done when:

- The repo reads coherently as a prompt-first project.
- Top-level docs no longer describe the old architecture.
- Prompt files exist and are organized cleanly.
- Agent config examples exist.
- Human-facing setup docs exist.
- Legacy implementation cruft is removed or intentionally excluded.

## Suggested commit breakdown

- `docs: rewrite README for prompt-first v2`
- `docs: replace v1 spec with v2 prompt-first spec`
- `docs: add agent config scaffolds`
- `docs: add getting started and prompt guide`
- `chore: remove remaining legacy repo artifacts`

## Notes for the next agent

When in doubt, choose the simpler path.

The value here is not in building a giant framework. The value is in:

- strong prompt design,
- clear packaging of prompt assets,
- easy handoff into local agents and editor workflows,
- and a repo that explains itself cleanly.
