# Task Checklist

This checklist is organized into small phases so an agent can complete one bounded slice at a time. Each task should be implemented, tested, and reviewed before the next task begins.

## Phase 0: Foundations

- [ ] T0.1 Create `pyproject.toml` with package metadata and a console entry point for `forerunner`. (Plan: P0.1, Requirement: 1) 
- [ ] T0.2 Create `src/codeforerunner/` with `__init__.py` and `cli.py`. (Plan: P0.1, Requirement: 1)
- [ ] T0.3 Implement a `forerunner --help` command path that exits cleanly. (Plan: P0.1, Requirement: 1)
- [ ] T0.4 Add config model and loader support for `forerunner.config.yaml`. (Plan: P0.2, Requirement: 2)
- [ ] T0.5 Add config validation errors with clear field-level messages. (Plan: P0.2, Requirement: 2)
- [ ] T0.6 Define initial shared models for repository, stack area, entity, integration hint, and generation result. (Plan: P0.3, Requirement: 4)
- [ ] T0.7 Add structured logging utilities. (Plan: P0.3, Requirement: 1)
- [ ] T0.8 Add unit tests for CLI bootstrapping and config loading. (Plan: P0.1, P0.2, Requirements: 1, 2)
- [ ] T0.9 Define the base model adapter interface (protocol, core types, and how orchestration supplies an adapter to pipelines). Any AI-assisted path SHALL call through this interface only. (Plan: P0.4, Requirement: 12)

## Phase 1: Repository understanding

- [ ] T1.1 Implement repository file scanning with include and exclude support. (Plan: P1.1, Requirement: 3)
- [ ] T1.2 Add technology detection for Python markers. (Plan: P1.2, Requirement: 3)
- [ ] T1.3 Add technology detection for React or general frontend markers. (Plan: P1.2, Requirement: 3)
- [ ] T1.4 Add technology detection for Ruby markers. (Plan: P1.2, Requirement: 3)
- [ ] T1.5 Add technology detection for Terraform markers. (Plan: P1.2, Requirement: 3)
- [ ] T1.6 Normalize scanner and detector output into the shared repository model. (Plan: P1.3, Requirement: 4)
- [ ] T1.7 Add tests for single-stack detection. (Plan: P1.2, Requirements: 3, 4)
- [ ] T1.8 Add tests for polyglot stack detection. (Plan: P1.2, P1.3, Requirements: 3, 4)

## Phase 2: First generated docs

Prerequisite: **T0.9** is complete so AI-assisted generation in this phase uses the adapter interface, not a concrete provider.

- [ ] T2.1 Implement README generation from the shared repository model. (Plan: P2.1, P0.4, Requirements: 5, 12)
- [ ] T2.2 Make README generation concise and link-oriented rather than dumping all detail. (Plan: P2.1, Requirement: 5) 
- [ ] T2.3 Implement the first stack-specific documentation generator for Python services or React apps. (Plan: P2.2, P0.4, Requirements: 6, 12)
- [ ] T2.4 Add output directory creation for `docs/apps/`, `docs/services/`, `docs/infrastructure/`, `docs/api/`, `docs/diagrams/`, and `docs/flows/`. (Plan: P2.2, Requirements: 5, 6)
- [ ] T2.5 Implement a minimal Mermaid architecture diagram generator. (Plan: P2.3, Requirement: 8) 
- [ ] T2.6 Add tests for README and first doc generation outputs. (Plan: P2.1, P2.2, Requirements: 5, 6, 8)

## Phase 3: Deeper code understanding

- [ ] T3.1 Implement API extraction for the first supported ecosystem. (Plan: P3.1, Requirement: 7)
- [ ] T3.2 Generate API Markdown docs from extracted entities. (Plan: P3.1, Requirement: 7)
- [ ] T3.3 Add the second stack-specific analyzer and generator. (Plan: P3.2, Requirements: 3, 6, 7)
- [ ] T3.4 Add the third stack-specific analyzer and generator. (Plan: P3.2, Requirements: 3, 6, 7)
- [ ] T3.5 Add tests for partial extraction behavior and clear limitations reporting. (Plan: P3.1, Requirement: 7)

## Phase 4: Cross-stack system understanding

- [ ] T4.1 Detect integration hints such as HTTP clients, queues, jobs, databases, webhooks, and external services. (Plan: P4.1, Requirements: 4, 9) 
- [ ] T4.2 Add normalized flow edge models to the shared repository graph. (Plan: P4.1, Requirements: 4, 9)
- [ ] T4.3 Generate `docs/flows/overview.md` from detected interactions. (Plan: P4.2, Requirement: 9)
- [ ] T4.4 Generate one integration-specific flow doc per major detected integration. (Plan: P4.2, Requirement: 9)
- [ ] T4.5 Generate a Mermaid data-flow or interaction diagram. (Plan: P4.3, Requirements: 8, 9) 
- [ ] T4.6 Add tests using an integration-heavy fixture repo. (Plan: P4.1, P4.2, Requirement: 9)


