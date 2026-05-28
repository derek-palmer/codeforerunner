---
name: forerunner-arch-review
description: Rank architecture improvement candidates. Use when the user wants architecture friction reviewed before planning refactors.
---

# forerunner-arch-review

Produces an Architecture Review: ranked Deepening Opportunities that identify shallow modules, leaky seams, testability friction, and high-leverage refactor candidates.

Inspired by Matt Pocock's `/improve-codebase-architecture` skill:
https://github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture

## Activate when

User asks to: review architecture, find deepening opportunities, identify shallow modules, assess refactor candidates, or improve codebase architecture.

## Collect this context

- Scan result (run `/forerunner-scan` first)
- Key module/package files from the scan result
- Existing tests for the modules under review
- `CONTEXT.md` or `CONTEXT-MAP.md` if present
- Relevant `docs/adr/*.md` files if present
- Existing architecture docs only when they clarify current design

## Execute

Run `forerunner generate --prompt-only arch-review` — outputs the assembled prompt bundle to stdout. Read this output and execute the architecture review task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/arch-review.md`
- `src/codeforerunner/prompts/system/base.md`
- `src/codeforerunner/prompts/partials/output-rules.md`

## Output

`.forerunner/arch-review.md` with a top recommendation and 3-7 ranked Deepening Opportunities. Each candidate includes files/modules, problem, evidence, proposed direction, locality/leverage benefits, testing impact, risk/blast radius, and recommendation strength. Do not implement changes or propose final interfaces.
