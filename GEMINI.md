# codeforerunner — Gemini CLI context

Model-agnostic repository documentation tooling. Ships prompt packs for codebase analysis, doc generation, drift detection, and agent onboarding. Python CLI + MCP server + agent skills.

## Available tasks

Run any task via `forerunner doc <task>`, or use the installed Gemini extension skills:

| Slash command | Task | Description |
|---|---|---|
| `/forerunner-scan` | `scan` | Scan repo; always run first |
| `/forerunner-readme` | `readme` | Generate or refresh README.md |
| `/forerunner-api-docs` | `api-docs` | Generate API reference |
| `/forerunner-diagrams` | `diagrams` | Generate Mermaid architecture diagrams |
| `/forerunner-flows` | `flows` | Document system flows |
| `/forerunner-stack-docs` | `stack-docs` | Stack-specific developer docs |
| `/forerunner-version-audit` | `version-audit` | Audit pinned versions vs EOL |
| `/forerunner-check` | `check` | Check docs for staleness |
| `/forerunner-review` | `review` | Doc-impact summary for PR review |
| `/forerunner-audit` | `audit` | Security and dependency audit |
| `/forerunner-changelog` | `changelog` | Generate changelog entry from git log |
| `/forerunner-init` | `init-agent-onboarding` | Bootstrap or refresh AGENTS.md |

## Workflow

1. Start with `/forerunner-scan` to collect repo evidence.
2. Run the documentation task you need.
3. Use `/forerunner-check` before commits to detect drift.

## CLI quick reference

```bash
forerunner doc <task>         # Get composed prompt for a task
forerunner generate <task>    # Call configured provider directly
forerunner check              # Run drift-detection rules
forerunner doctor             # Health report
forerunner install gemini     # Install skills to Gemini config dir
```

## Config

Drop a `forerunner.config.yaml` at repo root to enable drift rules. Run `forerunner doctor --fix` to generate a starter config.

## Sources

- Prompts: `src/codeforerunner/prompts/tasks/`
- Skills: `skills/` (source) → `plugins/codeforerunner/skills/` (distribution)
- Repo: https://github.com/derek-palmer/codeforerunner
