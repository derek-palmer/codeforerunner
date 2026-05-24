---
name: forerunner-scan
description: Scan a repository to collect structured evidence for documentation tasks. Always run this first — all other forerunner tasks depend on its output.
---

# forerunner-scan

First task in every codeforerunner workflow. Produces a structured YAML scan result that all downstream tasks consume as input.

## Activate when

User asks to: scan a repo, analyze the codebase before generating docs, collect repo evidence, or run any forerunner task that says "requires scan result."

## Collect this context

- Full file tree (respecting `.gitignore`)
- Root manifests and lockfiles: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `requirements*.txt`, and matching lockfiles
- Entry-point files (up to 5)
- Build, test, lint, CI configuration files
- `forerunner.config.yaml` if present

## Execute

Run `forerunner doc scan` to compose the full prompt with system rules, then execute it.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/scan.md`
- `src/codeforerunner/prompts/system/base.md`
- `src/codeforerunner/prompts/partials/context-format.md`

## Output

A YAML-structured scan result containing: detected stack, runtime versions, entry points, key module catalog, config file inventory, and test framework. Save as `.forerunner/scan.yaml` or pass inline to the next task.

## Important

Never skip this step for readme, api-docs, diagrams, flows, stack-docs, check, audit, or version-audit tasks. Only `changelog` and `init` can run without a prior scan.
