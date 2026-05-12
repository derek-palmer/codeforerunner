# codeforerunner Specification

## Overview

codeforerunner is a Python-implemented, model-agnostic, AI-assisted repository documentation system built around a finely tuned agent or skill layer plus workflow add-ons such as pre-commit enforcement. Although the implementation is in Python, the target input is polyglot repositories across any language, framework, or infrastructure stack. It analyzes a source repository and produces a documentation set consisting of a primary README, API documentation, architecture diagrams, and integration or data-flow documentation.

The product is intended to work with whatever model stack a user already prefers, rather than forcing a single hosted provider or requiring the project itself to own user API key management. Vendor-agnostic AI architectures typically separate business logic from provider-specific adapters so the underlying model can be swapped without rewriting the system.

## Product intent

The core goal is to let a developer point codeforerunner at a repository and receive useful, reviewable, version-controlled documentation with minimal manual setup. The generated outputs should help a new or existing contributor understand what the system does, how it is structured, how major APIs and components relate to each other, and how data moves across integrations and internal flows.

A second goal is continuous documentation enforcement. Pre-commit hooks are commonly used to stop commits when required checks fail, and they work best when paired with CI so the same rules are enforced even if a local hook is skipped or bypassed.

A third goal is portability across model ecosystems. The project should function as an agent or skill that can be used with OpenAI, Anthropic, Gemini, local models, Ollama, OpenRouter-style routers, or other model endpoints, depending on user preference and local setup.

## Naming convention

- Repository and project name: `codeforerunner`
- CLI command: `forerunner`
- Default config file: `forerunner.config.yaml`

This split keeps the branded repository name descriptive while keeping the command and config filename short and ergonomic for everyday use.

## Product framing

codeforerunner should be treated primarily as:
- a finely tuned AI agent or skill for repository understanding and documentation generation,
- a deterministic orchestration layer around repository scanning and output generation,
- a workflow enforcement layer for keeping docs synchronized over time.

It should not be framed primarily as a hosted AI SaaS product. The value is in the reusable repo functionality, local or bring-your-own-model workflows, and composability inside existing agent stacks.

## Problem statement

Many repositories have outdated, incomplete, or missing documentation because documentation is usually written after code changes rather than as part of the development workflow. That causes drift between implementation and docs, especially in fast-moving projects.

The problem is worse in large repositories with many integrations, pipelines, queues, background jobs, data transformations, and external services. In those systems, understanding the end-to-end flow often takes days of code reading because the most important information is architectural and behavioral rather than local to any single file.

Existing README guidance emphasizes clarity, concise structure, and keeping examples and instructions up to date. When repositories grow, additional documentation should move into dedicated docs rather than overloading the README, which supports codeforerunner's split output model of README plus API docs plus diagrams plus flow docs.

## Primary users

- Solo developers who want a fast way to bootstrap and maintain repository documentation.
- Small engineering teams that want documentation checks enforced before code lands.
- Maintainers of internal tools or services who need architecture visibility and API clarity.
- Teams working in complex integration-heavy repositories who need to understand data flow without reading the entire codebase manually.
- AI-assisted development workflows that need a stable, machine-readable spec and predictable documentation outputs.

## Core use cases

- Generate first-pass docs for an existing repository.
- Regenerate docs after code changes.
- Detect documentation drift before commit.
- Require the committer to review generated documentation updates before finalizing a commit.
- Produce Mermaid diagrams that can live in version control alongside Markdown docs.
- Document end-to-end integration and data flows across modules, services, jobs, queues, and external systems.
- Let users plug codeforerunner into their preferred AI model stack instead of forcing one provider path or one API-key workflow.
- Install codeforerunner as an agent skill or plugin so users can invoke the repository documentation workflow directly from Claude Code, Codex, Gemini, or similar coding agents without manually finding prompt files.

## Scope

### In scope

