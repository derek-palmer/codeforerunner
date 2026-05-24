# Changelog

All notable changes to `codeforerunner` are documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[Unreleased]: https://github.com/derek-palmer/codeforerunner/compare/v0.3.2...HEAD
[0.3.2]: https://github.com/derek-palmer/codeforerunner/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/derek-palmer/codeforerunner/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/derek-palmer/codeforerunner/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/derek-palmer/codeforerunner/releases/tag/v0.2.0
