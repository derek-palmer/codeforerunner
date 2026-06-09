---
name: forerunner-refresh
description: Scan repo, check all docs for staleness, then ask which stale or missing docs to regenerate before updating them. Use when the user wants to update all docs, refresh docs, or sync documentation with the current codebase. Pass "auto" to skip the approval step and update everything stale.
---

# forerunner-refresh

Runs a full documentation refresh cycle: scan → check → Refresh Gate → generate/update the approved stale or missing docs.

## Activate when

User asks to: update all docs, refresh documentation, sync docs with code, run a doc sweep, or "update everything."

## Execute

Run each step in order, processing the result before moving to the next:

1. **Scan** — `forerunner doc scan` → capture YAML output as the scan result
2. **Check** — `forerunner doc check` → classify every doc as `CURRENT`, `STALE`, `MISSING`, or `UNVERIFIABLE`
3. **Refresh Gate** — present the check report (what is stale, what is current, what is missing, what is unverifiable), then ask the user **once**, as a multi-select with all options pre-selected, which of the `STALE` and `MISSING` docs to regenerate.
   - `UNVERIFIABLE` docs appear in the report but are never offered for regeneration — note them as gaps.
   - Skip the gate entirely when the user passed `auto` as an argument, or when the harness has no way to ask (headless/AFK run): proceed with the full stale set and say so in the summary.
4. **For each approved doc** — run the corresponding task in this order, passing the scan result:
   - `forerunner doc readme`
   - `forerunner doc api-docs`
   - `forerunner doc stack-docs`
   - `forerunner doc diagrams`
   - `forerunner doc flows`
   - `forerunner doc version-audit`
   - `forerunner doc audit`
   - Run order follows this sequence regardless of selection order. Skip any task whose check status is `CURRENT` or that the user declined at the gate.

`changelog` and `review` are on-demand tasks — exclude from automated refresh and never offer them at the gate.

## Output

Write each artifact to its task-defined output path. Append `## Gaps` wherever evidence is insufficient. Report a summary of what was updated, what was skipped as `CURRENT`, what was declined at the Refresh Gate, and any gaps found.
