# codeforerunner Spec

## G Goal

G1: `codeforerunner` → model-agnostic doc guardian; analyze repo, maintain docs/diagrams/architecture knowledge as code evolves.

## C Constraints

C1: prompts = core product; wrappers thin.
C2: no analyzer-heavy v1 rebuild unless explicit.
C3: no claims for working CLI, MCP, hooks, CI, Docker, PyPI until files exist.
C4: model/provider agnostic; provider-specific config optional.
C5: docs must distinguish current state vs roadmap.
C6: future legacy-style files (`src/`, `tests/`, `Dockerfile`, `Makefile`, `pyproject.toml`, `uv.lock`) must support prompt-first strategy directly.
C7: skill/plugin packages ! route to prompt pack/current files until runtime wrappers exist.

## I Interfaces

I.prompts: `prompts/system/base.md` + `prompts/partials/*.md` + `prompts/tasks/*.md` → reusable prompt pack.
I.init-onboarding: `prompts/tasks/init-agent-onboarding.md` → onboarding task for creating/updating `AGENTS.md` from repo evidence.
I.config: `forerunner.config.yaml.example` → example config only; no loader yet.
I.agent-configs: `agent-configs/*.md` → copyable editor-agent instructions.
I.docs: `docs/*.md` → human setup, prompt guide, editor setup, roadmap.
I.spec: `SPEC.md` → canonical phase/task tracker.
I.agent-skill: `agent/codeforerunner.skill.md` → canonical skill instruction source; its post-frontmatter Markdown content is consumed verbatim by Codex/Claude packages and `forerunner install` (per-agent frontmatter may differ; body cannot). See V10.
I.skill-plugin: skill/plugin packages = Codex (`plugins/codeforerunner/`) + Claude (`.claude-plugin/`, `skills/codeforerunner/`); install via `forerunner install <agent>` (I.installer).
I.validation: `scripts/validate_skill_copies.py` → local SPEC V10 body parity check for canonical and distributed skill files.
I.cli: `forerunner` CLI → `src/codeforerunner/cli.py`; subcommands `init`/`scan`/`doc`/`check`/`mcp-server`/`install`/`doctor`. `init`/`scan`/`doc` → resolve prompt bundle to stdout. `check` → run drift rules (I.hooks gate). `mcp-server` → stdio JSON-RPC (I.mcp). `install` → idempotent skill/marketplace writer (I.installer). `doctor` → health report (skill parity + marketplace + install destinations + config). `--version` flag prints package version.
I.installer: `forerunner install <agent>` → `src/codeforerunner/installer.py`; idempotent body-parity write into Codex/Claude/generic targets; managed-region markers; `--check` dry-run.
I.hooks: `.pre-commit-hooks.yaml` + `.github/workflows/forerunner-check.yml` → run `forerunner check`; skip when no `forerunner.config.yaml`.
I.mcp: stdio MCP server → `src/codeforerunner/mcp_server.py`; exposes one tool per `prompts/tasks/*.md` over JSON-RPC 2.0; `tools/call` returns `cmd_doc`-shaped bundle.

## V Invariants

V1: README current-state claims ! match tracked files.
V2: doc-gen/check workflows ! run `prompts/tasks/scan.md` first; `init-agent-onboarding` exempt (derives from repo evidence directly).
V3: roadmap surfaces ! labeled future until executable/scaffold files exist.
V4: no doc says install/run `forerunner` until CLI runnable end-to-end (stubs ≠ runnable; ! `--help` exits 0 AND ≥1 cmd executes prompt path).
V5: no doc says Docker/Makefile/PyPI/CI/pre-commit exists until corresponding files exist.
V6: spec ! updated when phases/tasks shift.
V7: agent configs ! reference prompt files, not imaginary package install.
V8: skill/plugin design ! avoid manual prompt discovery but must not claim installed package support before files exist.
V9: init onboarding docs must not claim runnable `forerunner init` until wrapper files exist.
V10: `agent/codeforerunner.skill.md` = canonical skill source; downstream Codex/Claude/generic skill files ! preserve its post-frontmatter Markdown content verbatim (per-agent YAML frontmatter may differ, but body content cannot diverge).
V11: future-surface designs (§D.*) ! remain design-only until corresponding wrapper/script/manifest files exist; no doc may claim runnable behavior before then (extends V4, V5, V9).
V12: installer ! idempotent: re-run = no diff when sources unchanged; ∀ writes overlay-safe (preserve user edits ∉ managed regions).

