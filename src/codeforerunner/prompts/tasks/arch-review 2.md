# Task: Architecture Review

Inspired by Matt Pocock's `/improve-codebase-architecture` skill:
https://github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture

Ranks repo-grounded Deepening Opportunities: architecture improvements that hide more behavior behind smaller interfaces, increasing leverage for callers and locality for maintainers.
Requires scan result as input.

## Input

- Scan result from `prompts/tasks/scan.md`
- File tree
- Key module/package files relevant to the scan result
- Existing tests for the modules under review
- `CONTEXT.md` or `CONTEXT-MAP.md` if present
- Relevant `docs/adr/*.md` files if present
- Existing architecture docs only when they clarify current design

## Review Focus

Look for architecture friction, not documentation drift:

1. Modules that are shallow: interface complexity nearly matches implementation complexity
2. Concepts that require bouncing across many files to understand
3. Seams that leak implementation details into callers
4. Pure helpers extracted for testability while real behavior remains hard to test
5. Adapter seams with more abstraction than real variation
6. Missing or weak tests caused by poor locality

Apply the deletion test to suspected shallow modules: if deleting the module makes complexity disappear, it was probably a pass-through; if complexity reappears across many callers, it was earning its keep.

## Vocabulary

Use these architecture terms consistently:

- Module
- Interface
- Implementation
- Deep
- Shallow
- Seam
- Adapter
- Leverage
- Locality
- Deepening Opportunity
- Deletion test

Use repo vocabulary from `CONTEXT.md` when present. If the repo lacks `CONTEXT.md` or the vocabulary is incomplete, infer temporary terms from evidence and list them under `## Suggested Glossary Additions`; do not write or rewrite `CONTEXT.md`.

## Candidate Format

For each Deepening Opportunity, include:

- **Files/modules**: concrete files or modules involved
- **Problem**: architecture friction observed
- **Evidence**: repo evidence supporting the finding
- **Proposed direction**: plain-English direction only
- **Benefits**: locality and leverage improvements
- **Testing impact**: what becomes easier to verify, without final test code
- **Risk / blast radius**: likely scope and migration risk
- **Recommendation strength**: `Strong`, `Worth exploring`, or `Speculative`

## Rules

- Claims must derive from provided files. If evidence is absent, omit or document in `## Gaps`.
- Do not report stale README/API/diagram/doc drift; use `check`, `review`, `diagrams`, or `flows` for that.
- Do not propose final function signatures, dataclass fields, schema shapes, or file-by-file implementation plans.
- Do not mutate `CONTEXT.md` or create ADRs.
- Do not imply Matt Pocock endorses codeforerunner.
- Keep the highest-signal 3-7 candidates. Fewer is acceptable when evidence is thin.

## Output Format

<!-- output: .forerunner/arch-review.md -->

# Architecture Review

> Inspired by Matt Pocock's `/improve-codebase-architecture` skill:
> https://github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture

## Summary

One paragraph describing the main architecture pressure observed.

## Top Recommendation

Name the highest-value Deepening Opportunity and why it should be first.

## Deepening Opportunities

### 1. [Candidate Name]

**Recommendation strength:** Strong | Worth exploring | Speculative

**Files/modules:** ...

**Problem:** ...

**Evidence:** ...

**Proposed direction:** ...

**Benefits:** ...

**Testing impact:** ...

**Risk / blast radius:** ...

## Suggested Glossary Additions

Only include if `CONTEXT.md` is missing or incomplete. Suggest terms; do not write them.

## Not Yet Decided

- Final interface shapes
- Migration sequence
- Exact tests

## Gaps

List missing evidence that could materially change the review.