- Repository scanning and structure analysis.
- AI-assisted summarization of project purpose and code organization.
- README generation.
- API documentation generation for supported languages and frameworks.
- Stack-specific documentation generation for frontend, backend, worker, infrastructure, and other detected repository domains.
- Mermaid diagram generation for architecture, dependency, integration, or flow views.
- Integration and data-flow discovery and explanation.
- Pre-commit integration for doc freshness checks.
- CLI-first workflow.
- Configuration file for include and exclude rules, output paths, enforcement behavior, and model adapter settings.

### Out of scope for initial version

- Full hosted SaaS product.
- Managed billing or centralized user API key storage.
- Multi-user approval system with separate reviewer identities.
- Guaranteed semantic correctness of every AI-generated explanation.
- Deep IDE integration.
- Automatic publishing to external documentation sites.

## Product principles

- Docs should be useful before they are perfect.
- Generated content must be reviewable and editable.
- Documentation should live in the repository and be version-controlled.
- Enforcement should be strict enough to prevent drift, but configurable enough to avoid blocking adoption in messy legacy repos.
- The system should separate concise README content from more detailed docs to avoid bloated top-level documentation.
- Provider-specific model logic should be abstracted behind adapters or interfaces so the repo functionality remains model-agnostic.
- Deterministic analysis and generation steps should be preferred where possible, with AI used to interpret and synthesize rather than to replace every part of the pipeline.

## Polyglot support model

The tool should be implemented in Python, but it must support documentation generation for repositories containing any combination of supported languages, frameworks, and infrastructure definitions. Polyglot analysis approaches commonly use technology-specific extractors or plugins that feed a shared representation, rather than forcing one parser or one language model to understand every stack identically.

The intended operating model is:
- language and framework detectors identify technology boundaries,
- ecosystem-specific analyzers extract useful structure for each area,
- a shared normalized repository model unifies those findings,
- generators create both per-stack docs and cross-stack system documentation.

Examples:
- A React-only repository should get React-oriented documentation.
- A repository containing React, Python, Ruby, and Terraform should get stack-specific docs for each area plus shared architecture and workflow documentation showing how those parts interact.

## Functional requirements

### FR1 Repository analysis

The system shall scan a repository root and identify:
- project structure,
- likely entrypoints,
- major modules or packages,
- supported languages and frameworks,
- stack or domain boundaries such as frontend, backend, worker, shared library, data pipeline, or infrastructure,
- public API surfaces where detectable,
- existing documentation assets,
- likely integration points,
- likely sources, transforms, stores, and sinks of data.

The system should support configurable include and exclude paths so users can ignore generated, vendor, cache, test, or irrelevant directories.

### FR2 README generation

The system shall generate or update a top-level README that may include:
- project summary,
- key capabilities,
- install or setup guidance if inferable,
- usage overview if inferable,
- project structure summary,
- links to deeper documentation,
- architecture or diagram references,
- references to integration and flow documentation where appropriate.

The README should stay concise and point to deeper docs when detail would make the file bloated.

### FR3 API documentation generation

The system shall generate API-oriented documentation for supported code elements such as modules, classes, functions, methods, routes, or service interfaces, depending on language and framework support.

The generated API docs should include signatures or interface shape where available, plain-language descriptions, parameter notes where possible, and links back to source locations when practical.

### FR3a Stack-specific documentation generation

The system shall generate stack-aware documentation for detected repository domains. Examples include frontend application docs for React or other web frameworks, service docs for Python or Ruby applications, and infrastructure docs for Terraform or similar tooling.

These documents should use the conventions and terminology that fit the detected stack rather than forcing one generic template for every technology area.

### FR4 Mermaid diagram generation

The system shall generate Mermaid-compatible diagrams that can be committed directly to the repository as Markdown-embedded Mermaid blocks or Mermaid source files. Mermaid is well suited to version-controlled, text-based diagrams that stay close to the code and docs.

Initial diagram types may include:
- high-level architecture diagrams,
- module dependency graphs,
- service interaction diagrams,
- integration diagrams,
- selected flow diagrams,
- data-flow diagrams.

### FR5 Continuous documentation sync

The system shall provide a mode to evaluate whether documentation is stale relative to current code. This mode should compare source inputs, generated outputs, and config to decide whether regeneration is required.

