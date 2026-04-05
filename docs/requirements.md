# Requirements Document

codeforerunner is a Python-built, model-agnostic documentation agent for single-stack and polyglot repositories. The product must generate useful repository documentation in small, testable increments and support ongoing documentation sync through workflow enforcement rather than one-time generation only.

## Requirement 1: Python CLI foundation

**User Story**

As a developer, I want a stable Python CLI foundation so that the project can be installed, run, and extended consistently.

**Acceptance Criteria**

- WHEN the package is installed, THEN the system SHALL expose a `forerunner` CLI command.
- WHEN a user runs `forerunner --help`, THEN the system SHALL display available commands without error.
- WHEN the project is created from source, THEN the system SHALL follow a Python package structure that is safe for incremental expansion.

## Requirement 2: Config loading

**User Story**

As a developer, I want the tool to read `forerunner.config.yaml` so that behavior can be changed without code edits.

**Acceptance Criteria**

- WHEN `forerunner.config.yaml` exists in the repo root, THEN the system SHALL load it and validate known keys.
- WHEN the config file is missing, THEN the system SHALL use sane defaults and continue unless the requested action requires explicit config.
- WHEN the config file is invalid, THEN the system SHALL fail with a clear validation error that identifies the invalid field.

## Requirement 3: Repository detection

**User Story**

As a developer, I want forerunner to detect repository structure and technology boundaries so that later generators have a reliable base model.

**Acceptance Criteria**

- WHEN a repository contains recognizable markers such as `package.json`, `pyproject.toml`, `Gemfile`, or Terraform files, THEN the system SHALL classify the relevant stack areas.
- WHEN multiple supported stacks exist in one repository, THEN the system SHALL record them as separate stack or domain areas in a shared repository model.
- WHEN no supported stack is recognized, THEN the system SHALL return an unknown classification without crashing.

## Requirement 4: Shared repository model

**User Story**

As a developer, I want language-specific findings normalized into a shared model so that the system can document cross-stack behavior instead of isolated files only.

**Acceptance Criteria**

- WHEN analyzers return stack-specific findings, THEN the system SHALL normalize them into one shared repository model.
- WHEN generators run, THEN they SHALL consume the shared model rather than raw analyzer output directly.
- WHEN the model is serialized for debugging or tests, THEN it SHALL expose stack boundaries, entities, integrations, and flow hints in a predictable structure.

## Requirement 5: README generation

**User Story**

As a developer, I want a concise generated README so that contributors can quickly understand the repository and find deeper documentation.

**Acceptance Criteria**

- WHEN `forerunner generate` runs on a supported repo, THEN the system SHALL generate or update `README.md`.
- WHEN the repository is complex, THEN the README SHALL remain concise and link to deeper docs rather than dumping all detail into one file.
- WHEN no meaningful summary can be inferred, THEN the README generator SHALL produce a minimal structured placeholder rather than failing.

## Requirement 6: Stack-specific docs

**User Story**

As a developer, I want docs that match each detected stack so that React areas read like frontend docs, Python areas read like service docs, and Terraform areas read like infrastructure docs.

**Acceptance Criteria**

- WHEN a supported stack is detected, THEN the system SHALL generate a stack-appropriate documentation artifact for that area.
- WHEN a repo contains multiple supported stacks, THEN the system SHALL generate more than one stack-specific artifact.
- WHEN a stack is unsupported, THEN the system SHALL note it in output without blocking supported stacks from being documented.

## Requirement 7: API docs

**User Story**

As a developer, I want API-oriented documentation for supported code elements so that public interfaces can be understood quickly.

**Acceptance Criteria**

- WHEN supported code entities are detected, THEN the system SHALL generate API-oriented documentation for them.
- WHEN signatures or routes can be detected, THEN the generated docs SHALL include them.
- WHEN API extraction is partial, THEN the docs SHALL still be generated with clear limitations rather than silently skipping sections.

## Requirement 8: Diagrams

