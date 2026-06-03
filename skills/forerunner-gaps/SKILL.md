---
name: forerunner-gaps
description: Surface missing or stale forerunner documentation findings and scan gaps. Use when the user wants to know what docs are outdated, what tasks have never been run, or what the scan couldn't determine.
---

# forerunner-gaps

Reads cached forerunner state and surfaces two categories of gaps:
1. **Doc gaps** — STALE or MISSING findings from the check report
2. **Scan gaps** — fields the scan couldn't determine from available evidence

Does not generate docs itself. Routes the user to the right next step.

## Activate when

User asks to: find gaps, check forerunner gaps, what's missing, surface stale findings, what docs are outdated, gaps report, what hasn't been run.

## Collect this context

- `.forerunner/scan.yaml` — scan result (check file modification time)
- `.forerunner/check-report.md` — staleness classifications (check file modification time)

## Execute

### Step 1 — Check cache freshness

Read `.forerunner/scan.yaml` and `.forerunner/check-report.md`.

**If either file is missing:** Tell the user which file is absent. Ask them to run `/forerunner-scan` and/or `/forerunner-check` first. Stop.

**If scan.yaml is older than 24 hours:** Warn the user: "scan.yaml is X hours old — findings may not reflect current codebase. Run `/forerunner-scan` to refresh, or continue with cached results?" Wait for their choice before proceeding.

**If check-report.md is older than scan.yaml:** Warn the user: "check-report.md predates the last scan — it may not reflect the current scan result. Run `/forerunner-check` to refresh, or continue?" Wait for their choice.

### Step 2 — Surface doc gaps

Extract all rows from check-report.md where status is `STALE` or `MISSING`.

If none: report "All documented tasks are CURRENT." Skip to Step 3.

Otherwise, present a summary table:

```
## Doc Gaps

| Document              | Status  | Issue                                   |
|-----------------------|---------|-----------------------------------------|
| README.md             | STALE   | DATABASE_URL missing from config section |
| docs/api.md           | MISSING | No API docs found                        |
```

Then offer: "Run `/forerunner-refresh` to regenerate all stale/missing docs, or invoke a specific task skill (e.g. `/forerunner-readme`) for individual items."

### Step 3 — Surface scan gaps

Read the `gaps:` field from scan.yaml. If absent or empty, report "No scan gaps detected." Stop.

Otherwise, list each gap and ask the user:

> "The scan couldn't determine the following from available evidence:
> - [gap 1]
> - [gap 2]
>
> How would you like to fill these?
> A) Quick fill — I'll ask one question per gap and patch scan.yaml
> B) Full grill session — deeper conversation that also updates CONTEXT.md and domain docs (requires grill-with-docs skill)
> C) Skip"

**If user selects B and `grill-with-docs` skill is not available** (check by looking for the skill in the skills directory or `skills-lock.json`): inform the user that `grill-with-docs` is not installed. Fall back to option A automatically, or suggest they install the skill first.

**If user selects A:** Ask one question per gap in sequence. After each answer, update the corresponding field in `.forerunner/scan.yaml` and mark it as user-provided (add `# user-provided` comment inline). Continue until all gaps are filled or user skips a gap.

**If user selects B:** Invoke the `grill-with-docs` skill, passing the gap list as the grilling focus.

## Output

No files written by default. Side effects:
- If quick-fill (A): patches `.forerunner/scan.yaml` with user-provided values
- If grill session (B): `grill-with-docs` owns its own output (CONTEXT.md, ADRs)

Always end with a summary of what was surfaced, what was filled, and what remains open.