The system should support both explicit regeneration commands and check-only commands for CI or hooks.

### FR6 Pre-commit enforcement

The system shall provide a pre-commit hook integration that runs before commit finalization. Pre-commit frameworks are commonly used to halt commits when checks fail, making them suitable for documentation freshness enforcement.

The hook behavior should be configurable with at least these modes:
- warn only,
- regenerate and allow review,
- fail on stale docs,
- fail unless generated changes have been acknowledged by the committer.

### FR7 Review acknowledgement

The system shall require an explicit acknowledgement step from the committer before documentation-generated changes are accepted in strict mode.

Possible implementations may include:
- interactive CLI confirmation,
- writing a generated state file or metadata marker,
- requiring staged generated doc changes after regeneration,
- CI confirmation with a documented override or approval workflow.

### FR8 Configuration

The system shall support a root configuration file, such as YAML, TOML, or JSON, with fields for:
- include paths,
- exclude paths,
- output locations,
- enabled generators,
- language hints,
- diagram settings,
- enforcement strictness,
- model adapter selection,
- provider configuration mode,
- verbosity and diff behavior.

### FR9 Extensibility

The system should be designed so language analyzers, generators, output templates, and model adapters can be extended over time without redesigning the whole tool. Modular specs are easier to keep useful as a system grows.

### FR10 Integration and data flow documentation

The system shall analyze supported repositories for integration points and data movement paths, including inbound interfaces, outbound interfaces, internal transformation stages, queues, scheduled jobs, persistence layers, and external services.

The system shall generate documentation that describes:
- where data enters the system,
- which components process or transform the data,
- where data is stored,
- where data exits or is forwarded,
- what major dependencies or external systems are involved,
- what triggers the flow, such as API calls, events, schedules, or file drops.

The system should produce both:
- human-readable narrative summaries of major flows, and
- Mermaid diagrams representing architecture and data movement.

Where possible, the system should identify likely contracts or schemas involved in the flow, such as request payloads, event shapes, database models, or mapped fields.

### FR11 Model-agnostic execution

The system shall support a provider-agnostic execution interface so the same repository analysis and generation workflow can run against different LLM backends, local models, or agent hosts without changing core business logic.

The system should support at least these execution patterns:
- local model runtime,
- bring-your-own-key provider adapters,
- external agent host integration,
- offline or reduced-AI fallback for deterministic analysis-only tasks.

The project should avoid making user API key entry a core assumption of setup. If provider adapters support keys, they should be optional adapter details rather than the product's primary onboarding path.

### FR12 Agent skill and plugin distribution

The system shall provide first-class agent installation artifacts so codeforerunner can be installed as a skill, plugin, or equivalent agent extension instead of requiring users to copy prompts or discover internal files manually.

The distribution should include:
- canonical skill instructions that tell an agent how to run codeforerunner against a target repository,
- Codex plugin metadata and skill packaging,
- Claude plugin metadata and command or skill packaging where supported,
- shared source files for the canonical instructions so each agent package does not drift,
- an installer that detects supported agents and installs only the relevant artifacts,
- idempotent install and uninstall behavior,
- a clear fallback for unsupported agents that writes a portable Markdown skill file and setup instructions.

The installer should be modeled after repos that ship a thin shell or PowerShell wrapper around a unified Node installer. The wrapper should be small, while the Node installer owns detection, file copying, marker-block updates, validation, and uninstall behavior.

Initial supported agent targets should include:
- Codex skill/plugin package,
- Claude Code skill/plugin package,
- generic Markdown skill package for agents that support project or user-level instruction files.

Future targets may include Gemini, Cursor, Windsurf, Cline, Copilot, OpenCode, or other agent hosts if their skill or rule-file conventions become stable enough to support.

The agent-facing instructions should route work through the real CLI and repo-local config. They should not duplicate codeforerunner's full product spec. The skill should tell the agent how to inspect the target repo, choose safe commands, call `forerunner init`, `forerunner generate`, or `forerunner check`, and report changed docs back to the user.

## Non-functional requirements

### NFR1 Developer experience

