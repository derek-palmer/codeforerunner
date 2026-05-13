# Prompt Guide

`codeforerunner` prompts compose in three layers.

## 1. System Prompt

`prompts/system/base.md` defines the role, accuracy bar, Markdown rules, and gap handling.

Use it for every run.

## 2. Partials

`prompts/partials/` contains shared rules.

| File | Purpose |
| --- | --- |
| `context-format.md` | Defines target repo context shape and file selection rules. |
| `output-rules.md` | Defines Markdown, output target, accuracy, diagram, and length rules. |
| `stack-hints.md` | Helps classify repo stacks from evidence. |

## 3. Task Prompts

`prompts/tasks/scan.md` always runs first. Its YAML output feeds downstream tasks.

| Task | Input | Output |
| --- | --- | --- |
| `scan.md` | File tree, manifests, entrypoints, config | YAML repo scan |
| `readme.md` | Scan result, README, key files | `README.md` |
| `api-docs.md` | Scan result, route/interface files | API docs |
| `stack-docs.md` | Scan result, stack files | Stack docs |
| `diagrams.md` | Scan result, architecture files | Mermaid diagrams |
| `flows.md` | Scan result, flow-relevant files | Flow docs |
| `version-audit.md` | Manifests, lockfiles, Dockerfiles, workflows, IaC | Version audit |
| `check.md` | Fresh scan, docs, optional diff | Staleness report |
| `review.md` | Check report, diff, scan | Review summary |

## Contract

- Scan first.
- Downstream prompts depend on scan output.
- Claims must cite or derive from provided files.
- Missing evidence belongs in `## Gaps`.
- File output targets use `<!-- output: path/to/file.md -->` when prompt requires it.
