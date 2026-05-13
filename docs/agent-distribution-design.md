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

## Proposed Layout

```text
agent/
  codeforerunner.skill.md
  templates/
    codex-plugin.json
    claude-plugin.json
    generic-skill.md
bin/
  install-agent.js
install.sh
install.ps1
plugins/
  codeforerunner/
    .codex-plugin/
      plugin.json
    skills/
      codeforerunner/
        SKILL.md
.claude-plugin/
  plugin.json
skills/
  codeforerunner/
    SKILL.md
```

## Ownership Rules

- `agent/codeforerunner.skill.md` is canonical.
- Generated or copied skill files must preserve canonical instruction content.
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

- support skill directory or `.claude-plugin/plugin.json`, depending on validated current convention,
- hooks may activate or expose commands,
- hooks must not silently generate docs against user repos.

Generic:

- ship `skills/codeforerunner/SKILL.md`,
- include manual setup notes for agents that support Markdown instructions but not package metadata.

## Validation

Tests should cover:

- package file presence,
- plugin metadata parses as JSON,
- install creates expected files in temp agent roots,
- rerun is idempotent,
- uninstall removes only owned files and marker blocks,
- unsupported targets produce generic fallback guidance,
- `--only` limits touched targets.

## Open Decisions

- Whether `bin/install-agent.js` is the first implementation or waits until package layout stabilizes.
- Whether future `forerunner agent install` shells out to Node or uses Python for local installs.
- Which Claude package convention is current enough to support as first-class.
- Whether copied skill files are generated at build time or checked in as committed artifacts.