- CLI commands must be straightforward and discoverable.
- Generated files must be readable and easy to edit by hand.
- Default behavior should work on a typical repository with minimal configuration.
- The project should be usable as a repo tool, agent skill, or reusable workflow component.

### NFR2 Performance

- Initial scans should be reasonable for medium-sized repositories.
- Incremental checks should prefer changed-file or targeted analysis where possible, because pre-commit workflows are most effective when they stay fast and scoped.
- Expensive AI calls should be minimized by reusing structured repository analysis when possible.

### NFR3 Reliability

- The tool must fail clearly when it cannot determine structure or generate content.
- Partial generation failures should report which artifact failed and why.
- The tool should avoid silently overwriting major user-authored content without an explicit strategy.
- Adapter failures should be isolated so one provider integration does not require changes to core repo analysis.

### NFR4 Auditability

- Generated outputs should be deterministic enough that changes are reviewable in Git.
- Regeneration should produce understandable diffs.
- The system should log why a file changed when possible.
- The system should distinguish deterministic findings from AI-inferred summaries when practical.

### NFR5 Security and privacy

- The system must clearly define whether source code is processed locally, remotely, or both.
- Secret files, environment files, and excluded paths must never be sent to an external model provider unless explicitly configured.
- Local-first and provider-agnostic workflows should be treated as first-class design goals.

### NFR6 Agent package maintainability

- Agent packages must derive from shared source instructions where practical.
- Generated package artifacts must be testable for file presence, metadata validity, and idempotent install behavior.
- Installers must avoid overwriting unrelated user content.
- Any injected global instruction blocks must use stable begin/end markers so uninstall can remove only codeforerunner-owned content.
- Agent-specific packages should stay thin and point back to the CLI, config, and docs rather than duplicating product behavior.


## Licensing direction

The project is intended to be source-available rather than OSI open source. Source-available licenses make source code available while imposing restrictions that standard open-source licenses do not, such as limits on redistribution or productization.

The intended licensing posture is:
- allow personal, educational, and commercial use,
- allow modification for internal use,
- forbid selling the software itself as a product,
- forbid selling modified or integrated versions where codeforerunner provides material functionality,
- forbid rebranding a fork as a competing official product.

This posture is closer to a custom source-available or not-for-resale style license than to a conventional permissive or copyleft open-source license.

### Licensing risks

Because custom or source-available licenses can introduce legal ambiguity and extra review burden, adopters may treat them as higher-risk than standard licenses, especially in company environments with strict compliance rules.

The final license text should be reviewed by counsel before public release, especially around terms such as "material functionality", "internal use", and "competing product", which may otherwise be interpreted inconsistently across jurisdictions.

## Proposed architecture

### High-level layers

- Repository scanner
- Technology detectors
- Ecosystem-specific analyzers
- Structure normalizer
- Integration and flow detector
- Documentation generators
- Mermaid diagram generator
- Drift detector
- Enforcement layer
- Model adapter interface
- CLI and config layer
- Agent skill/plugin packaging layer
- Cross-agent installer layer

### Architectural principle

Business logic should be separated from model-provider specifics through a stable adapter boundary. Unified interfaces and adapter patterns are a common way to keep vendor-specific details from leaking into the rest of the system.

The same separation should apply to repository analysis. Technology-specific analyzers should feed a shared intermediate representation so that React, Python, Ruby, Terraform, and future ecosystems can contribute findings into one system model instead of producing isolated islands of documentation.

### Suggested internal pipeline

1. Scan files and detect project, stack, and technology boundaries.
2. Run ecosystem-specific analyzers for each supported area.
3. Detect code entities, integration points, and flow hints.
4. Normalize findings into a shared intermediate representation or repository graph.
5. Use deterministic rules to assemble candidate documentation structure.
6. Use AI only where interpretation, summarization, or explanation adds value.
7. Render Markdown and Mermaid outputs for both stack-specific and cross-stack docs.
8. Compare outputs against current files for drift detection.
9. Enforce review and update rules in hook or CI contexts.

### Agent distribution architecture

