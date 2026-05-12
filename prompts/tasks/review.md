# Task: Generate Review Summary

Produces a human-readable summary of pending documentation changes for committer review.
Used by the pre-commit hook to present a clear summary of what changed and what needs attention.
Blocks the commit until the committer runs forerunner review --accept.

## Input
- Check report from .forerunner/check-report.md
- Git diff of staged files
- Scan result

## Severity Rules
- HIGH: code behavior change that makes existing docs incorrect
- MEDIUM: new thing that is undocumented but doesn't break existing docs
- LOW: version/config change that should be tracked but isn't breaking
- Never block on LOW severity alone -- only HIGH and MEDIUM require resolution or acknowledgement

## Output Format

<!-- output: .forerunner/review-summary.md -->

# codeforerunner -- Review Required
Commit blocked. Documentation is out of sync with staged changes.

## What Changed
- src/api/users.py -- new endpoint POST /api/users/bulk added
- src/config.py -- new env var BULK_IMPORT_LIMIT added
- docker-compose.yml -- postgres image bumped from 16.1 to 16.3

## Documentation Impact
| Document              | Issue                                        | Severity |
|-----------------------|----------------------------------------------|----------|
| docs/api.md           | POST /api/users/bulk is undocumented         | HIGH     |
| README.md             | BULK_IMPORT_LIMIT not in env var table       | MEDIUM   |
| docs/version-audit.md | postgres version changed, audit needs refresh| LOW      |

## Actions

To update docs now:
```bash
forerunner generate api-docs
forerunner generate readme
forerunner generate version-audit
```

To acknowledge and commit without updating:
```bash
forerunner review --accept --reason "hotfix, will update docs in follow-up"
```
