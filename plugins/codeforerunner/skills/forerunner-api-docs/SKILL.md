---
name: forerunner-api-docs
description: Generate endpoint-level API documentation from route and handler files. Use when the user wants to document a public API or REST endpoints.
---

# forerunner-api-docs

Generates API reference documentation at the endpoint level. Requires scan result and all route/handler files in context.

## Activate when

User asks to: document the API, generate API reference, write endpoint docs, create OpenAPI-style documentation.

## Collect this context

- Scan result (run `/forerunner-scan` first)
- All route/handler files (every file the scan identified as an API entry point)
- Middleware files
- Auth and validation logic (for request/response shapes)
- Existing API docs (when updating)

## Execute

Run `forerunner generate --prompt-only api-docs` — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/api-docs.md`
- `src/codeforerunner/prompts/system/base.md`
- `src/codeforerunner/prompts/partials/output-rules.md`

## Output

Structured API reference covering: endpoint list, HTTP method, path, auth requirement, request parameters/body, response shape, status codes. Write to `docs/api.md` or return as Markdown. Append `## Gaps` for endpoints without sufficient source evidence.
