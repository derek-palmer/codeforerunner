---
name: forerunner-refresh
description: Scan repo, check all docs for staleness, then generate or update every stale or missing doc in one pass. Use when the user wants to update all docs, refresh docs, or sync documentation with the current codebase.
---

# forerunner-refresh

Runs a full documentation refresh cycle: scan → check → generate/update all stale or missing docs.

## Activate when

User asks to: update all docs, refresh documentation, sync docs with code, run a doc sweep, or "update everything."

## Execute

Run each step in order, processing the result before moving to the next:

1. **Scan** — `forerunner doc scan` → capture YAML output as the scan result
2. **Check** — `forerunner doc check` → identify every doc with `STALE` or `MISSING` status
3. **For each stale/missing** — run the corresponding task in this order, passing the scan result:
   - `forerunner doc readme`
   - `forerunner doc api-docs`
   - `forerunner doc stack-docs`
   - `forerunner doc diagrams`
   - `forerunner doc flows`
   - `forerunner doc version-audit`
   - `forerunner doc audit`
   - Skip any task whose check status is `CURRENT`

`changelog` and `review` are on-demand tasks — exclude from automated refresh.

## Output

Write each artifact to its task-defined output path. Append `## Gaps` wherever evidence is insufficient. Report a summary of what was updated.