## P Phases

id|status|phase|exit
P0|x|repo truth cleanup|README/spec/AGENTS align with v2 state
P1|x|prompt pack hardening|task prompts consistent, composable, evidence-first
P2|x|agent config exports|editor-agent configs usable from tracked prompts
P3|x|human docs|setup, prompt guide, editor setup, roadmap present
P4|x|skill/plugin distribution design|simple agent setup planned without runtime claims
P5|x|thin wrappers|CLI, hooks, MCP server all runnable; future polish tracked as follow-up §T rows
P6|x|polish|config schema + scan-first MCP gating + init flags + marketplace publishing CI
P7|x|surface parity|docs + AGENTS refresh, CLI scan-first parity, expanded check rules
P8|x|doc backfill|sweep remaining stale "future"/"planned" docs against current SPEC phases
P9|x|tool ergonomics|`--version`, `forerunner doctor`, workflow lint, initial CHANGELOG
P10|x|model runtime|provider abstraction + `forerunner generate` + config + doctor wiring
P11|x|release|PyPI publish workflow + install docs
P12|x|MCP example|usable Claude Desktop / mcp-cli example wiring

## T Tasks

id|status|phase|task|cites
T1|x|P0|replace stale `README.md` with prompt-first current state|V1,V3,V4,V5
T2|x|P0|move phase/task tracker to `SPEC.md`|V6,I.spec
T3|x|P2|add `agent-configs/` scaffolds|V7,I.agent-configs
T4|x|P3|add `docs/getting-started.md`|I.docs,V1
T5|x|P3|add `docs/prompt-guide.md`|I.prompts,V2
T6|x|P3|add `docs/editor-agent-setup.md`|I.agent-configs,V7
T7|x|P3|add `docs/roadmap.md`|V3,I.cli,I.mcp,I.hooks
T8|x|P1|add evidence rules and gaps convention to all task prompts|I.prompts,V2
T16|x|P1|add prompt-first init onboarding task for AGENTS generation/update|I.init-onboarding,V9
T9|x|P5|design CLI surface (§D.cli); implementation deferred|I.cli,C1,V11
T10|x|P5|design hooks/CI surface (§D.hooks); implementation deferred|I.hooks,C1,V11
T11|x|P4|write skill/plugin distribution design|I.skill-plugin,I.agent-skill,V8,V10
T12|x|P4|add canonical skill source from prompt pack|I.prompts,I.agent-skill,I.skill-plugin,C7,V10
T13|x|P4|add Codex plugin package for prompt workflow|I.skill-plugin,I.agent-skill,V8,V10
T14|x|P4|add Claude skill/plugin package for prompt workflow|I.skill-plugin,I.agent-skill,I.validation,V8,V10
T15|x|P4|design installer + Codex marketplace + Claude install (§D.installer); implementation deferred|I.skill-plugin,I.agent-skill,I.installer,V8,V10,V11,V12
T17|x|P5|implement minimal `forerunner` CLI under `src/` (D.cli: init, scan, doc, check stubs routing to prompt pack)|I.cli,D.cli,C1,V4,V11
T18|x|P4|implement idempotent installer `forerunner install <agent>` (D.installer: body-parity check, managed-region markers, --check dry-run)|I.installer,D.installer,V8,V10,V11,V12
T19|x|P5|wire pre-commit + CI hooks calling `forerunner check` (D.hooks: skip when no forerunner.config.yaml)|I.hooks,D.hooks,V11
T20|x|P5|wire `forerunner init` subcommand to `prompts/tasks/init-agent-onboarding.md` bundle (replace stub exit 2)|I.cli,I.init-onboarding,D.cli,V2,V9
T21|x|P5|wire `forerunner scan` subcommand to `prompts/tasks/scan.md` bundle (replace stub exit 2)|I.cli,I.prompts,D.cli,V2
T22|x|P5|implement real `forerunner check` rules: detect V1/V3/V5 drift (docs claim absent files, files claim absent docs); exit ≠0 on violation|I.cli,I.hooks,D.cli,D.hooks,V1,V3,V5
T23|x|P5|design + implement minimal MCP server exposing prompt bundles (promote I.future-mcp → I.mcp); add §D.mcp design row|I.mcp,D.mcp,C1,V11
T24|x|P4|publish Codex marketplace manifest at `plugins/codex/marketplace.json` (D.installer follow-up); installer learns `--marketplace` flag|I.installer,D.installer,V11
T25|x|P6|define `forerunner.config.yaml` schema + loader; `check` consumes config to drive rule list & ignore paths|I.cli,I.hooks,C4,V2
T26|x|P6|MCP server enforces scan-first per V2 (`tools/call` for non-exempt tasks → error without prior `scan` call in session)|I.mcp,V2
T27|x|P6|implement `forerunner init --full` and `--agents-only` flags per Init-Onboarding wrapper block|I.cli,I.init-onboarding,V9
T28|x|P6|automate Codex marketplace publishing on git tag (CI workflow validates + uploads `plugins/codex/marketplace.json`)|I.installer,I.hooks,V11
T29|x|P7|refresh README + docs/getting-started.md to document mcp-server, init --full/--agents-only, forerunner.config.yaml schema|V1,I.cli,I.mcp,I.hooks
T30|x|P7|refresh AGENTS.md against current repo state (CLI + installer + hooks + MCP + config)|I.init-onboarding,V9
T31|x|P7|`forerunner doc <task>` emits stderr warning when task ∉ scan-exempt and config present without prior scan (CLI parity w/ MCP V2 gate)|I.cli,V2
T32|x|P7|expand check rules (R6 Docker/Makefile claims, R7 MCP claims, R8 marketplace claims) + validate workflow lints via actionlint|I.cli,I.hooks,I.installer,V1,V5
T33|x|P8|refresh docs/roadmap.md + docs/agent-distribution-design.md + README "future installer" reference against current §P statuses|V1,V3,I.docs
T34|x|P9|add `forerunner --version` flag (sources `codeforerunner.__version__`)|I.cli
T35|x|P9|add `forerunner doctor` subcommand: runs skill body-parity + marketplace validation + flags unmanaged install destinations|I.cli,I.installer,I.validation,V10,V12
T36|x|P9|add workflow-YAML parse test for `.github/workflows/*.yml` (catches typos without needing actionlint)|I.hooks
T37|x|P9|seed `CHANGELOG.md` documenting v0.2.0 → release-ready surfaces|I.docs,V1
T38|x|P10|provider abstraction (`src/codeforerunner/providers/`) + `forerunner generate <task>` subcommand calling configured provider|I.cli,C4,V2
T39|x|P10|extend `forerunner.config.yaml` schema with per-provider `api_key_env` override; `forerunner doctor` reports missing key when provider configured|I.cli,I.installer,V12
T40|x|P11|add `.github/workflows/publish.yml` (publish on `v*.*.*` tag via OIDC); document `pipx`/`pip` install in README + CHANGELOG|I.hooks,I.docs,V5
T41|x|P12|add `examples/mcp/` with Claude Desktop config snippet + README showing how to wire `forerunner mcp-server`|I.mcp,I.docs

