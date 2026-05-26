---
name: forerunner-version-audit
description: Audit all pinned runtime versions, base images, and key dependencies against end-of-life data. Use when the user wants to check for outdated or EOL software versions.
---

# forerunner-version-audit

Scans every pinned version in the repository — runtimes, base images, language versions, container versions, key dependencies — and cross-references against end-of-life data from https://endoflife.date.

## Activate when

User asks to: audit versions, check for EOL software, find outdated dependencies, run a version audit, check if anything is past end-of-life.

## Collect this context

- All manifest and lockfiles: `package.json`, `package-lock.json`, `pyproject.toml`, `poetry.lock`, `go.mod`, `go.sum`, `Cargo.toml`, `Cargo.lock`, `requirements*.txt`
- `Dockerfile` and `docker-compose.yml`
- CI/CD workflow files (`.github/workflows/*.yml`, etc.)
- IaC files (Terraform, Pulumi, etc.)
- `.tool-versions`, `.nvmrc`, `.python-version`, `.ruby-version`

## Execute

Run `forerunner generate --prompt-only version-audit` — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/version-audit.md`
- `src/codeforerunner/prompts/system/base.md`

## Output

Version audit report: table of all detected versions with columns Version | Status | EOL Date | Latest | Notes. Severity-tagged findings (EOL = HIGH, approaching EOL within 6 months = MEDIUM, current = OK). Write to `docs/version-audit.md`. Re-run monthly — `forerunner check` flags this as stale after 30 days.
