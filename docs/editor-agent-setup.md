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
2. Ensure it points to `prompts/system/base.md`.
3. Include `prompts/partials/context-format.md` and `prompts/partials/output-rules.md` in the agent context.
4. Run `prompts/tasks/scan.md` before any downstream task.

## Usage Notes

- Keep target repo context selective but evidence-rich.
- Prefer config, manifests, entrypoints, and existing docs over random leaf files.
- If the agent asks for a command, verify the target repo actually defines it.
- Do not tell the agent to install or run `forerunner`; no runtime wrapper exists yet.

## Maintenance

When prompt contracts change, update both:

- `codeforerunner_spec.md`
- affected files in `agent-configs/`
