# codeforerunner Context

codeforerunner is a prompt-first documentation tool for keeping repository knowledge aligned with code. Its language separates prompt-pack tasks from thin runtime wrappers.

## Language

**Architecture Review**:
A documentation task that surfaces repo-grounded opportunities to deepen modules and improve maintainability. The command/path name is `arch-review`; the human-facing title is Architecture Review.
_Avoid_: Architecture audit, refactor report

**Deepening Opportunity**:
A candidate architecture improvement that hides more behavior behind a smaller interface, increasing leverage for callers and locality for maintainers. Architecture Reviews rank Deepening Opportunities but do not implement them.
_Avoid_: Refactor idea, cleanup item

**Agent Onboarding**:
A task that creates or refreshes the instructions and domain vocabulary a coding agent needs before working in a repo. Agent Onboarding may create or update `CONTEXT.md` with conservative glossary terms inferred from stable repo evidence.
_Avoid_: Init docs, setup docs

## Example Dialogue

Dev: "Run arch-review on this repo."

Domain expert: "That means produce an Architecture Review: ranked Deepening Opportunities, grounded in scan evidence, without changing code or proposing final interfaces yet."

Dev: "Run init for this repo."

Domain expert: "That means perform Agent Onboarding: update agent instructions and, when stable terms are evident, maintain the repo glossary in `CONTEXT.md`."