**User Story**

As a developer, I want Mermaid diagrams so that architecture and dependencies can live in version control alongside the docs.

**Acceptance Criteria**

- WHEN diagram generation is enabled, THEN the system SHALL produce Mermaid-compatible output.
- WHEN a repo contains multiple stack areas, THEN at least one diagram SHALL reflect cross-stack relationships.
- WHEN diagram generation cannot infer enough structure, THEN the system SHALL emit a minimal valid diagram or an explicit limitation note.

## Requirement 9: Integration and data-flow docs

**User Story**

As a developer, I want end-to-end integration and data-flow documentation so that I do not have to spend days reading code to understand how the system works.

**Acceptance Criteria**

- WHEN integrations or flow boundaries are detected, THEN the system SHALL generate human-readable flow documentation.
- WHEN data appears to move across services, jobs, queues, APIs, or storage layers, THEN the system SHALL describe entrypoints, transformations, stores, and exits where possible.
- WHEN multiple stacks interact, THEN the output SHALL include at least one cross-stack interaction summary.

## Requirement 10: Drift detection

**User Story**

As a developer, I want the tool to detect stale docs so that documentation drift can be caught before changes land.

**Acceptance Criteria**

- WHEN generated docs are current, THEN `forerunner check` SHALL exit successfully.
- WHEN generated docs are stale, THEN `forerunner check` SHALL exit non-zero and identify the stale outputs.
- WHEN only unaffected areas changed, THEN the system SHOULD avoid regenerating unrelated artifacts where possible.

## Requirement 11: Workflow enforcement

**User Story**

As a developer, I want pre-commit and CI enforcement so that documentation stays synced over time.

**Acceptance Criteria**

- WHEN enforcement is enabled, THEN the system SHALL support pre-commit integration.
- WHEN configuring the hook, THEN the system SHALL support at least these modes (per FR6): warn only; regenerate and allow review; fail on stale docs; fail unless generated changes have been acknowledged by the committer.
- WHEN configured checks fail, THEN the commit SHALL be blocked in strict mode.
- WHEN CI mode is used, THEN the same stale-doc rules SHALL be enforceable outside local hooks.

## Requirement 12: Model-agnostic execution

**User Story**

As a developer, I want to use my preferred model provider or local runtime so that I am not locked into one vendor or API key workflow.

**Acceptance Criteria**

- WHEN an adapter is configured, THEN the core workflow SHALL invoke it through a stable adapter interface.
- WHEN a different supported adapter is swapped in, THEN the core generation pipeline SHALL not require redesign.
- WHEN no model adapter is configured, THEN deterministic analysis-only operations SHALL still be able to run where applicable.

## Requirement 13: Licensing and product restrictions

**User Story**

As the project owner, I want usage to be broadly allowed while preventing resale or rebranded competing products so that the code can be used widely without becoming someone else's product.

**Acceptance Criteria**

- WHEN the repository is published, THEN it SHALL include the project's source-available license text.
- WHEN the README is generated or maintained, THEN it SHALL include a short human-readable licensing summary.
- WHEN project metadata is documented, THEN the distinction between allowed use and disallowed resale or competing-product use SHALL be explicit.

## Requirement 14: Runtime support and EOL matrix

**User Story**

As a developer, I want a generated runtime and EOL matrix so that I can quickly see which platforms and versions in this repo are supported, approaching end-of-life, or already EOL.

**Acceptance Criteria**

- WHEN runtimes or platform versions are detected in repo config, Docker, CI, or manifest files, THEN the system SHALL record them in the shared repository model.
- WHEN `forerunner generate` runs, THEN the system SHALL query endoflife.date (or a compatible data source) for each detected runtime or platform and determine current support or EOL status.
- WHEN runtimes are classified, THEN the system SHALL generate a `docs/versions.md` file containing tables for: currently EOL, approaching EOL, and in-support versions, including EOL or support end dates and links to where each version was found in the repo.