## Phase 5: Runtime health and EOL

- [ ] T5.1 Detect runtimes and platform versions from manifests, Dockerfiles, CI configs, and other known locations and add them to the repository model. (Plan: P5.1, Requirement: 14)
- [ ] T5.2 Implement endoflife.date client logic to query EOL/support information for each detected runtime/platform. (Plan: P5.2, Requirement: 14)
- [ ] T5.3 Implement generation of `docs/versions.md` with EOL, approaching EOL, and in-support tables, including links to endoflife.date and to the files/lines where versions were found. (Plan: P5.3, Requirement: 14)
- [ ] T5.4 Add tests using fixture repositories with multiple runtimes and versions in different support states. (Plan: P5.1, P5.3, Requirement: 14)

## Phase 6: Enforcement

- [ ] T6.1 Implement `forerunner check` for stale documentation detection. (Plan: P6.1, Requirement: 10)
- [ ] T6.2 Add output diff reporting for stale artifacts. (Plan: P6.1, Requirement: 10)
- [ ] T6.3 Implement pre-commit hook installation support. (Plan: P6.2, Requirement: 11) 
- [ ] T6.4 Implement the four FR6 enforcement modes: warn only; regenerate and allow review; fail on stale docs; fail unless generated changes have been acknowledged by the committer. (Plan: P6.2, Requirement: 11)
- [ ] T6.5 Make the same checks runnable in CI mode. (Plan: P6.3, Requirement: 11) 
- [ ] T6.6 Add tests for stale-doc pass/fail behavior. (Plan: P6.1, P6.2, Requirements: 10, 11)

## Phase 7: Model adapter implementations

- [ ] T7.1 Implement one concrete adapter, such as a local runtime or OpenAI-compatible endpoint, against the Phase 0 interface. (Plan: P7.1, Requirement: 12)
- [ ] T7.2 Add deterministic fallback behavior for non-AI operations. (Plan: P7.2, Requirement: 12)
- [ ] T7.3 Add tests for adapter swapping and no-adapter fallback. (Plan: P7.1, P7.2, Requirement: 12)

## Phase 8: Hardening and policy

- [ ] T8.1 Add fixture repos for single-stack, polyglot, and integration-heavy test coverage. (Plan: P8.1, Requirements: 3 through 12) 
- [ ] T8.2 Add regression tests over generated Markdown and Mermaid outputs, exercising scanning and the shared repository model (Requirements 3–4) through end-to-end runs on the Phase 8 fixtures. (Plan: P8.1, Requirements: 3 through 12)
- [ ] T8.3 Add the custom source-available license file to the repo. (Plan: P8.2, Requirement: 13) 
- [ ] T8.4 Add the human-readable license summary to `README.md`. (Plan: P8.2, Requirement: 13)
- [ ] T8.5 Improve performance and partial-failure handling. (Plan: P8.3, Requirements: 1 through 12)
- [ ] T8.6 Improve logs, help text, and error messages for unsupported stacks or incomplete analysis. (Plan: P8.3, Requirements: 1 through 12)

## Phase 9: Agent skill and plugin distribution

- [ ] T9.1 Create the canonical agent instruction source for codeforerunner usage. (Plan: P9.1, Requirement: 15)
- [ ] T9.2 Add a generic `skills/codeforerunner/SKILL.md` artifact from the canonical instruction source. (Plan: P9.1, Requirement: 15)
- [ ] T9.3 Add Codex plugin metadata and package layout under `plugins/codeforerunner/`. (Plan: P9.2, Requirement: 15)
- [ ] T9.4 Add Claude-compatible skill or plugin metadata and package layout. (Plan: P9.3, Requirement: 15)
- [ ] T9.5 Implement `forerunner agent install`, `forerunner agent uninstall`, and `forerunner agent doctor`. (Plan: P9.4, Requirement: 15)
- [ ] T9.6 Add `--only <target>` support for scoped installs. (Plan: P9.4, Requirement: 15)
- [ ] T9.7 Add thin `install.sh` and `install.ps1` wrappers around the unified installer. (Plan: P9.5, Requirement: 15)
- [ ] T9.8 Add installer tests for metadata validity, idempotency, uninstall ownership, unsupported target reporting, and generic fallback output. (Plan: P9.6, Requirement: 15)
