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

Codex slice (`plugins/codeforerunner/.codex-plugin/plugin.json` + `plugins/codeforerunner/skills/codeforerunner/SKILL.md`) is implemented (SPEC T13). Claude slice (`.claude-plugin/plugin.json` + `skills/codeforerunner/SKILL.md`) is implemented (SPEC T14). Generic installer-driven distribution remains proposed (SPEC T15) and reuses the same root `skills/codeforerunner/SKILL.md` file rather than a separate generic-only skill file.

```text
agent/
  codeforerunner.skill.md
  templates/                  # planned (T15)
    codex-plugin.json         # planned (T15)
    claude-plugin.json        # planned (T15)
    generic-skill.md          # planned (T15)
bin/                          # planned (T15)
  install-agent.js            # planned (T15)
install.sh                    # planned (T15)
install.ps1                   # planned (T15)
plugins/
  codeforerunner/
    .codex-plugin/
      plugin.json             # implemented (T13)
    skills/
      codeforerunner/
        SKILL.md              # implemented (T13)
.claude-plugin/               # implemented (T14)
  plugin.json                 # implemented (T14)
skills/                       # implemented for Claude (T14), reused by generic distribution (T15)
  codeforerunner/             # implemented (T14)
    SKILL.md                  # implemented (T14)
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
- respect `forerunner.config.yaml` as the canonical config name, using the tracked example shape only until a real loader exists,
- report generated file changes and stale-doc failures clearly,
- avoid sending excluded or secret paths to external model providers,
- stop before destructive overwrites unless the prompt output gives an explicit managed-section strategy.

Naming convention: repo/product `codeforerunner`; CLI/config `forerunner`; canonical config filename `forerunner.config.yaml`.

The skill should avoid duplicating full product requirements. It should route to the prompt pack and repo-local docs.

## Installer Interface

Future CLI commands, once thin wrappers exist:

```bash
forerunner agent install
forerunner agent install --only codex
forerunner agent install --only claude
forerunner agent uninstall
forerunner agent doctor
```

Design example; standalone wrappers are planned and not currently runnable:

```bash
bash install.sh --only codex
pwsh ./install.ps1 --only claude
```

Design example; one-line shell install is planned and not currently runnable:

```bash
curl -fsSL https://raw.githubusercontent.com/derek-palmer/codeforerunner/main/install.sh | bash
```

Design example; one-line PowerShell install is planned and not currently runnable:

```powershell
irm https://raw.githubusercontent.com/derek-palmer/codeforerunner/main/install.ps1 | iex
```

## Installer Behavior

Install:

- detect known agent roots,
- copy owned skill/plugin artifacts,
- create or update a repo-local marketplace entry when Codex UI discovery is in scope,
- install or register Claude package artifacts through Claude-specific discovery paths when Claude support is in scope,
- create parent directories as needed,
- append marker-fenced global instruction blocks only when required by a target agent,
- avoid duplicate blocks on rerun,
- print installed/skipped/failed targets.

Uninstall:

- remove owned skill/plugin files,
- remove marker-fenced blocks,
- leave unrelated user files untouched,
- print removed/skipped targets.

Doctor:

- check expected files exist,
- validate JSON metadata,
- verify canonical instruction hash or content match where practical,
- report stale copied artifacts.

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

- Whether `bin/install-agent.js` is the first implementation or waits until package layout stabilizes.
- Whether future `forerunner agent install` shells out to Node or uses Python for local installs.
- Whether installer templates should copy from `agent/codeforerunner.skill.md` every run or fail fast when `scripts/validate_skill_copies.py` reports drift.
