# codeforerunner Context

codeforerunner is a prompt-first documentation tool for keeping repository knowledge aligned with code. Its language separates prompt-pack tasks from thin runtime wrappers.

## Language

**Architecture Review**:
A documentation task that surfaces repo-grounded opportunities to deepen modules and improve maintainability. The command/path name is `arch-review`; the human-facing title is Architecture Review.
_Avoid_: Architecture audit, refactor report

**Deepening Opportunity**:
A candidate architecture improvement that hides more behavior behind a smaller interface, increasing leverage for callers and locality for maintainers. Architecture Reviews rank Deepening Opportunities but do not implement them.
_Avoid_: Refactor idea, cleanup item

**Task Registry**:
A catalog of codeforerunner task identity and policy: task name, output role, refresh inclusion, scan exemption, and installable skill surface. It is the source agents and wrappers consult instead of rediscovering task facts from scattered files.
_Avoid_: Task list, command list

**Prompt Session**:
A run-scoped interaction with codeforerunner prompt tasks that owns task lookup, scan-first enforcement, scan state, and bundle resolution. CLI and MCP code act as adapters to a Prompt Session rather than each reimplementing task ordering rules.
_Avoid_: Prompt runner, execution context

**Distribution Inventory**:
A catalog of codeforerunner distribution artifacts and install policy: canonical skill, skill copies, per-task skills, marketplace manifest, managed markers, and default install destinations. Installer, doctor, and validators consult the Distribution Inventory instead of repeating packaging paths.
_Avoid_: Package list, artifact list

**npm Publishing**:
The release path that makes the Node installer package available through npm-compatible registries. codeforerunner treats npmjs publishing, GitHub Packages publishing, and pinned installer shims as related but separately fixable release surfaces.
_Avoid_: JavaScript release, package upload

**Release Surface Manifest**:
A catalog of release surfaces, versions, registry targets, authentication modes, and validation expectations for codeforerunner releases. npm Publishing uses it to keep npmjs, GitHub Packages, installer shims, Socket badge URL, and release PR checks aligned.
_Avoid_: Release checklist, publish config

**Package Contents Inspector**:
A release validation module that checks the packed npm artifact before publish, including required files, executable entrypoints, skill payloads, lock metadata, and shim pins. It treats the package artifact as the test surface.
_Avoid_: npm pack script, file list check

**Agent Onboarding**:
A task that creates or refreshes the instructions and domain vocabulary a coding agent needs before working in a repo. Agent Onboarding may create or update `CONTEXT.md` with conservative glossary terms inferred from stable repo evidence.
_Avoid_: Init docs, setup docs

## Example Dialogue

Dev: "Run arch-review on this repo."

Domain expert: "That means produce an Architecture Review: ranked Deepening Opportunities, grounded in scan evidence, without changing code or proposing final interfaces yet."

Dev: "Run init for this repo."

Domain expert: "That means perform Agent Onboarding: update agent instructions and, when stable terms are evident, maintain the repo glossary in `CONTEXT.md`."

Dev: "Add a new prompt task."

Domain expert: "Register it in the Task Registry so wrappers, skills, docs, and refresh policy read the same task identity."

Dev: "Why does scan-first logic exist in both CLI and MCP?"

Domain expert: "That rule belongs to a Prompt Session: adapters should ask the session whether a task can run."

Dev: "Where should canonical skill paths and marketplace paths live?"

Domain expert: "In the Distribution Inventory, so installer, doctor, and validators share distribution facts."

Dev: "Fix npm publishing."

Domain expert: "Treat npm Publishing as three release surfaces: npmjs trusted publish, GitHub Packages publish, and installer shim pins."

Dev: "How do we keep release workflows aligned?"

Domain expert: "Use a Release Surface Manifest, then validate packed npm artifacts with a Package Contents Inspector before publish."