## Init-Onboarding

Goal: prompt-first, wrapper-agnostic repo onboarding → `AGENTS.md` + optional per-agent overlays.

State: prompt-driven; `forerunner init` (I.cli) resolves the bundle for `prompts/tasks/init-agent-onboarding.md` to stdout. Agent applies the bundle to produce/update AGENTS.md.

Concepts:
- Init pass: read-first analysis + focused instruction updates.
- AGENTS contract: repo-wide canonical onboarding rules for future agent sessions.
- Agent overlays: optional tool-specific instructions from same repo analysis.

Workflow (`I.init-onboarding`):
1. Repo analysis: detect lang/framework/tooling from manifests, lockfiles, workflows, infra. Classify topology (single vs monorepo); identify key boundaries & entrypoints.
2. Update `AGENTS.md`: create if absent; update in place; preserve custom constraints; keep high-signal only.
3. Optional overlays: per-agent files on request; same facts as `AGENTS.md`; no contradictory command sets.
4. Stop: default scope = onboarding only. Doc-gen = separate flow (`I.prompts`).

`AGENTS.md` requirements (keep compact):
1. Repo reality & scope boundaries.
2. Highest-value commands (dev/test/lint/format/release checks when present).
3. Structural notes that change agent behavior.
4. Non-obvious constraints & anti-claims (planned ≠ implemented).
5. Verification expectations for doc/prompt-only changes.

