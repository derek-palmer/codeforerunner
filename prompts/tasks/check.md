# Task: Check Documentation Staleness

Evaluates whether existing documentation is stale relative to the current codebase.
Designed for manual agent use now and future hook/CLI wrappers later.

## Input
- Scan result (run fresh)
- Existing documentation files (README.md, docs/*.md)
- .forerunner/state.json (last-run checksums, if present)
- Git diff of changed files (if running from pre-commit hook)

## What to Check
1. README accuracy: do setup steps, env vars, and usage match current codebase?
2. API docs accuracy: do documented endpoints still exist? New undocumented ones?
3. Diagram accuracy: do documented flows/components match scan result?
4. Version audit currency: is there an existing audit? Is it older than 30 days?
5. New modules: directories in scan result with no corresponding documentation?
6. Removed modules: documentation referencing files that no longer exist?

## Staleness Classification
| Status       | Meaning                                               |
|--------------|-------------------------------------------------------|
| CURRENT      | Documentation matches codebase                        |
| STALE        | Documentation is outdated -- specific issues found    |
| MISSING      | No documentation exists for a detected component      |
| UNVERIFIABLE | Insufficient context to determine staleness           |

## Output Format

<!-- output: .forerunner/check-report.md -->

# Documentation Check Report
Generated: YYYY-MM-DD

## Summary
Overall status: STALE

| Document              | Status  | Issue                                              |
|-----------------------|---------|----------------------------------------------------|
| README.md             | STALE   | DATABASE_URL env var missing from config section   |
| docs/api.md           | STALE   | /api/v2/webhooks endpoint undocumented             |
| docs/diagrams.md      | CURRENT | --                                                 |
| docs/version-audit.md | STALE   | Last generated 45 days ago                         |

## Details

### README.md -- STALE
- Missing env var: REDIS_URL appears in src/config.py but not in README
- Outdated command: setup step references npm install but package.json uses pnpm

### docs/api.md -- STALE
- New undocumented endpoint: POST /api/v2/webhooks found in src/api/webhooks.py
- Removed endpoint: DELETE /api/v1/users/:id is documented but handler no longer exists

## Recommended Actions
1. Re-run `prompts/tasks/readme.md`
2. Re-run `prompts/tasks/api-docs.md`
3. Re-run `prompts/tasks/version-audit.md` (audit is >30 days old)
