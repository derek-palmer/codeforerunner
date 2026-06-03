# Task: Surface Documentation and Scan Gaps

Reads cached forerunner state and surfaces two categories of gaps for the user to act on:
1. **Doc gaps** — STALE or MISSING findings from the check report
2. **Scan gaps** — fields the scan could not determine from available evidence

Does not generate docs. Routes the user to the right next step.

## Input

- `.forerunner/scan.yaml` — cached scan result (check file modification time)
- `.forerunner/check-report.md` — cached staleness classifications (check file modification time)

## Instructions

### Step 1 — Check cache freshness

Read `.forerunner/scan.yaml` and `.forerunner/check-report.md`.

If either file is missing: report which file is absent and stop. Ask the user to run `forerunner doc scan` and/or `forerunner doc check` first.

If `scan.yaml` is older than 24 hours: warn the user and offer to continue with cached results or re-run scan first.

If `check-report.md` is older than `scan.yaml`: warn the user and offer to continue or re-run check first.

### Step 2 — Surface doc gaps

Extract all rows from `check-report.md` where status is `STALE` or `MISSING`.

If none: report "All documented tasks are CURRENT." Proceed to step 3.

Present a summary table and offer: run `/forerunner-refresh` to regenerate all stale/missing docs, or invoke a specific task skill for individual items.

### Step 3 — Surface scan gaps

Read the `gaps:` field from `scan.yaml`. If absent or empty: report "No scan gaps detected." Stop.

Otherwise, list each gap and ask the user how to fill them:

**A) Quick fill** — ask one question per gap and patch `scan.yaml` with user-provided values  
**B) Full grill session** — deeper conversation that also updates `CONTEXT.md` and domain docs (requires `grill-with-docs` skill; fall back to A if not available)  
**C) Skip**

For quick fill (A): ask one question per gap in sequence, update the corresponding field in `.forerunner/scan.yaml`, mark as `# user-provided` inline.

For grill session (B): invoke `grill-with-docs` with the gap list as the grilling focus.

## Rules

- Never run a fresh scan or check automatically. Only read cached files.
- If `grill-with-docs` is not available when user selects B, fall back to A and inform the user.
- End with a summary: what was surfaced, what was filled, what remains open.
