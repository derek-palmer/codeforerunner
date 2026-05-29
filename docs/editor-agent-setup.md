# Editor Agent Setup

Use `agent-configs/` as copyable starting points for editor-agent instructions.

## Available Configs

| File | Target |
| --- | --- |
| `agent-configs/claude-project.md` | Claude Project instructions |
| `agent-configs/cursor-rules.md` | Cursor rules |
| `agent-configs/copilot-instructions.md` | GitHub Copilot instructions |
| `agent-configs/cline.md` | Cline or Roo-style agents |
| `agent-configs/windsurf.md` | Windsurf instructions |

## Setup Pattern

1. Copy the matching config into your editor's instruction surface.
2. Point it at the system prompt (`forerunner doc scan` emits the full assembled bundle, or read `src/codeforerunner/prompts/system/base.md` directly from source).
3. Include `partials/context-format.md` and `partials/output-rules.md` in the agent context.
4. Run the `scan` task before any downstream task.

## Usage Notes

- Keep target repo context selective but evidence-rich.
- Prefer config, manifests, entrypoints, and existing docs over random leaf files.
- If the agent asks for a command, verify the target repo actually defines it.
- `forerunner` is installed via `pip install codeforerunner`; agents can call `forerunner doc <task>` to get assembled prompt bundles.

## Maintenance

When prompt contracts change, update affected files in `agent-configs/`.
