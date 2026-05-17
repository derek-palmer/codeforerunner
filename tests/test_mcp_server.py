"""Subprocess-based integration tests for the stdio MCP server."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
READ_TIMEOUT = 5.0


class _Server:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "codeforerunner.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(REPO),
            text=True,
            bufsize=1,
        )

    def request(self, msg: dict) -> dict:
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            stderr = self.proc.stderr.read() if self.proc.stderr else ""
            raise RuntimeError(f"server closed stdout without response. stderr={stderr!r}")
        return json.loads(line)

    def notify(self, msg: dict) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def close(self) -> None:
        try:
            if self.proc.stdin and not self.proc.stdin.closed:
                self.proc.stdin.close()
            try:
                self.proc.wait(timeout=READ_TIMEOUT)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        finally:
            for stream in (self.proc.stdout, self.proc.stderr):
                if stream and not stream.closed:
                    stream.close()


@pytest.fixture
def server():
    s = _Server()
    try:
        yield s
    finally:
        s.close()


def test_initialize(server: _Server) -> None:
    resp = server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["id"] == 1
    result = resp["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert result["serverInfo"] == {"name": "codeforerunner", "version": "0.2.0"}
    assert "tools" in result["capabilities"]


def test_tools_list_contains_scan(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    server.notify({"jsonrpc": "2.0", "method": "notifications/initialized"})
    resp = server.request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = resp["result"]["tools"]
    assert len(tools) >= 1
    names = [t["name"] for t in tools]
    assert "scan" in names
    for t in tools:
        assert "name" in t
        assert "description" in t and isinstance(t["description"], str) and t["description"]
        assert t["inputSchema"] == {"type": "object", "properties": {}, "required": []}


def test_tools_call_scan_returns_bundle(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    resp = server.request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "scan", "arguments": {}},
        }
    )
    result = resp["result"]
    assert result["isError"] is False
    text = result["content"][0]["text"]
    assert result["content"][0]["type"] == "text"
    scan_first_line = (REPO / "prompts" / "tasks" / "scan.md").read_text().splitlines()[0]
    assert scan_first_line in text


def test_tools_call_unknown(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    resp = server.request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "nonexistent", "arguments": {}},
        }
    )
    assert "error" in resp
    assert resp["error"]["code"] == -32602


def test_unknown_method(server: _Server) -> None:
    resp = server.request({"jsonrpc": "2.0", "id": 1, "method": "no/such/method", "params": {}})
    assert "error" in resp
    assert resp["error"]["code"] == -32601
