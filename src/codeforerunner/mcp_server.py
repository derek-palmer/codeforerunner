"""Minimal stdio MCP server exposing prompt bundles as tools.

Hand-rolled JSON-RPC 2.0 over line-delimited stdio. Stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

from codeforerunner import __version__ as _pkg_version
from codeforerunner.bundle import find_prompts_root, resolve_bundle
from codeforerunner.tasks import all_tasks as _all_tasks
from codeforerunner.tasks import scan_exempt_names as _scan_exempt_names

PROTOCOL_VERSION = "2025-03-26"
SERVER_NAME = "codeforerunner"
SERVER_VERSION = _pkg_version


def _description_for(task_path: Path) -> str:
    """First non-empty markdown line, stripped of leading '#' and whitespace."""
    with task_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            return line.lstrip("#").strip()
    return task_path.stem


def _tools(prompts_root: Path) -> list[dict[str, Any]]:
    """Build MCP tools/list payload from registered tasks."""
    return [
        {
            "name": task.name,
            "description": _description_for(prompts_root / "tasks" / f"{task.name}.md"),
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        }
        for task in _all_tasks()
    ]


def _ok(req_id: Any, result: Any) -> dict[str, Any]:
    """Return a JSON-RPC 2.0 success response."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id: Any, code: int, message: str) -> dict[str, Any]:
    """Return a JSON-RPC 2.0 error response."""
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _handle(prompts_root: Path, msg: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    """Dispatch a single JSON-RPC message; return response dict or None for notifications."""
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}

    if method == "notifications/initialized":
        return None
    if req_id is None and isinstance(method, str) and method.startswith("notifications/"):
        return None

    if method == "initialize":
        state["initialized"] = True
        return _ok(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if not state.get("initialized"):
        return _err(req_id, -32002, "Server not initialized")

    if method == "tools/list":
        return _ok(req_id, {"tools": _tools(prompts_root)})

    if method == "tools/call":
        name = params.get("name")
        if not isinstance(name, str) or "/" in name or "\\" in name or ".." in name:
            return _err(req_id, -32602, f"invalid tool name: {name!r}")
        task_path = prompts_root / "tasks" / f"{name}.md"
        tasks_root = (prompts_root / "tasks").resolve()
        if not task_path.resolve().is_relative_to(tasks_root) or not task_path.is_file():
            return _err(req_id, -32602, f"unknown tool: {name!r}")
        if name not in _scan_exempt_names() and not state.get("scan_called"):
            return _err(
                req_id,
                -32000,
                "scan-first required: call tools/call name=scan before this task (SPEC V2)",
            )
        if name == "scan":
            state["scan_called"] = True
        try:
            text = resolve_bundle(prompts_root, name)
        except Exception as e:  # pragma: no cover - defensive
            return _err(req_id, -32603, f"internal error: {e}")
        return _ok(
            req_id,
            {"content": [{"type": "text", "text": text}], "isError": False},
        )

    return _err(req_id, -32601, f"method not found: {method!r}")


def serve(
    prompts_root: Path,
    repo_root: Path | None = None,
    stdin: Iterable[str] = sys.stdin,
    stdout=sys.stdout,
    stderr=sys.stderr,
) -> int:
    """Run the JSON-RPC 2.0 MCP server loop over *stdin*/*stdout* until EOF."""
    root = repo_root if repo_root is not None else Path.cwd()
    scan_artifact = root / ".forerunner" / "scan.md"
    state: dict[str, Any] = {"scan_called": scan_artifact.is_file(), "initialized": False}
    for raw in stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"mcp_server: invalid JSON: {e}", file=stderr)
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()
            continue

        try:
            resp = _handle(prompts_root, msg, state)
        except Exception as e:  # pragma: no cover - defensive
            print(f"mcp_server: handler error: {e}", file=stderr)
            resp = _err(msg.get("id"), -32603, f"internal error: {e}")

        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Locate prompts root and start the MCP server; returns 2 if prompts not found."""
    try:
        prompts_root = find_prompts_root()
    except FileNotFoundError as e:
        print(f"mcp_server: {e}", file=sys.stderr)
        return 2
    return serve(prompts_root, repo_root=Path.cwd().resolve())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
