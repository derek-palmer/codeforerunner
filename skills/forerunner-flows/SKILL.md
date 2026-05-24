---
name: forerunner-flows
description: Generate narrative flow documentation for key system paths. Use when the user wants to document how data, requests, or jobs move through the system.
---

# forerunner-flows

Generates prose documentation for key system flows: request/response cycles, data pipelines, background jobs, user journeys, and integration paths. Complements diagrams with narrative explanation.

## Activate when

User asks to: document flows, describe how the system works end-to-end, explain data flow, document request lifecycle, write flow documentation.

## Collect this context

- Scan result (run `/forerunner-scan` first)
- Entry-point and routing files
- Key middleware and service layer files
- Background job or queue handler files (if detected)
- External integration clients (if detected)

## Execute

Run `forerunner doc flows` to compose the full prompt with system rules, then execute it.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/flows.md`
- `src/codeforerunner/prompts/system/base.md`
- `src/codeforerunner/prompts/partials/output-rules.md`

## Output

`docs/flows.md` with one section per major flow. Each section: flow name, narrative description, step-by-step trace (actor → component → component), and a Mermaid sequence or flowchart diagram. Append `## Gaps` for flows with insufficient source evidence.
