# Output Rules — Partial

## Markdown Standards
- Use ATX-style headers (#, ##, ###) — never underline style
- Fenced code blocks must always include a language identifier
- Bold (**text**) for key terms on first use only
- Tables must have header rows

## File Output Format
When writing to a specific file, the first line must be:
<!-- output: path/to/output/file.md -->
Followed immediately by the file content. No preamble.

## Accuracy Rules
- Never document a function, endpoint, or behavior not present in the provided code
- Version numbers must come from lock files or manifests — never guess
- Environment variables must come from .env.example or explicit code references

## Diagram Rules (Mermaid)
- All diagrams use Mermaid syntax in a fenced ```mermaid block
- Node IDs: no spaces, no special characters except _ and -
- Use graph TD for top-down, graph LR for left-right pipelines
- Use sequenceDiagram for request/response flows
- Use erDiagram for data models
- Label all edges with action verbs
- Max ~20 nodes per section diagram, ~40 for master

## Length Guidelines
| Document type           | Target length               |
|-------------------------|-----------------------------|
| README                  | 150-400 lines               |
| API docs (per endpoint) | 20-60 lines                 |
| Stack doc               | 100-300 lines               |
| Master diagram          | 30-60 lines of Mermaid      |
| Section diagram         | 10-25 lines of Mermaid      |
| Flow doc                | 50-150 lines                |
| Version audit           | scales with component count |
| Check report            | 20-80 lines                 |
| Review summary          | 10-30 lines                 |