The agent distribution should have one canonical source of truth and generated or copied package outputs:

```text
agent/
  codeforerunner.skill.md
  templates/
    codex-plugin.json
    claude-plugin.json
    generic-skill.md
bin/
  install-agent.js
install.sh
install.ps1
plugins/
  codeforerunner/
    .codex-plugin/
      plugin.json
    skills/
      codeforerunner/
        SKILL.md
.claude-plugin/
  plugin.json
skills/
  codeforerunner/
    SKILL.md
```

The exact paths may change once Codex and Claude package conventions are validated, but the ownership model should stay stable:
- `agent/codeforerunner.skill.md` is the canonical agent instruction source.
- `skills/codeforerunner/SKILL.md` is the generic skill artifact.
- `plugins/codeforerunner/.codex-plugin/plugin.json` is Codex plugin metadata.
- `.claude-plugin/plugin.json` is Claude plugin metadata if Claude plugin hooks are needed.
- `bin/install-agent.js` owns target detection, install, uninstall, and validation.
- `install.sh` and `install.ps1` are thin launchers only.

Supported installer commands should include:

```bash
forerunner agent install
forerunner agent install --only codex
forerunner agent install --only claude
forerunner agent uninstall
forerunner agent doctor
```

The direct shell install path may also be supported after packaging:

```bash
curl -fsSL https://raw.githubusercontent.com/derek-palmer/codeforerunner/main/install.sh | bash
```

The installer should:
- detect known agent config roots,
- copy codeforerunner-owned skill/plugin files,
- append marker-fenced instruction blocks only when an agent requires global injected context,
- avoid duplicate blocks on rerun,
- remove only marker-fenced or owned files on uninstall,
- print exact installed targets and skipped targets.

The Codex package should prefer a plugin with a `skills/` directory and `plugin.json` interface metadata. The skill should trigger on repository documentation generation, README/API/diagram/flow documentation, stale-doc checks, and pre-commit or CI documentation enforcement setup.

The Claude package should support either Claude's skill directory convention, Claude plugin metadata, or both, depending on current Claude Code capabilities. Any hooks should be limited to activation or command routing and must not silently run code generation against user repos.

## Proposed outputs

### Repository files

A likely output layout for an early version is:

```text
README.md
docs/
  api/
  apps/
  services/
  infrastructure/
  diagrams/
  flows/
forerunner.config.yaml
```

### Example generated artifacts

- `README.md`
- `docs/api/<module>.md`
- `docs/apps/<frontend-name>.md`
- `docs/services/<service-name>.md`
- `docs/infrastructure/<stack-name>.md`
- `docs/diagrams/architecture.md`
- `docs/diagrams/dependencies.md`
- `docs/diagrams/dataflow.md`
- `docs/flows/overview.md`
- `docs/flows/<integration-name>.md`
- `.codeforerunner/state.json` or similar metadata for generation checks
- `skills/codeforerunner/SKILL.md`
- `plugins/codeforerunner/.codex-plugin/plugin.json`
- `.claude-plugin/plugin.json`
- `install.sh`, `install.ps1`, and `bin/install-agent.js`

## CLI concept

Illustrative commands:

```bash
forerunner init
forerunner generate
forerunner check
forerunner review
forerunner hook install
forerunner agent install
forerunner agent uninstall
forerunner agent doctor
forerunner config init
forerunner adapters list
```

The exact command surface can evolve, but the separation between generate, check, and enforcement flows should remain clear because specs are most useful when externally visible behaviors are explicit.

## Suggested workflow

### Initial bootstrap

1. User installs codeforerunner.
2. User runs `forerunner init` in a repository.
3. Tool detects language, framework, structure, and likely integration or flow boundaries.
4. Tool writes config and initial documentation outputs.
5. User reviews and edits generated docs.
6. User optionally installs the enforcement hook.

### Ongoing workflow

1. Developer changes code.
2. Pre-commit hook or explicit command runs `forerunner check`.
3. Tool detects stale documentation.
4. Tool regenerates or prompts, depending on config.
5. Developer reviews generated changes.
6. Commit proceeds only if configured documentation requirements are satisfied.

