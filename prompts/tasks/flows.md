# Task: Generate Flow Documentation

Generates narrative documentation for key system flows and integration paths.
Complements diagrams with prose explanation of how data and control move through the system.
Requires scan result as input.

## Input
- Scan result
- Key module files relevant to each flow
- Integration config files

## Flow Identification by Repo Type

**API / App:**
- Request lifecycle (ingress -> middleware -> handler -> service -> db -> response)
- Authentication flow
- Error handling flow

**ETL Pipeline:**
- Ingestion flow (source -> extraction -> staging)
- Transformation flow (staging -> rules -> validated output)
- Load flow (output -> destination write -> confirmation)
- Error/retry flow

**Infra / IaC:**
- Provisioning flow (how terraform apply sequences resource creation)
- Dependency flow (which resources block others)

**CLI:**
- Command dispatch flow
- Output flow

## Per-Flow Format

### [Flow Name]

**Trigger:** What initiates this flow
**Outcome:** Successful end state
**Error Path:** What happens on failure

#### Steps
1. **[Step name]** -- What happens, which module/file handles it
2. **[Step name]** -- What happens, which module/file handles it

#### Notes
Non-obvious behavior, edge cases, or important constraints.

## Rules
- Every step must reference the actual module or file that handles it
- Only describe what the code demonstrably does
- Explicitly call out process/service boundary crossings
- Claims must derive from provided files. If evidence is absent, omit or document in `## Gaps`.

## Output
<!-- output: docs/flows.md -->
