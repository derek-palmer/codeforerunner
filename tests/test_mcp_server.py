"""MCP server tests: subprocess integration + direct unit tests."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import codeforerunner
import pytest

REPO = Path(__file__).resolve().parents[1]
PROMPTS = Path(codeforerunner.__file__).parent / "prompts"
READ_TIMEOUT = 5.0


class _Server:
    def __init__(self, cwd: str | None = None) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "codeforerunner.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd if cwd is not None else str(REPO),
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
    assert result["protocolVersion"] == "2025-03-26"
    from codeforerunner import __version__
    assert result["serverInfo"] == {"name": "codeforerunner", "version": __version__}
    assert "tools" in result["capabilities"]


def test_tools_list_contains_scan(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    server.notify({"jsonrpc": "2.0", "method": "notifications/initialized"})
    resp = server.request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = resp["result"]["tools"]
    assert len(tools) >= 1
    names = [t["name"] for t in tools]
    assert "scan" in names
    assert "arch-review" in names
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
    scan_first_line = (PROMPTS / "tasks" / "scan.md").read_text().splitlines()[0]
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
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    resp = server.request({"jsonrpc": "2.0", "id": 2, "method": "no/such/method", "params": {}})
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_tools_call_blocks_without_scan(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    resp = server.request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "readme", "arguments": {}},
        }
    )
    assert "error" in resp
    assert resp["error"]["code"] == -32000
    msg = resp["error"]["message"]
    assert "scan-first" in msg
    assert "V2" in msg


def test_tools_call_arch_review_blocks_without_scan(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    resp = server.request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "arch-review", "arguments": {}},
        }
    )
    assert "error" in resp
    assert resp["error"]["code"] == -32000


def test_tools_call_exempt_init_agent_onboarding(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    resp = server.request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "init-agent-onboarding", "arguments": {}},
        }
    )
    assert "error" not in resp
    assert resp["result"]["isError"] is False


def test_tools_call_allowed_after_scan(server: _Server) -> None:
    server.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    scan_resp = server.request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "scan", "arguments": {}},
        }
    )
    assert "error" not in scan_resp
    resp = server.request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "readme", "arguments": {}},
        }
    )
    assert "error" not in resp
    assert resp["result"]["isError"] is False


def test_tools_call_blocks_without_scan_artifact_on_restart(tmp_path) -> None:
    """A fresh server process with no scan artifact must block non-exempt calls."""
    s1 = _Server()
    try:
        s1.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        scan_resp = s1.request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "scan", "arguments": {}},
            }
        )
        assert "error" not in scan_resp
    finally:
        s1.close()

    s2 = _Server(cwd=str(tmp_path))
    try:
        s2.request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        resp = s2.request(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "readme", "arguments": {}},
            }
        )
        assert "error" in resp
        assert resp["error"]["code"] == -32000
    finally:
        s2.close()


# ── Unit tests (direct in-process; these count toward coverage) ──────────────

from codeforerunner.mcp_server import (
    PROTOCOL_VERSION,
    _description_for,
    _err,
    _handle,
    _ok,
    _tools,
    main as mcp_main,
    serve,
)


def _state() -> dict:
    return {"initialized": False, "scan_called": False}


def _initialized_state() -> dict:
    return {"initialized": True, "scan_called": False}


# ── _ok / _err ────────────────────────────────────────────────────────────────

def test_ok_shape():
    r = _ok(1, {"x": 1})
    assert r == {"jsonrpc": "2.0", "id": 1, "result": {"x": 1}}


def test_err_shape():
    r = _err(2, -32601, "not found")
    assert r == {"jsonrpc": "2.0", "id": 2, "error": {"code": -32601, "message": "not found"}}


# ── _description_for / _tools ─────────────────────────────────────────────────

def test_description_for_returns_first_nonempty_stripped(tmp_path):
    f = tmp_path / "task.md"
    f.write_text("\n## My Task\nBody\n")
    assert _description_for(f) == "My Task"


def test_description_for_empty_file_returns_stem(tmp_path):
    f = tmp_path / "my-task.md"
    f.write_text("\n\n")
    assert _description_for(f) == "my-task"


def test_tools_returns_registered_tasks_with_correct_shape():
    from codeforerunner.tasks import all_tasks
    tools = _tools(PROMPTS)
    registered_names = {t.name for t in all_tasks()}
    tool_names = {t["name"] for t in tools}
    assert tool_names == registered_names
    for tool in tools:
        assert set(tool.keys()) == {"name", "description", "inputSchema"}
        assert tool["inputSchema"] == {"type": "object", "properties": {}, "required": []}


# ── _handle ───────────────────────────────────────────────────────────────────

def test_handle_notifications_initialized_returns_none():
    msg = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    assert _handle(PROMPTS, msg, _state()) is None


def test_handle_notification_without_id_returns_none():
    msg = {"jsonrpc": "2.0", "method": "notifications/foo"}
    assert _handle(PROMPTS, msg, _state()) is None


def test_handle_initialize_sets_state_and_returns_ok():
    state = _state()
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, state)
    assert state["initialized"] is True
    assert resp["result"]["protocolVersion"] == PROTOCOL_VERSION
    assert resp["result"]["serverInfo"]["name"] == "codeforerunner"


def test_handle_not_initialized_returns_error():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, _state())
    assert resp["error"]["code"] == -32002


def test_handle_tools_list_returns_tools():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, _initialized_state())
    assert "tools" in resp["result"]
    assert any(t["name"] == "scan" for t in resp["result"]["tools"])


def test_handle_tools_call_invalid_name_slash():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "a/b"}}, _initialized_state())
    assert resp["error"]["code"] == -32602


def test_handle_tools_call_invalid_name_dotdot():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": ".."}}, _initialized_state())
    assert resp["error"]["code"] == -32602


def test_handle_tools_call_invalid_name_backslash():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "a\\b"}}, _initialized_state())
    assert resp["error"]["code"] == -32602


def test_handle_tools_call_unknown_tool():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "nonexistent-task"}}, _initialized_state())
    assert resp["error"]["code"] == -32602


def test_handle_tools_call_scan_first_required():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "readme"}}, _initialized_state())
    assert resp["error"]["code"] == -32000
    assert "scan-first" in resp["error"]["message"]


def test_handle_tools_call_scan_sets_scan_called():
    state = _initialized_state()
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "scan"}}, state)
    assert state["scan_called"] is True
    assert resp["result"]["isError"] is False


def test_handle_tools_call_init_agent_onboarding_exempt():
    state = _initialized_state()
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "init-agent-onboarding"}}, state)
    assert "error" not in resp
    assert resp["result"]["isError"] is False


def test_handle_tools_call_allowed_after_scan():
    state = _initialized_state()
    _handle(PROMPTS, {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "scan"}}, state)
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "readme"}}, state)
    assert "error" not in resp
    assert resp["result"]["isError"] is False


def test_handle_unknown_method():
    resp = _handle(PROMPTS, {"jsonrpc": "2.0", "id": 4, "method": "no/such"}, _initialized_state())
    assert resp["error"]["code"] == -32601


# ── serve ────────────────────────────────────────────────────────────────────

def test_serve_invalid_json_returns_parse_error():
    out = io.StringIO()
    err = io.StringIO()
    rc = serve(PROMPTS, stdin=["not-json\n"], stdout=out, stderr=err)
    assert rc == 0
    out.seek(0)
    resp = json.loads(out.readline())
    assert resp["error"]["code"] == -32700


def test_serve_empty_line_produces_no_output():
    out = io.StringIO()
    rc = serve(PROMPTS, stdin=["  \n", "\n"], stdout=out, stderr=io.StringIO())
    assert rc == 0
    out.seek(0)
    assert out.read() == ""


def test_serve_notification_produces_no_output():
    out = io.StringIO()
    msg = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
    rc = serve(PROMPTS, stdin=[msg], stdout=out, stderr=io.StringIO())
    assert rc == 0
    out.seek(0)
    assert out.read() == ""


def test_serve_initialize_response_written():
    out = io.StringIO()
    msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n"
    serve(PROMPTS, stdin=[msg], stdout=out, stderr=io.StringIO())
    out.seek(0)
    resp = json.loads(out.readline())
    assert resp["result"]["protocolVersion"] == PROTOCOL_VERSION


# ── mcp_main ──────────────────────────────────────────────────────────────────

def test_mcp_main_returns_2_when_prompts_not_found(tmp_path, capsys, monkeypatch):
    with patch("codeforerunner.mcp_server.find_prompts_root", side_effect=FileNotFoundError("no prompts")):
        rc = mcp_main()
    assert rc == 2
    assert "mcp_server:" in capsys.readouterr().err


def test_mcp_main_calls_serve_with_resolved_root(capsys):
    with patch("codeforerunner.mcp_server.serve", return_value=0) as mock_serve:
        rc = mcp_main()
    assert rc == 0
    mock_serve.assert_called_once()
    _, kwargs = mock_serve.call_args
    assert "repo_root" in kwargs
    assert kwargs["repo_root"] == Path.cwd().resolve()


# ── serve re-hydration from scan artifact ────────────────────────────────────

def _rpc(*msgs: dict) -> list[str]:
    return [json.dumps(m) + "\n" for m in msgs]


def _seed_prompts(path: Path) -> Path:
    """Create a minimal self-contained prompts root with one non-exempt task."""
    prompts = path / "prompts"
    (prompts / "system").mkdir(parents=True)
    (prompts / "system" / "base.md").write_text("# base\n", encoding="utf-8")
    (prompts / "partials").mkdir()
    (prompts / "tasks").mkdir()
    (prompts / "tasks" / "scan.md").write_text("# Scan\n", encoding="utf-8")
    (prompts / "tasks" / "init-agent-onboarding.md").write_text("# Onboarding\n", encoding="utf-8")
    (prompts / "tasks" / "check.md").write_text("# Check Task\n", encoding="utf-8")
    return prompts


def test_serve_allows_non_exempt_when_scan_artifact_present(tmp_path):
    prompts_root = _seed_prompts(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".forerunner").mkdir()
    (repo_root / ".forerunner" / "scan.md").write_text("# scan result\n", encoding="utf-8")
    out = io.StringIO()
    msgs = _rpc(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "check"}},
    )
    serve(prompts_root, repo_root=repo_root, stdin=msgs, stdout=out, stderr=io.StringIO())
    out.seek(0)
    out.readline()  # initialize response
    resp = json.loads(out.readline())
    assert "error" not in resp
    assert resp["result"]["isError"] is False


def test_serve_blocks_non_exempt_when_scan_artifact_absent(tmp_path):
    prompts_root = _seed_prompts(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    out = io.StringIO()
    msgs = _rpc(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "check"}},
    )
    serve(prompts_root, repo_root=repo_root, stdin=msgs, stdout=out, stderr=io.StringIO())
    out.seek(0)
    out.readline()  # initialize response
    resp = json.loads(out.readline())
    assert "error" in resp
    assert resp["error"]["code"] == -32000
