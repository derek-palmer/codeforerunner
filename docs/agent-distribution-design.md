# Agent Skill and Plugin Distribution Design

## Goal

Make codeforerunner installable as an agent skill or plugin so users can ask Claude Code, Codex, or another coding agent to run the documentation workflow without manually locating prompts or copying files.

This is packaging and workflow glue around the tracked prompt pack. The agent package should not become a second implementation of codeforerunner.

## Upstream Pattern

The `caveman` repo uses three ideas worth mirroring:

- one-line install entrypoints for macOS/Linux and Windows,
- thin shell/PowerShell wrappers around a unified Node installer,
- per-agent package folders such as Codex plugin metadata, Claude plugin metadata, generic skills, and command files.

That shape keeps install UX simple while leaving agent-specific differences isolated.

## Package Layout

Codex slice (`plugins/codeforerunner/.codex-plugin/plugin.json` + `plugins/codeforerunner/skills/codeforerunner/SKILL.md`) is implemented (SPEC T13). Claude slice (`.claude-plugin/plugin.json` + `skills/codeforerunner/SKILL.md`) is implemented (SPEC T14). Generic installer-driven distribution is implemented via the Python `forerunner install` CLI (SPEC T18) and reuses the root `skills/codeforerunner/SKILL.md` file. The original Node-based wrapper layout (`bin/install-agent.js`, `install.sh`, `install.ps1`, `agent/templates/*`) is no longer the planned route; the Python CLI subsumes that surface.

```text
agent/
  codeforerunner.skill.md       # implemented (T12) — canonical skill source
src/
  codeforerunner/
    installer.py                # implemented (T18) — forerunner install <agent>
plugins/
  codeforerunner/
    .codex-plugin/
      plugin.json               # implemented (T13)
    skills/
      codeforerunner/
        SKILL.md                # implemented (T13)
  codex/
    marketplace.json            # implemented (T24)
.claude-plugin/                 # implemented (T14)
  plugin.json                   # implemented (T14)
skills/                         # implemented for Claude (T14), reused by generic distribution (T18)
  codeforerunner/               # implemented (T14)
    SKILL.md                    # implemented (T14)
.github/
  workflows/
    codex-marketplace-publish.yml  # implemented (T28)
```

## Ownership Rules

- `agent/codeforerunner.skill.md` is canonical.
- Generated or copied skill files must preserve canonical instruction content.
- Run `scripts/validate_skill_copies.py` after skill edits to check SPEC V10 body parity.
- Agent metadata files stay small and agent-specific.
- Installer owns only files below known codeforerunner package paths and marker-fenced blocks it creates.
- Uninstall removes only owned files/blocks.

## Agent Instructions

The skill should tell agents to:

- inspect the target repo first,
- use `prompts/system/base.md` as the governing instruction source,
- assemble repo context using `prompts/partials/context-format.md`,
- run `prompts/tasks/scan.md` before downstream task prompts,
- use task prompts from `prompts/tasks/` for README, API docs, stack docs, diagrams, flows, version audits, checks, and reviews,
- respect `forerunner.config.yaml` as the canonical config name (schema loaded by `src/codeforerunner/config.py`),
- report generated file changes and stale-doc failures clearly,
- avoid sending excluded or secret paths to external model providers,
- stop before destructive overwrites unless the prompt output gives an explicit managed-section strategy.

Naming convention: repo/product `codeforerunner`; CLI/config `forerunner`; canonical config filename `forerunner.config.yaml`.

The skill should avoid duplicating full product requirements. It should route to the prompt pack and repo-local docs.

## Installer Interface

The installer is the Python `forerunner install` subcommand (T18). It targets one agent per invocation:

```bash
forerunner install codex             # install skill into ~/.codex/skills/codeforerunner/SKILL.md
forerunner install claude            # install into ~/.claude/plugins/codeforerunner/skills/codeforerunner/SKILL.md
forerunner install generic --path PATH    # custom destination
forerunner install <agent> --check        # dry-run; print plan, write nothing
forerunner install codex --marketplace    # install plugins/codex/marketplace.json into ~/.codex/marketplaces/
```

Uninstall and doctor commands are not implemented; the installer aborts when a destination exists without managed-region markers, so user content is never silently overwritten.

The one-line `install.sh` / `install.ps1` / `bin/install-agent.js` shape from earlier drafts is not planned; the Python CLI subsumes that route.

## Installer Behavior

Implemented (T18, T24):

- resolve the agent-specific destination (`codex`, `claude`, or `generic` with `--path`),
- compare source body against the canonical skill (`agent/codeforerunner.skill.md`); abort with `EXIT_BODY_MISMATCH` on drift (V10),
- wrap the body in `<!-- forerunner:begin managed=codeforerunner.skill -->` / `<!-- forerunner:end -->` markers,
- create parent directories as needed,
- on rerun, overlay only the managed region; preserve any user content outside the markers (V12),
- skip the write when the rendered output already matches the destination hash (V12 idempotent),
- abort with `EXIT_UNMANAGED_DEST` when the destination exists without markers, refusing to overwrite user content,
- print a `create` / `update` / `skip` / `abort` plan line (prefixed with `would ` when `--check` is passed).

Not implemented (not currently planned):

- `forerunner install uninstall` / `forerunner install doctor` — out of scope until a real need surfaces.
- Bulk install across all agents in one invocation — call `forerunner install <agent>` per target instead.

## Target Packages

Codex:

- package as `plugins/codeforerunner/`,
- include `.codex-plugin/plugin.json`,
- include `skills/codeforerunner/SKILL.md`,
- set plugin interface metadata for repository documentation, generated docs, diagrams, flow docs, and stale-doc checks.

Claude Code:

- package as repo-root Claude Code plugin metadata plus skill directory,
- include `.claude-plugin/plugin.json`,
- include `skills/codeforerunner/SKILL.md`,
- do not ship hooks that silently generate docs against user repos.

Generic:

- reuse the root `skills/codeforerunner/SKILL.md` file shipped for Claude,
- include manual setup notes for agents that support Markdown instructions but not package metadata.

## Validation

Tests should cover:

- package file presence,
- plugin metadata parses as JSON,
- skill copy body parity with `scripts/validate_skill_copies.py`,
- install creates expected files in temp agent roots,
- rerun is idempotent,
- uninstall removes only owned files and marker blocks,
- unsupported targets produce generic fallback guidance,
- `--only` limits touched targets.
- Codex marketplace generation writes `policy.installation`, `policy.authentication`, and `category`.
- Claude install support places `.claude-plugin/plugin.json` and `skills/codeforerunner/SKILL.md` where Claude expects them without using the Codex marketplace format.

## Open Decisions

- Whether to add an `uninstall` subcommand once a concrete user need appears (today the managed-region markers make manual removal tractable).
- Whether `forerunner install codex --marketplace` should learn a `--repository` flag for marketplaces other than the default `~/.codex/marketplaces/`.
- Whether to expose body-parity validation as a standalone CLI subcommand instead of a separate `scripts/validate_skill_copies.py` script.
