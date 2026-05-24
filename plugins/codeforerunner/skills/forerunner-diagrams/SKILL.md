---
name: forerunner-diagrams
description: Generate Mermaid architecture and flow diagrams from a repository's structure. Use when the user wants architecture diagrams, component diagrams, or visual documentation.
---

# forerunner-diagrams

Generates Mermaid diagrams: one master architecture overview plus focused section diagrams for key subsystems. All diagrams grounded in scan evidence.

## Activate when

User asks to: generate diagrams, create architecture diagrams, visualize the system, draw component relationships, produce a Mermaid diagram.

## Collect this context

- Scan result (run `/forerunner-scan` first)
- Entry-point files (up to 5)
- Key module and interface files identified in the scan
- Existing `docs/diagrams.md` (when updating)

## Execute

Run `forerunner doc diagrams` to compose the full prompt with system rules, then execute it.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/diagrams.md`
- `src/codeforerunner/prompts/system/base.md`
- `src/codeforerunner/prompts/partials/output-rules.md`

## Output

`docs/diagrams.md` containing fenced Mermaid code blocks: one top-level architecture diagram + one focused diagram per major subsystem detected. Each diagram preceded by a short prose caption. Never invent components not present in the provided files.
