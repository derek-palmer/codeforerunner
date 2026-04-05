# Agent Workflow Guidelines

Use these rules when implementing codeforerunner from the task checklist. Spec-driven AI workflows work best when requirements, plan, and tasks stay aligned and each task remains independently testable.

## Core rules

- Work from `docs/tasks.md` only.
- Complete one unchecked task at a time.
- Mark a task as `[x]` only after code, tests, and any required docs for that task are complete.
- Do not merge or skip phases unless a human explicitly changes the plan.
- If a task needs to be split, add the new tasks under the same phase before implementation begins.
- Complete **T0.9** (model adapter interface, P0.4) before any Phase 2 generation task so AI-assisted code paths never start against a concrete provider.

## Traceability rules

- Every implementation task must map back to a plan item in `docs/plan.md` and a requirement in `docs/requirements.md`.
- If behavior changes beyond current requirements, update `docs/requirements.md` first, then `docs/plan.md`, then `docs/tasks.md`.
- Do not add large new features without linking them to an explicit requirement.

## Task execution rules

- Prefer the smallest shippable change that satisfies the task.
- Add or update tests in the same change as the implementation.
- Keep implementation deterministic where possible and isolate AI-dependent logic behind adapters.
- Avoid broad refactors unless they are required by the active task.
- Leave unsupported stacks or uncertain behavior explicit in logs or generated docs rather than faking confidence.

## Validation rules

- Run only the relevant tests for the current task first, then broader tests as needed.
- Validate command behavior manually for CLI-related tasks.
- Validate generated Markdown or Mermaid outputs when a task changes generators.
- Do not mark a task complete if acceptance criteria are only partially met.

## Documentation rules

- Keep README updates small and tied to shipped capabilities.
- Keep the master spec stable; use the requirements, plan, and tasks docs for incremental execution.
- When a task introduces a new limitation, document it near the affected generator, analyzer, or adapter.
