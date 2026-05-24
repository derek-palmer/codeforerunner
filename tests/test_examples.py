from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_mcp_examples_present_and_reference_server():
    readme = REPO / "examples/mcp/README.md"
    config = REPO / "examples/mcp/claude-desktop.json"

    text = readme.read_text(encoding="utf-8")
    assert "Claude Desktop" in text
    assert "mcp-cli" in text
    assert "forerunner" in text
    assert "mcp-server" in text
    assert "scan" in text

    data = json.loads(config.read_text(encoding="utf-8"))
    server = data["mcpServers"]["codeforerunner"]
    assert server["command"] == "forerunner"
    assert server["args"][-1] == "mcp-server"
