# Prompt Session unifies the scan-first rule, not the scan-state signals

The scan-first gate was duplicated across the CLI and MCP adapters, and the two had drifted: the CLI gate is config-gated and honors a `FORERUNNER_SCAN_DONE` escape hatch, while MCP gates unconditionally with no escape; the CLI validates task existence against the Task Registry while MCP validated only that a prompt file existed on disk. We introduced a run-scoped Prompt Session that owns the single scan-first *rule* (exempt task → allow; scan satisfied → allow; else deny) and task lookup (via the Task Registry for both adapters), but it does **not** unify the scan-state *signals*: each adapter still computes its own `scan_satisfied` boolean (CLI from `.forerunner/scan.md` ∨ env ∨ absent-config; MCP from `.forerunner/scan.md`, plus an in-process flag set when the `scan` tool runs) and injects it.

We chose this deliberately because the issue (#49) scoped out changing the scan-first invariant and required preserving `FORERUNNER_SCAN_DONE` for the CLI; fully unifying the signals would change MCP's observable behavior (it would gain config-gating and an env escape) and is deferred to a separate migration. So a future reader who sees CLI and MCP still differing on env/config signals — despite the glossary saying adapters share one policy — should know the divergence in *signal sourcing* is intentional; only the *rule and deny path* were unified here.

## Status

accepted
