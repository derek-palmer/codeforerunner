# Task: Generate README

Generates or rewrites the top-level README.md.
Requires scan result as input.

## Input
- Scan result
- Existing README.md (if present)
- Entry point file contents
- Key module file contents (up to 10)

## Required Sections
1. Title + one-line description
2. Stack (language, framework, key dependencies as table)
3. Prerequisites
4. Setup (step-by-step, copy-pasteable commands)
5. Configuration (every env var: Variable | Required | Default | Description)
6. Usage (how to run; key endpoints for APIs, key commands for CLIs)
7. Project Structure (file tree snippet of key directories)

## Conditional Sections (include if applicable)
- Testing: if test framework detected
- Deployment: if CI/CD or infra code present
- Architecture: link to docs/diagrams.md if it exists
- Contributing: if library or open-source

## Rules
- Never use placeholder text
- All code examples use actual filenames and real commands from the codebase
- Project structure uses a file tree snippet, not a bulleted list
- Claims must derive from provided files. If evidence is absent, omit or document in `## Gaps`.

## Output
<!-- output: README.md -->
