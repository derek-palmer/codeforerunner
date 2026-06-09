# Changelog

All notable changes to `codeforerunner` are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.10] — 2026-06-09

### Added

- **Docs Index** — glossary term in `CONTEXT.md` defining the `## Documentation` README section that links every user-facing doc in `docs/` with one-line descriptions. The readme task is its sole writer; the check task flags README STALE on unlinked docs or dead index links; `.forerunner/` artifacts are never indexed. Groundwork for the README docs-index feature (#105). (#106, `CONTEXT.md`)

## [0.4.9] — 2026-06-09

### Added

- **Refresh Gate** — the `/forerunner-refresh` skill form now presents the staleness check report and asks once (multi-select, all options pre-selected) which `STALE`/`MISSING` docs to regenerate, instead of rewriting everything unprompted. `UNVERIFIABLE` docs are reported but never offered. Pass `auto` (or run in a harness that can't ask) to skip the gate and update the full stale set. The batch prompt form stays non-interactive for CI/AFK use. Summary output gains a "declined" category. Glossary term added to `CONTEXT.md`. (#102, `skills/forerunner-refresh/SKILL.md`, `src/codeforerunner/prompts/tasks/refresh.md`)

## [0.4.8] — 2026-06-02

### Added

- **`forerunner-gaps` skill** — surfaces STALE/MISSING documentation findings from `.forerunner/check-report.md` and unresolved `gaps:` fields from `.forerunner/scan.yaml`. For doc gaps, routes to `/forerunner-refresh` or specific task skills. For scan gaps, offers quick Q&A fill (patches `scan.yaml` inline) or a full `grill-with-docs` session; falls back to Q&A if `grill-with-docs` is not installed. Registered in the Task Registry (`scan_exempt: true`) and installable via the skill installer. (`skills/forerunner-gaps/SKILL.md`, `src/codeforerunner/prompts/tasks/gaps.md`, `src/codeforerunner/tasks.json`)

## [0.4.7] — 2026-06-02

### Fixed

- **Agent detection silent failures** — `shellEscape` was missing its closing single quote, causing all `command:`-based detections (`claude`, `gemini`, `opencode`, `codex`, etc.) to produce a shell syntax error and return `not found`. Only agents with a `macapp:` fallback (e.g. Cursor) were detected. (`bin/install.js`)
- **Global install installing locally** — `installViaSkills` never passed `-g` to `npx skills add`, so the global/local choice had no effect for non-Claude/Gemini agents; both modes installed to the current directory. (`bin/install.js`)
- **Agent profile filter overridden by `--all`** — `npx skills add --all` expands to `--agent '*'`, silently overriding the per-provider `-a <profile>` argument. Replaced with explicit `--agent <profile> --skill '*'`. (`bin/install.js`)
- **Bundled skills ignored on `npx` installs** — `fetchSkill` fell back to HTTPS even though `skills/` ships in the npm package, because `detectRepoRoot` requires `plugins/` which is not in the published files. Now checks `__dirname/../skills/` before the network. (`bin/install.js`)

### Added

- **Interactive agent selection** — when multiple agents are detected and stdin/stdout are TTYs, the installer prompts users to choose which agents to install to (numbered list, space-separated input, default: all). Skipped when `--only`, `--non-interactive`, or only one agent is detected. (`bin/install.js`)
- 12 new installer tests: `shellEscape` correctness and shell round-trip, `buildSkillsAddArgs` unit tests for global `-g` flag and agent profile preservation, local install path targeting, `--only` validation, `--non-interactive` non-blocking. (`tests/install.test.js`)

## [0.4.6] — 2026-06-01

### Added

- npm package metadata: SPDX-style license declaration, `author` field, and a `SECURITY.md` policy. (`package.json`, `SECURITY.md`)

### Changed

- Installer refactored so the **Install Plan** is the unit of work. (`bin/install.js`)
- Skill-parity refactored: the canonical↔copies body rule now lives in one module.
- Prompt-session bundle outcome now owned behind `resolve()`.
- Purged iCloud sync-conflict files and added a guard to block future ones.

## [0.4.5] — 2026-05-29

### Added

- **Task Registry** (`src/codeforerunner/tasks.json`) — single source of truth for task identity, scan-exemption policy, the refresh sequence, and installable skill slugs. (#66)
- Node installer (`bin/install.js`) now reads installable skill slugs from the Task Registry instead of a hardcoded list, backed by a Node↔Python parity test and a `node --test` suite wired into CI. (#70)
- Scan-first gate persists across restarts via `.forerunner/` session state and is enforced consistently across the CLI and MCP server. (#56, #68)
- `arch-review` task and skill surface.

### Fixed

- **npm publishing** — the publish workflow now upgrades the npm CLI before publishing. Node 22 bundles npm 10.x, which lacks OIDC trusted-publishing support and silently falls back to anonymous publish (registry returns `404`); OIDC trusted publishing requires npm ≥ 11.5.1. (`.github/workflows/npm-publish.yml`)
- Socket badge version stays in sync on release. (#67)
- Installer shim pins corrected, with future-drift detection.
- Docker login credentials in the publish workflow. (#41)
- `package.json` paths and README install instructions. (#40)

### Changed

- Retired `SPEC.md`; GitHub Issues now own work tracking.
- `CONTEXT.md` and agent docs: added npm release and GitHub Issues glossary terms.
- CodeRabbit automatic review disabled.
- **npmjs publishing is now OIDC trusted publishing** (tokenless). The `NPM_TOKEN` secret referenced in the 0.4.1 notes is no longer used or required; auth comes from the `npm` environment's `id-token: write` permission. (#48)

## [0.4.4] — 2026-05-26

### Added

- Installer supports `--global` / `--local` flags and refresh mode for updating existing installations. (`bin/install.js`)
- GitHub Action published to marketplace — composite runner at `action.yml` for CI-based forerunner runs.
- Docker + Makefile sample for containerized usage.
- Dependabot configuration for automated dependency updates.
- Branch protection rules for `main` via Rulesets API with admin bypass.
- Published to GitHub Packages npm registry under `@derek-palmer/codeforerunner`.

### Fixed

- `tomllib` import compatibility fix for Python < 3.11; canonical Windows argument quoting.
- CodeQL scan findings: incomplete URL substring sanitization, workflow missing permissions, incomplete string escaping, clear-text logging of sensitive information.

### Changed

- Configuration and documentation clarity improvements.
- GitHub Actions pinned to latest versions.

## [0.4.3] — 2026-05-26

### Security

- **H1** — `forerunner doctor` no longer executes Python scripts from the target repo by default. Script-based checks (`skill-body-parity`, `codex-marketplace`) now emit `[warn] skipping script validation` unless `--run-scripts` is passed explicitly. (`doctor.py`, `cli.py`)
- **H2** — `install.sh` and `install.ps1` now pin the npm package to `codeforerunner@0.4.1` and the GitHub fallback to `github:derek-palmer/codeforerunner#v0.4.1`, preventing arbitrary code execution in `curl|bash` one-liner installs.
- **H3** — Added comment in `providers/google.py` documenting that the API key appears in the URL query string (Google REST API requirement; key may appear in proxy logs).
- **M2** — MCP server `tools/call` validates that the tool `name` contains no path separators or `..` components, and checks the resolved path is inside `prompts/tasks/` before executing. (`mcp_server.py`)
- **M7** — `OllamaProvider` and `is_available` now validate the base URL scheme (`http`/`https`) and reject `169.254.*` link-local addresses to prevent SSRF via `OLLAMA_HOST`. (`providers/ollama.py`)

### Fixed

- **M1** — `forerunner.config.yaml` and `_STARTER_CONFIG` in `doctor.py` had `enabled_rules` at the YAML root instead of under `tasks.check`. This was a functional bug causing the field to be silently ignored. Both the dogfood config and the `--fix` template are corrected.
- **M3** — `cmd_generate` no longer swaps `sys.stdout` globally (thread-unsafe). Bundle resolution now goes through `_get_bundle()` which returns a string directly. (`cli.py`)
- **M4** — All provider `urlopen` calls now pass `timeout=120` to prevent indefinite hangs. (`providers/anthropic.py`, `openai.py`, `google.py`, `ollama.py`)
- **M5** — `install_all_skills` now correctly sets `any_error = True` when a source file is missing or a write fails, so install failures propagate to the return code. (`installer.py`)
- **M6** — `int()` calls in `config.py` are now wrapped in `_to_int()` which raises `ConfigError` with a descriptive message instead of bare `ValueError`. (`config.py`)
- **L1** — Replaced `assert span is not None` in `overlay()` with `RuntimeError`. (`installer.py`)
- **L2** — Removed unused `output_dir`, `context_max_files`, `context_max_lines_per_file` fields from `ForerunnerConfig` and the YAML parser. (`config.py`)
- **L3** — `_load_script_module` now uses a UUID-suffixed module name to prevent stale cached modules on repeated calls. (`doctor.py`)
- **L4** — `_description_for` in MCP server now reads line-by-line instead of loading the entire file into memory. (`mcp_server.py`)
- **L5** — `format_report` uses direct dict access (`counts['ok']`) instead of redundant `.get()` calls. (`doctor.py`)
- **L6** — MCP server now enforces `initialize` as the first call; `tools/list` and `tools/call` before `initialize` return JSON-RPC error `-32002 Server not initialized`. (`mcp_server.py`)
- **L7** — `vscodeExtPresent` and `cursorExtPresent` in `bin/install.js` now use `includes()` instead of `new RegExp(needle)`, preventing extension ID metacharacters from being interpreted as regex. (`bin/install.js`)
- **L8** — Added unit test `test_generate_stream_flag_yields_chunks` covering the `--stream` branch of `cmd_generate`. (`tests/test_cli.py`)
- **L9** — `find_prompts_root` now stops walking after 10 parent directories to avoid traversing to the filesystem root. (`bundle.py`)

## [0.4.1] — 2026-05-24

### Added

- **npm publish** — `codeforerunner` package published to npmjs.com alongside the existing PyPI release. `npx codeforerunner` and `npx codeforerunner-install` both run the multi-agent installer.
- Root `package.json` with `bin`, `files`, `engines`, `keywords`, `repository` fields.
- `.github/workflows/npm-publish.yml` — publishes to npm with provenance (`--provenance --access public`) on every `v*.*.*` tag push, using `NPM_TOKEN` secret.
- `install.sh` and `install.ps1` now probe the npm registry first (`HEAD https://registry.npmjs.org/codeforerunner/latest`) and fall back to `npx github:derek-palmer/codeforerunner` if npm is unavailable.

### Notes

- Both `pyproject.toml` and `package.json` versions must be kept in sync on every release. Bump both files, commit as a single `chore: bump to vX.Y.Z` commit, then tag.
- npm provenance requires the `npm` GitHub Actions environment to be configured in the repo settings and an `NPM_TOKEN` secret with `Automation` scope to be added.

## [0.4.0] — 2026-05-24

### Added

- **Multi-agent skill packaging** — 12 per-task slash commands (`/forerunner-scan`, `/forerunner-readme`, `/forerunner-api-docs`, `/forerunner-audit`, `/forerunner-changelog`, `/forerunner-check`, `/forerunner-diagrams`, `/forerunner-flows`, `/forerunner-init`, `/forerunner-review`, `/forerunner-stack-docs`, `/forerunner-version-audit`) for Claude Code, Codex, Gemini CLI, and 30+ other agent CLIs.
- **`bin/install.js`** — unified cross-platform installer modelled on caveman's pattern: 33-agent matrix with detection probes (`command:`, `macapp:`, `vscode-ext:`, `cursor-ext:`, `jetbrains-plugin:`, `dir:`, `file:`), three install mechanisms (`claude plugin install`, `gemini extensions install`, `npx skills add`), and full flag surface (`--dry-run`, `--force`, `--only`, `--all`, `--minimal`, `--list`, `--no-color`, `--skip-skills`, `--uninstall`).
- **`install.sh` / `install.ps1`** rewritten as thin Node.js shims: exec `node bin/install.js` locally, fall back to `npx github:derek-palmer/codeforerunner` for curl|bash installs.
- **`skills-lock.json`** — SHA-256 content hashes for all 13 skill files.
- Agent autodiscovery files: `GEMINI.md` (Gemini CLI), `.codex/config.toml` (Codex), `.claude-plugin/marketplace.json` (Claude Code marketplace).
- **Ollama auto-fallback** — `forerunner generate` probes `localhost:11434` when no API key is configured; automatically switches to Ollama local mode if available. Explicit `--provider` or `provider:` in config always takes precedence. Improved error message includes Ollama hint when no fallback is found.
- `forerunner doctor` surfaces Ollama local-mode status: reports running/not-running when no `forerunner.config.yaml` is present.
- 218 new tests (187 → 405 total) covering Ollama fallback paths, doctor Ollama checks, and skill installer logic.

### Changed

- Default Anthropic model updated from `claude-opus-4-5` to `claude-opus-4-7` across CLI, MCP server, and provider defaults.

## [0.3.2] — 2026-05-24

### Added

- Inverse drift rules RI1, RI5, RI7: fire when docs positively reference a feature (CLI, pip package, MCP server) that is absent from the repo.
- Version-pin drift rule RV1: flags `codeforerunner==X.Y.Z` pins in docs that differ from the current `pyproject.toml` version; skips `CHANGELOG.md`.
- `forerunner doctor --fix`: writes a starter `forerunner.config.yaml` (enabling R1–R5, R7, R8) when no config exists, then runs the normal health report.
- `forerunner generate --stream`: streams output token-by-token for all four providers (Anthropic SSE, OpenAI SSE, Google `streamGenerateContent?alt=sse`, Ollama NDJSON).
- `action.yml` composite GitHub Action — `uses: derek-palmer/codeforerunner@vX.Y.Z` installs codeforerunner and runs `forerunner check`. No-op when `forerunner.config.yaml` is absent.

### Changed

- Test suite expanded from 145 to 174 tests: inverse rule and version-drift coverage, streaming provider coverage for all four backends, `doctor --fix` integration tests.

## [0.3.1] — 2026-05-24

### Added

- `forerunner.config.yaml` dogfood config at repo root; enables drift rules R1–R5, R7, R8.
- `audit` and `changelog` task prompts (`prompts/tasks/audit.md`, `prompts/tasks/changelog.md`).
- PyPI `classifiers` and `keywords` in `pyproject.toml` for discoverability.
- `src/codeforerunner/bundle.py` — shared `find_prompts_root()` + `resolve_bundle()` used by both `cli.py` and `mcp_server.py`; eliminates duplicated `_repo_root` logic.

### Fixed

- `forerunner mcp-server` now works after `pip install` without requiring `--repo`: prompts bundled inside the package (`src/codeforerunner/prompts/`) and included via `package-data`.
- `forerunner --version` and MCP `serverInfo.version` now read the installed package version dynamically instead of the hardcoded `"0.2.0"` string.
- MCP advertised protocol version updated from `2024-11-05` to `2025-03-26`.
- `forerunner mcp-server --repo /path` now works and appears in `--help` (previously only `forerunner --repo /path mcp-server` worked).
- `forerunner-check` CI no longer fails on every push: removed pre-checkout `hashFiles()` gate that always evaluated false (empty workspace before `actions/checkout`).

### Changed

- Test suite expanded from 117 to 145 tests: HTTP/network error paths for all four providers, check edge cases, CLI exit codes.

## [0.3.0] — 2026-05-24

### Added

- `forerunner --version` flag (T34).
- `forerunner doctor` subcommand — single-screen health report covering skill body parity, Codex marketplace validation, and installed-destination markers (T35).
- Workflow-YAML parse test (`tests/test_workflows_yaml.py`) — catches typos in `.github/workflows/*.yml` without requiring `actionlint` locally (T36).
- This changelog (T37).
- Provider abstraction and `forerunner generate <task>` command for configured model calls (T38).
- Per-provider `api_key_env` config override plus `forerunner doctor` key checks (T39).
- PyPI publish workflow (`.github/workflows/publish.yml`) using OIDC trusted publishing on `v*.*.*` tags (T40).
- `README.md` "Install" section documenting `pipx`/`pip` install after the first PyPI release (T40).

### Notes

- Direct model invocation is available through `forerunner generate`; `provider` / `model` config fields are active there.

## [0.2.0]

Initial release-ready surface around the prompt pack.

### Added

- Python package and `forerunner` console script.
- CLI subcommands: `init`, `scan`, `doc`, `check`, `mcp-server`, `install`.
- `forerunner init --full / --agents-only` flags (T27).
- `forerunner check` rules R1–R8 with `forerunner.config.yaml` schema, `enabled_rules` allowlist, and `ignore_paths` globs (T22, T25, T32).
- `forerunner.config.yaml` schema + loader (`src/codeforerunner/config.py`); `ConfigError` surfaces field paths (T25).
- `forerunner mcp-server` — stdio JSON-RPC MCP server exposing one tool per `prompts/tasks/*.md`; `tools/call` enforces SPEC V2 scan-first per session (T23, T26).
- `forerunner install <agent>` — idempotent body-parity skill installer with managed-region markers and `--check` dry-run (T18).
- `forerunner install <agent> --marketplace` — installs `plugins/codex/marketplace.json` into `~/.codex/marketplaces/codeforerunner.json` (T24).
- `forerunner doc <task>` stderr warning when `forerunner.config.yaml` is present and `FORERUNNER_SCAN_DONE` is unset (CLI parity with the MCP scan-first gate; T31).
- Pre-commit hook (`.pre-commit-hooks.yaml`) and GitHub Actions workflow (`.github/workflows/forerunner-check.yml`) wrapping `forerunner check`; both no-op without `forerunner.config.yaml` (T19).
- GitHub Actions workflow (`.github/workflows/codex-marketplace-publish.yml`) that validates the manifest, asserts tag/version parity, and uploads it on tagged release (T28).
- Canonical skill source (`agent/codeforerunner.skill.md`) with Codex (`plugins/codeforerunner/`) and Claude (`.claude-plugin/`, `skills/codeforerunner/`) distributions; body parity enforced by `scripts/validate_skill_copies.py` (T12–T14).
- Prompt pack hardening (evidence rules, gaps convention) across `prompts/tasks/*.md` (T8, T16).
- `agent-configs/` scaffolds for Claude, Cursor, Copilot, Cline, Windsurf (T3).
- `docs/getting-started.md`, `docs/prompt-guide.md`, `docs/editor-agent-setup.md`, `docs/roadmap.md`, `docs/agent-distribution-design.md`.

### Notes

- Only runtime dep: `PyYAML>=6.0`.
- `init` and `scan` are honest wrappers over the prompt pack; they emit bundled prompt text to stdout for the calling agent to act on.
- Model invocation is out of scope; `provider` / `model` config fields are honored only by future wrappers.

[Unreleased]: https://github.com/derek-palmer/codeforerunner/compare/v0.4.5...HEAD
[0.4.5]: https://github.com/derek-palmer/codeforerunner/compare/v0.4.4...v0.4.5
[0.4.4]: https://github.com/derek-palmer/codeforerunner/compare/v0.4.3...v0.4.4
[0.3.2]: https://github.com/derek-palmer/codeforerunner/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/derek-palmer/codeforerunner/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/derek-palmer/codeforerunner/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/derek-palmer/codeforerunner/releases/tag/v0.2.0
