# MCP Examples

`forerunner mcp-server` runs over stdio from repo root and exposes one MCP tool per `prompts/tasks/*.md`.

## Claude Desktop

Add an entry like this to your Claude Desktop config, replacing `/path/to/codeforerunner` with the checkout path:

```json
{
  "mcpServers": {
    "codeforerunner": {
      "command": "forerunner",
      "args": ["--repo", "/path/to/codeforerunner", "mcp-server"]
    }
  }
}
```

If `forerunner` is not on Claude Desktop's `PATH`, use an absolute command path such as `/path/to/venv/bin/forerunner`.

## mcp-cli

Use the same command shape with any stdio-capable MCP client:

```bash
mcp-cli tools --server "forerunner --repo /path/to/codeforerunner mcp-server"
```

Call `scan` before non-exempt documentation tools. The server enforces SPEC V2 per process: `readme`, `api-docs`, `stack-docs`, and similar tools return a scan-first error until `scan` succeeds in that session.
