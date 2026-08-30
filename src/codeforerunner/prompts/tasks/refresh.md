# Task: Refresh All Documentation

Runs a full documentation refresh cycle: scan, check staleness, then generate or update every stale or missing doc in one pass.

This prompt is the batch form (all bundles concatenated). When running via the `/forerunner-refresh` skill, the agent calls `forerunner doc <task>` for each step individually so it can process each result before moving to the next, and applies the Refresh Gate — asking the user which stale or missing docs to regenerate — between check and generate. The batch form has no gate.

## Steps (execute in order)

1. **Scan** — Execute the scan task bundle. Capture the YAML output. All downstream tasks depend on it.
2. **Check** — Execute the check task bundle using the scan result. Identify every doc with `STALE` or `MISSING` status.
3. **Generate / update** — For each stale or missing doc, run the corresponding task bundle in this order:
   `api-docs` → `stack-docs` → `diagrams` → `flows` → `version-audit` → `audit` → `readme`
   Skip any task whose check status is `CURRENT`, **except `readme`**: run `readme` if its own
   check status is `STALE`/`MISSING` *or* any other task in this step ran, so the Docs Index
   reflects docs generated earlier in the same pass. Skip `readme` only when it was `CURRENT`
   and no other task ran.
   Note: `changelog` and `review` are on-demand tasks excluded from automated refresh.

## Rules

- The scan result from step 1 is the input to all downstream tasks.
- The check report from step 2 determines which tasks run, except `readme` per step 3's rule.
- Stop and report if scan fails (non-zero exit or empty output).
- Write each artifact to its task-defined output path.
- Append a `## Gaps` section to any doc where evidence is insufficient — never silently omit content.
- Report a summary of what was updated, skipped, and any gaps found.
