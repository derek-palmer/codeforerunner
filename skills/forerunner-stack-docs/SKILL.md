---
name: forerunner-stack-docs
description: Generate stack-specific developer documentation. Use when the user wants deep technical docs for a specific part of the stack — database schema, service interfaces, configuration reference, etc.
---

# forerunner-stack-docs

Generates developer documentation tailored to the detected stack. Template selected based on scan result: backend API, frontend SPA, CLI tool, data pipeline, ML service, etc.

## Activate when

User asks to: generate developer docs, document the stack, write technical documentation, create a developer guide, document the database schema / service layer / config reference.

## Collect this context

- Scan result (run `/forerunner-scan` first)
- Key module files for the detected stack (schema files, service interfaces, config loaders, handler files)
- Type definitions or interface files
- Configuration documentation (env vars, config schemas)

## Execute

Run `forerunner generate --prompt-only stack-docs` — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/stack-docs.md`
- `src/codeforerunner/prompts/system/base.md`
- `src/codeforerunner/prompts/partials/stack-hints.md`

## Output

Stack-specific `docs/stack.md` covering: architecture decisions, key interfaces, configuration reference, data model, extension points. Format and depth matched to detected stack type. Append `## Gaps` for areas with insufficient source evidence.
