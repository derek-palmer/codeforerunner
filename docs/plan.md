# Implementation Plan

This plan breaks codeforerunner into small, independently shippable slices. Spec-driven development workflows are most effective when requirements, plan, and tasks are separated, and each task can be validated in isolation.

**Adapter boundary:** The model adapter **interface** is defined in Phase 0 (P0.4) before any AI-assisted generation work in Phases 2 onward. Phases 2–6 implement generators and enforcement against that interface so code does not depend on a concrete LLM provider and later “adapter refactors” are avoided. Phase 7 adds a first concrete adapter and strengthens deterministic fallback.

## Phase 0: Foundations

### Plan Item P0.1: Python package and CLI scaffold
- **Priority:** High
- **Covers:** Requirement 1
- Create the Python package layout, `pyproject.toml`, and the `forerunner` CLI entry point.

### Plan Item P0.2: Config loader and validation
- **Priority:** High
- **Covers:** Requirement 2
- Add support for `forerunner.config.yaml`, defaults, and validation errors.

### Plan Item P0.3: Base domain models and logging
- **Priority:** High
- **Covers:** Requirements 1, 4
- Define the initial internal models and structured logging needed for future phases.

### Plan Item P0.4: Model adapter interface
- **Priority:** High
- **Covers:** Requirement 12
- Define the stable adapter protocol (types, lifecycle, and how orchestration passes an adapter into pipelines) used for all model-backed calls. Generators and other code that need an LLM SHALL depend only on this interface, not on a specific provider SDK.

## Phase 1: Repository understanding

### Plan Item P1.1: Repository scanner
- **Priority:** High
- **Covers:** Requirement 3
- Build a scanner that walks a repo, respects include and exclude settings, and detects root markers.

### Plan Item P1.2: Technology detection
- **Priority:** High
- **Covers:** Requirement 3
- Detect basic stack areas such as React, Python, Ruby, and Terraform from file markers and config patterns.

### Plan Item P1.3: Shared repository model
- **Priority:** High
- **Covers:** Requirement 4
- Normalize scanner and detector output into one predictable repository model.

## Phase 2: First generated docs

### Plan Item P2.1: README generator
- **Priority:** High
- **Covers:** Requirement 5
- Generate a concise top-level README from the shared model.

### Plan Item P2.2: First stack-specific docs
- **Priority:** High
- **Covers:** Requirement 6
- Generate one stack-aware doc type for each initially supported ecosystem.

### Plan Item P2.3: Basic diagram generation
- **Priority:** Medium
- **Covers:** Requirement 8
- Generate a minimal Mermaid architecture or dependency diagram.

## Phase 3: Deeper code understanding

### Plan Item P3.1: API docs for first ecosystem
- **Priority:** High
- **Covers:** Requirement 7
- Add API documentation generation for the first supported language or framework.

### Plan Item P3.2: Additional stack analyzers
- **Priority:** Medium
- **Covers:** Requirements 3, 6, 7
- Expand analyzers beyond the first ecosystem in small steps.

## Phase 4: Cross-stack system understanding

### Plan Item P4.1: Integration detection
- **Priority:** High
- **Covers:** Requirements 4, 9
- Detect integration points such as HTTP clients, queues, jobs, databases, webhooks, and external services.

### Plan Item P4.2: Data-flow summaries
- **Priority:** High
- **Covers:** Requirement 9
- Generate human-readable docs that explain where data enters, changes, and exits the system.

### Plan Item P4.3: Flow diagrams
- **Priority:** Medium
- **Covers:** Requirements 8, 9
- Generate Mermaid diagrams for major cross-stack interactions and data flow.


## Phase 5: Runtime health and EOL

### Plan Item P5.1: Runtime and platform detection
- **Priority:** Medium
- **Covers:** Requirement 14
- Detect runtime and platform versions from configuration, manifest, Docker, and CI files and store them in the repository model.

### Plan Item P5.2: endoflife.date integration
- **Priority:** Medium
- **Covers:** Requirement 14
- Query endoflife.date (or a compatible source) for detected runtimes to obtain EOL and support dates and classify versions by status.

### Plan Item P5.3: Versions documentation generator
- **Priority:** Medium
- **Covers:** Requirement 14
- Generate `docs/versions.md` containing tables for current EOL, approaching EOL, and in-support versions, including links to endoflife.date and to where each version is found in the repo.

## Phase 6: Enforcement

### Plan Item P6.1: Drift detection
- **Priority:** High
- **Covers:** Requirement 10
- Add check mode and output comparison logic.

### Plan Item P6.2: Pre-commit integration
- **Priority:** High
- **Covers:** Requirement 11
- Add hook installation and configurable enforcement aligned with FR6: warn only; regenerate and allow review; fail on stale docs; fail unless generated changes have been acknowledged by the committer.

### Plan Item P6.3: CI parity
- **Priority:** Medium
- **Covers:** Requirement 11
- Ensure the same enforcement rules can run in CI outside local hooks.

## Phase 7: Model adapter implementations

### Plan Item P7.1: First adapter implementation
- **Priority:** High
- **Covers:** Requirement 12
- Implement one concrete adapter against the Phase 0 interface, ideally local-first or OpenAI-compatible.

### Plan Item P7.2: Deterministic fallback behavior
- **Priority:** Medium
- **Covers:** Requirement 12
- Ensure non-AI or reduced-AI operations remain available where possible, and that behavior is consistent with the adapter interface from P0.4.

## Phase 8: Hardening and policy

### Plan Item P8.1: Fixture repos and regression tests
- **Priority:** High
- **Covers:** Requirements 3 through 12
- Add single-stack, integration-heavy, and polyglot fixture repos for repeatable tests, and regression tests that validate outputs end-to-end from scanning and modeling (Requirements 3–4) through generated docs, diagrams, enforcement, and adapters (Requirements 5–12).

### Plan Item P8.2: License and README policy text
- **Priority:** Medium
- **Covers:** Requirement 13
- Add the source-available license and the short README licensing summary.

### Plan Item P8.3: Performance and UX hardening
- **Priority:** Medium
- **Covers:** Requirements 1 through 12
- Improve speed, logs, error messages, and partial-failure handling.
