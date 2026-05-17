"""Thin CLI orchestration. Product logic lives in `prompts/`. See SPEC.md §D.cli."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

SCAN_EXEMPT_TASKS = frozenset({"scan", "init-agent-onboarding"})
SCAN_DONE_ENV = "FORERUNNER_SCAN_DONE"


def _repo_root(start: Path | None = None) -> Path:
    """Walk up from cwd (or `start`) to a directory containing `prompts/tasks`."""
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "prompts" / "tasks").is_dir():
            return candidate
    raise FileNotFoundError(
        "could not locate codeforerunner repo root (no prompts/tasks/ found upward)"
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cmd_doc(args: argparse.Namespace) -> int:
    """Resolve `prompts/system/base.md` + `prompts/partials/*.md` + `prompts/tasks/<task>.md` to stdout."""
    root = _repo_root(Path(args.repo) if args.repo else None)
    task_path = root / "prompts" / "tasks" / f"{args.task}.md"
    if not task_path.is_file():
        print(f"error: unknown task '{args.task}' (no {task_path})", file=sys.stderr)
        return 2

    if (
        args.task not in SCAN_EXEMPT_TASKS
        and (root / "forerunner.config.yaml").is_file()
        and not os.environ.get(SCAN_DONE_ENV)
    ):
        print(
            f"warning: SPEC V2 scan-first — run `forerunner scan` first, "
            f"then export {SCAN_DONE_ENV}=1 to silence this warning.",
            file=sys.stderr,
        )

    parts: list[str] = []
    base = root / "prompts" / "system" / "base.md"
    if base.is_file():
        parts.append(f"<!-- system: base.md -->\n{_read(base).rstrip()}")

    partials_dir = root / "prompts" / "partials"
    if partials_dir.is_dir():
        for p in sorted(partials_dir.glob("*.md")):
            parts.append(f"<!-- partial: {p.name} -->\n{_read(p).rstrip()}")

    parts.append(f"<!-- task: {task_path.name} -->\n{_read(task_path).rstrip()}")
    sys.stdout.write("\n\n".join(parts) + "\n")
    return 0


def _doc_for(args: argparse.Namespace, task: str) -> int:
    ns = argparse.Namespace(repo=getattr(args, "repo", None), task=task)
    return cmd_doc(ns)


def cmd_init(args: argparse.Namespace) -> int:
    """Default + --agents-only = onboarding bundle only. --full prepends scan."""
    if getattr(args, "full", False):
        sys.stdout.write("<!-- forerunner init --full: section 1/2 (scan) -->\n")
        rc = _doc_for(args, "scan")
        if rc != 0:
            return rc
        sys.stdout.write("\n<!-- forerunner init --full: section 2/2 (onboarding) -->\n")
    return _doc_for(args, "init-agent-onboarding")


def cmd_scan(args: argparse.Namespace) -> int:
    rc = _doc_for(args, "scan")
    if rc == 0:
        print(
            f"hint: export {SCAN_DONE_ENV}=1 in this shell to silence "
            "scan-first warnings on follow-up `forerunner doc`/`init` calls.",
            file=sys.stderr,
        )
    return rc


def cmd_check(args: argparse.Namespace) -> int:
    """Run check rules when `forerunner.config.yaml` present. Silent no-op otherwise."""
    try:
        root = _repo_root(Path(args.repo) if args.repo else None)
    except FileNotFoundError:
        root = Path.cwd()
    from codeforerunner import check as _check
    from codeforerunner.config import ConfigError, load_from_repo
    try:
        cfg = load_from_repo(root)
    except ConfigError as e:
        print(f"forerunner check: invalid config: {e}", file=sys.stderr)
        return 2
    if cfg is None:
        return 0
    violations = _check.run(root, cfg.check)
    if not violations:
        return 0
    sys.stderr.write(_check.format_violations(violations) + "\n")
    return 1


def cmd_mcp_server(args: argparse.Namespace) -> int:
    from codeforerunner import mcp_server
    root = _repo_root(Path(args.repo) if args.repo else None)
    return mcp_server.serve(root)


def cmd_doctor(args: argparse.Namespace) -> int:
    from codeforerunner import doctor
    root = _repo_root(Path(args.repo) if args.repo else None)
    findings = doctor.run(root)
    sys.stdout.write(doctor.format_report(findings) + "\n")
    return 1 if any(f.severity == "error" for f in findings) else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="forerunner",
        description="Prompt-first repo documentation tooling. Thin CLI; product logic in prompts/.",
    )
    p.add_argument("--repo", help="path to repo root (defaults to cwd ancestor with prompts/tasks/)")
    from codeforerunner import __version__ as _version
    p.add_argument("--version", action="version", version=f"forerunner {_version}")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="<cmd>")

    s_init = sub.add_parser("init", help="resolve init-agent-onboarding prompt bundle to stdout")
    init_scope = s_init.add_mutually_exclusive_group()
    init_scope.add_argument(
        "--full",
        action="store_true",
        help="prepend scan bundle before the onboarding bundle (scan-first per V2)",
    )
    init_scope.add_argument(
        "--agents-only",
        action="store_true",
        help="explicit alias for the default scope (AGENTS.md update only)",
    )
    s_init.set_defaults(func=cmd_init)

    s_scan = sub.add_parser("scan", help="resolve scan prompt bundle to stdout")
    s_scan.set_defaults(func=cmd_scan)

    s_doc = sub.add_parser("doc", help="resolve prompt bundle for <task> to stdout")
    s_doc.add_argument("task", help="task name (basename without .md) under prompts/tasks/")
    s_doc.set_defaults(func=cmd_doc)

    s_check = sub.add_parser("check", help="run drift-detection rules against tracked docs")
    s_check.set_defaults(func=cmd_check)

    s_mcp = sub.add_parser("mcp-server", help="serve prompt bundles as MCP tools over stdio")
    s_mcp.set_defaults(func=cmd_mcp_server)

    s_doctor = sub.add_parser("doctor", help="health report: skill parity + marketplace + installed dests")
    s_doctor.set_defaults(func=cmd_doctor)

    from codeforerunner import installer
    installer.add_subparser(sub)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