Rules: executable truth > prose. No generic advice. No speculative claims. Names consistent: `codeforerunner`, `forerunner`, `forerunner.config.yaml`.

Non-destructive updates: preserve user-authored constraints unless contradicted by verifiable repo state. Replace stale commands. Keep deltas minimal & reviewable.

Wrapper:
```text
forerunner init                     # resolves bundle to stdout; agent applies
forerunner init --full              ? future flag (no impl yet)
forerunner init --agents-only       ? future flag (no impl yet)
```
Wrapper = orchestration only; product logic stays in prompt contracts & repo docs.

Acceptance:
- Output reflects current repo state; no overclaims.
- `AGENTS.md` compact, specific, materially useful.
- Prompt-first remains source of truth.

## D Future-Surface Designs

Design-only; cites V11. No file claims runnable until wrapper exists.

### D.cli — `forerunner` CLI

cmd: `forerunner init [--full|--agents-only]` → onboarding orchestration; delegates to `I.init-onboarding`.
cmd: `forerunner scan` → runs `prompts/tasks/scan.md` pipeline; emits repo-evidence JSON.
cmd: `forerunner doc <task>` → resolves `prompts/tasks/<task>.md` + base + partials → prompt bundle on stdout.
cmd: `forerunner check` → runs check/review prompts against tracked docs; exit ≠ 0 on drift.
cmd: `forerunner doctor` → aggregate health checks (V10 parity, V12 markers, config loadable, marketplace valid); exit 1 iff any "error" finding.

Shape:
- Thin orchestration only; product logic stays in `prompts/`.
- Model/provider agnostic (C4); provider plugin ? optional.
- No network calls in `init`/`scan`/`doc`; `check` may call configured model.

Gate: prompt contract stable (P1 `x`) + ≥1 wrapper file under `src/`.

### D.hooks — pre-commit/CI

hook: pre-commit → `forerunner check --staged` → block on V1/V3/V4/V5 violations.
hook: CI → same; matrix over tracked agent configs.
env: `FORERUNNER_MODEL` ? optional override.

Shape:
- Reuses `D.cli check` (single code path).
- Skip when no `forerunner.config.yaml` present.

Gate: `D.cli check` exists & stable.

### D.installer — distribution

cmd: `forerunner install <agent>` → idempotent copy of owned skill/plugin artifacts into agent-specific dirs.
- Supported targets: Codex (`~/.codex/...`), Claude (`~/.claude/plugins/...`), generic (manual path).
- Body-parity check (V10) before write; abort on mismatch.
- Managed-region markers in destination files; user edits outside markers preserved (V12).

api: Codex marketplace manifest → `plugins/codex/marketplace.json` (future path).
api: Claude plugin index → existing `plugins/claude/` artifacts; install = symlink|copy.

Shape:
- Re-run safe (V12): hash sources; skip when dest matches.
- Dry-run flag `--check` → print plan, write nothing.

Gate: T11-T14 done (`x`) + canonical skill source frozen.

### D.mcp — MCP server

cmd: `forerunner mcp-server` → stdio MCP server; exposes prompt bundles as tools.
api: `tools/list` → one tool per `prompts/tasks/*.md` (name = task basename; description = first H1 / first non-empty line).
api: `tools/call <task>` → resolved bundle (base + partials + task body) as text content.

Shape:
- Stdio transport only (initial).
- Read-only; no filesystem writes.
- Reuses `cmd_doc` resolution path (single code path with `D.cli`).

Gate: T17 stable + ≥1 MCP client tested end-to-end.

## B Bugs

id|date|cause|fix
