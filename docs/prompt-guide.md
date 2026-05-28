# Prompt Guide

`codeforerunner` prompts compose in three layers. Prompts live in `src/codeforerunner/prompts/` (bundled in the pip package) and are retrieved via `forerunner doc <task>`, which emits the fully assembled bundle (system + partials + task) to stdout.

## 1. System Prompt

`system/base.md` defines the role, accuracy bar, Markdown rules, and gap handling.

Use it for every run.

## 2. Partials

`partials/` contains shared rules.

| File | Purpose |
| --- | --- |
| `context-format.md` | Defines target repo context shape and file selection rules. |
| `output-rules.md` | Defines Markdown, output target, accuracy, diagram, and length rules. |
| `stack-hints.md` | Helps classify repo stacks from evidence. |

## 3. Task Prompts

`tasks/scan.md` runs first for documentation generation/check workflows. `init-agent-onboarding.md` may run before scan when its goal is to create or refresh repo agent instructions.

| Task | Input | Output |
| --- | --- | --- |
| `scan.md` | File tree, manifests, entrypoints, config | YAML repo scan |
| `init-agent-onboarding.md` | File tree, key configs/docs, instruction files, domain vocabulary files; scan not required | `AGENTS.md` update; `CONTEXT.md` update when stable terms exist |
| `readme.md` | Scan result, README, key files | `README.md` |
| `api-docs.md` | Scan result, route/interface files | API docs |
| `stack-docs.md` | Scan result, stack files | Stack docs |
| `diagrams.md` | Scan result, architecture files | Mermaid diagrams |
| `flows.md` | Scan result, flow-relevant files | Flow docs |
| `arch-review.md` | Scan result, key modules, tests, optional `CONTEXT.md`/ADRs | `.forerunner/arch-review.md` |
| `version-audit.md` | Manifests, lockfiles, Dockerfiles, workflows, IaC | Version audit |
| `check.md` | Fresh scan, docs, optional diff | Staleness report |
| `review.md` | Check report, diff, scan | Review summary |
| `audit.md` | Scan result, manifests, lockfiles, CI/CD files | Security and dependency audit |
| `changelog.md` | `git log` / `git diff` output, existing CHANGELOG.md | Keep-a-Changelog entry |

## Contract

- Scan first for documentation generation/check workflows.
- `init-agent-onboarding.md` may run without scan because it derives onboarding guidance directly from repo evidence and existing instruction files.
- Downstream documentation prompts depend on scan output.
- Claims must cite or derive from provided files.
- Missing evidence belongs in `## Gaps`.
- File output targets use `<!-- output: path/to/file.md -->` when prompt requires it.
