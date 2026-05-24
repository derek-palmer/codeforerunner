# Claude Project Instructions

Use this project as a prompt-first documentation toolkit.

## Load Order

1. Run `forerunner doc scan` to get the assembled system + partials + scan bundle, or read `src/codeforerunner/prompts/system/base.md` from source.
2. Read `partials/context-format.md` before assembling context.
3. Run `scan` first for every target repo.
4. Feed scan result into one downstream task prompt.

## Rules

- Ground every doc claim in provided files.
- If evidence missing, say so in a `## Gaps` section.
- Do not invent setup commands, env vars, APIs, integrations, or versions.
- Use Markdown output only.

## Common Tasks

- README: `forerunner doc readme`
- API docs: `forerunner doc api-docs`
- Stack docs: `forerunner doc stack-docs`
- Diagrams: `forerunner doc diagrams`
- Flows: `forerunner doc flows`
- Version audit: `forerunner doc version-audit`
- Staleness check: `forerunner doc check`
- Review summary: `forerunner doc review`
- Security audit: `forerunner doc audit`
- Changelog entry: `forerunner doc changelog`