### Model integration workflow

1. User chooses a supported adapter or host integration.
2. User points codeforerunner at an existing local model, agent host, or provider-backed adapter.
3. codeforerunner sends only the structured inputs needed for the current task, subject to include, exclude, and privacy rules.
4. Returned summaries are merged into deterministic output templates.

## Suggested Python package layout

A Python implementation should use a `src/` layout and expose the CLI through a standard package entry point, which is consistent with modern Python packaging guidance for installable command-line tools.

Illustrative package layout:

```text
src/
  codeforerunner/
    cli.py
    config.py
    detectors/
    analyzers/
      react/
      python/
      ruby/
      terraform/
    graph/
    generators/
    adapters/
    enforcement/
```

The analyzers directory should be ecosystem-specific, while the graph or normalized-model layer should remain shared across the whole tool. This keeps the implementation language in Python while preserving polyglot repository support.

## Acceptance criteria

### MVP acceptance criteria

- Running the tool against a supported repository produces a top-level README, at least one stack-specific or API documentation artifact, and at least one Mermaid diagram artifact.
- The tool can generate at least one integration or data-flow artifact for a supported repository with recognizable flow boundaries.
- In a polyglot repository, the tool can document more than one stack area and produce at least one cross-stack interaction summary.
- Generated files are valid Markdown and safe to commit.
- The tool supports a config file with include and exclude controls.
- A check mode exits successfully when docs are current and non-zero when docs are stale.
- A pre-commit integration can block commits when configured checks fail.
- Regenerated content produces reviewable file diffs in Git.
- The core logic can invoke at least two different model backends through the same adapter interface or run in a reduced deterministic mode without changing the rest of the pipeline.

### Quality acceptance criteria

- README output remains concise and links to deeper documentation rather than becoming a dump of all generated content.
- The tool does not scan excluded paths.
- Errors identify the failing stage, such as scan, summarize, generate, diagram, flow-detect, or enforce.
- The tool can operate on a repository with existing documentation without destroying user content by default.
- Flow documentation makes a reasonable attempt to identify entrypoints, transformations, storage, and exits in supported repositories.

## Open decisions

- Local-only model support versus hosted model support.
- Whether README generation is full replacement, section-managed, or patch-based.
- How review acknowledgement should be represented technically.
- Which languages and frameworks are supported in MVP, and in what order analyzers are added.
- Whether diagrams are generated as embedded Mermaid blocks, `.mmd` files, or both.
- Which adapters should be first-class in MVP, such as local CLI, Ollama, OpenAI-compatible endpoints, or external agent hosts.
- Whether hook enforcement alone is sufficient or CI must also be recommended, since client-side hooks can be bypassed and teams often reinforce policy in CI.

## AI-agent build instructions

An AI agent implementing this specification should work in this order:

1. Define the project structure, packaging approach, and **adapter interface** as real modules before building AI-assisted generators, so generation and orchestration never depend on a concrete provider SDK first.
2. Implement repository scanning and config loading.
3. Implement technology detection and analyzer registration.
4. Implement a normalized internal representation of repository structure, integrations, and flow hints.
5. Implement deterministic README and doc skeleton generation.
6. Implement stack-specific documentation generation for one ecosystem first, then expand.
7. Implement Mermaid diagram generation from the same normalized representation.
8. Implement integration and data-flow summarization from the normalized representation.
9. Implement check mode for drift detection.
10. Implement pre-commit hook installation and enforcement behavior.
11. Add tests using small fixture repositories, including at least one integration-heavy and one polyglot fixture.
12. Document analyzer limitations and unsupported constructs explicitly.
13. Add agent skill/plugin packaging after the core CLI contract is stable enough for agent instructions to call it without churn.

This order matches `docs/plan.md`: the adapter **interface** belongs in Phase 0 foundations; a first **concrete adapter** and deeper fallback behavior land in a later phase after generators are exercising the interface.

The agent should keep requirements separate from implementation details when possible, because specs are easier to maintain when the product behavior remains stable even as internal design evolves.
