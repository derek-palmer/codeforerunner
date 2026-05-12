# Claude Project Instructions

Use this project as a prompt-first documentation toolkit.

## Load Order

1. Use `prompts/system/base.md` as project instructions.
2. Read `prompts/partials/context-format.md` before assembling context.
3. Run `prompts/tasks/scan.md` first for every target repo.
4. Feed scan result into one downstream task prompt.

## Rules

- Ground every doc claim in provided files.
- If evidence missing, say so in a `## Gaps` section.
- Do not invent setup commands, env vars, APIs, integrations, or versions.
- Use Markdown output only.

## Common Tasks

- README: `prompts/tasks/readme.md`
- API docs: `prompts/tasks/api-docs.md`
- Stack docs: `prompts/tasks/stack-docs.md`
- Diagrams: `prompts/tasks/diagrams.md`
- Flows: `prompts/tasks/flows.md`
- Version audit: `prompts/tasks/version-audit.md`
- Staleness check: `prompts/tasks/check.md`
- Review summary: `prompts/tasks/review.md`
