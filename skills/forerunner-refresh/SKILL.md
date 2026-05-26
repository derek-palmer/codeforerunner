---
name: forerunner-refresh
description: Scan repo, check all docs for staleness, then generate or update every stale or missing doc in one pass. Use when the user wants to update all docs, refresh docs, or sync documentation with the current codebase.
---

# forerunner-refresh

Runs a full documentation refresh cycle: scan → check → generate/update all stale or missing docs.

## Activate when

User asks to: update all docs, refresh documentation, sync docs with code, run a doc sweep, or "update everything."

## Execute

Run `forerunner refresh` (or `forerunner doc refresh`) to output all task bundles in sequence. Execute each bundle in order:

1. **scan** — collect repo evidence
2. **check** — identify stale or missing docs
3. For each stale/missing: **readme** → **api-docs** → **stack-docs** → **diagrams** → **flows** → **version-audit**

Skip any task where check shows `CURRENT` status.

## Output

Write each artifact to its task-defined output path. Append `## Gaps` wherever evidence is insufficient. Report a summary of what was updated.
