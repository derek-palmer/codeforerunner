"""Minimal stdio MCP server exposing prompt bundles as tools. See SPEC.md §D.mcp.

Hand-rolled JSON-RPC 2.0 over line-delimited stdio. Stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "codeforerunner"
SERVER_VERSION = "0.2.0"


def _repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "prompts" / "tasks").is_dir():
            return candidate
    raise FileNotFoundError(
        "could not locate codeforerunner repo root (no prompts/tasks/ found upward)"
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_bundle(repo: Path, task: str) -> str:
    """Concatenate system/base.md + sorted partials/*.md + tasks/<task>.md with marker comments."""
    task_path = repo / "prompts" / "tasks" / f"{task}.md"
    if not task_path.is_file():
        raise FileNotFoundError(f"unknown task '{task}' (no {task_path})")

    parts: list[str] = []
    base = repo / "prompts" / "system" / "base.md"
    if base.is_file():
        parts.append(f"<!-- system: base.md -->\n{_read(base).rstrip()}")

    partials_dir = repo / "prompts" / "partials"
    if partials_dir.is_dir():
        for p in sorted(partials_dir.glob("*.md")):
            parts.append(f"<!-- partial: {p.name} -->\n{_read(p).rstrip()}")

    parts.append(f"<!-- task: {task_path.name} -->\n{_read(task_path).rstrip()}")
    return "\n\n".join(parts) + "\n"


def _list_tasks(repo: Path) -> list[Path]:
    tasks_dir = repo / "prompts" / "tasks"
    if not tasks_dir.is_dir():
        return []
    return sorted(tasks_dir.glob("*.md"))


def _description_for(task_path: Path) -> str:
    """First non-empty markdown line, stripped of leading '#' chars and whitespace."""
    for raw in task_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        return line.lstrip("#").strip()
    return task_path.stem


def _tools(repo: Path) -> list[dict[str, Any]]:
    return [
        {
            "name": p.stem,
            "description": _description_for(p),
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        }
        for p in _list_tasks(repo)
    ]


def _ok(req_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


SCAN_EXEMPT_TOOLS = frozenset({"init-agent-onboarding", "scan"})


def _handle(repo: Path, msg: dict[str, Any], state: dict[str, Any]) -> dict[str, Any] | None:
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}

    # Notifications: no id, no response.
    if method == "notifications/initialized":
        return None
    if req_id is None and isinstance(method, str) and method.startswith("notifications/"):
        return None

    if method == "initialize":
        return _ok(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "tools/list":
        return _ok(req_id, {"tools": _tools(repo)})

    if method == "tools/call":
        name = params.get("name")
        task_path = repo / "prompts" / "tasks" / f"{name}.md"
        if not isinstance(name, str) or not task_path.is_file():
            return _err(req_id, -32602, f"unknown tool: {name!r}")
        if name not in SCAN_EXEMPT_TOOLS and not state.get("scan_called"):
            return _err(
                req_id,
                -32000,
                "scan-first required: call tools/call name=scan before this task (SPEC V2)",
            )
        if name == "scan":
            state["scan_called"] = True
        try:
            text = resolve_bundle(repo, name)
        except Exception as e:  # pragma: no cover - defensive
            return _err(req_id, -32603, f"internal error: {e}")
        return _ok(
            req_id,
            {"content": [{"type": "text", "text": text}], "isError": False},
        )

    return _err(req_id, -32601, f"method not found: {method!r}")


def serve(repo: Path, stdin: Iterable[str] = sys.stdin, stdout=sys.stdout, stderr=sys.stderr) -> int:
    state: dict[str, Any] = {"scan_called": False}
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
            resp = _handle(repo, msg, state)
        except Exception as e:  # pragma: no cover - defensive
            print(f"mcp_server: handler error: {e}", file=stderr)
            resp = _err(msg.get("id"), -32603, f"internal error: {e}")

        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        repo = _repo_root()
    except FileNotFoundError as e:
        print(f"mcp_server: {e}", file=sys.stderr)
        return 2
    return serve(repo)


if __name__ == "__main__":
    raise SystemExit(main())
