---
name: forerunner-audit
description: Run a security and dependency audit against a repository. Use when the user wants a security review, dependency vulnerability check, or supply-chain audit.
---

# forerunner-audit

Produces a structured security and dependency audit report. Covers known vulnerability patterns, dependency hygiene, secret exposure risks, and supply-chain concerns.

## Activate when

User asks to: audit the repo, run a security check, check for vulnerabilities, review dependencies for security issues.

## Collect this context

- Scan result (run `/forerunner-scan` first)
- All manifest and lockfiles: `package.json`, `package-lock.json`, `yarn.lock`, `pyproject.toml`, `poetry.lock`, `requirements*.txt`, `go.mod`, `go.sum`, `Cargo.toml`, `Cargo.lock`, `Gemfile.lock`
- CI/CD workflow files
- Dockerfile and compose files
- `.env.example` or similar (never actual secret files)

## Execute

Run `forerunner generate --prompt-only audit` — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/audit.md`
- `src/codeforerunner/prompts/system/base.md`

## Output

Structured audit report covering: outdated/vulnerable dependencies, hardcoded secrets risk surface, CI security posture, supply-chain exposure. Severity-tagged findings (HIGH / MEDIUM / LOW). Write to `docs/audit.md` or return as Markdown.
