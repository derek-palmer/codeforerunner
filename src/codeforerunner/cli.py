"""Thin CLI orchestration. Product logic lives in `prompts/`. See SPEC.md §D.cli."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence


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


def _stub(name: str) -> int:
    print(
        f"forerunner {name}: not yet implemented; see SPEC.md §D.cli (V11 design-only).",
        file=sys.stderr,
    )
    return 2


def cmd_init(_: argparse.Namespace) -> int:
    return _stub("init")


def cmd_scan(_: argparse.Namespace) -> int:
    return _stub("scan")


def cmd_check(args: argparse.Namespace) -> int:
    """Stub. Honest exit: 0 when no config; 0 + notice when config present (no rules wired)."""
    try:
        root = _repo_root(Path(args.repo) if args.repo else None)
    except FileNotFoundError:
        root = Path.cwd()
    cfg = root / "forerunner.config.yaml"
    if not cfg.is_file():
        # Hook contract: silent no-op when project hasn't opted in.
        return 0
    print(
        "forerunner check: config detected but no check rules wired yet (SPEC §D.hooks).",
        file=sys.stderr,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="forerunner",
        description="Prompt-first repo documentation tooling. Thin CLI; product logic in prompts/.",
    )
    p.add_argument("--repo", help="path to repo root (defaults to cwd ancestor with prompts/tasks/)")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="<cmd>")

    s_init = sub.add_parser("init", help="onboarding orchestration (stub)")
    s_init.set_defaults(func=cmd_init)

    s_scan = sub.add_parser("scan", help="run scan pipeline (stub)")
    s_scan.set_defaults(func=cmd_scan)

    s_doc = sub.add_parser("doc", help="resolve prompt bundle for <task> to stdout")
    s_doc.add_argument("task", help="task name (basename without .md) under prompts/tasks/")
    s_doc.set_defaults(func=cmd_doc)

    s_check = sub.add_parser("check", help="run check prompts against tracked docs (stub)")
    s_check.set_defaults(func=cmd_check)

    from codeforerunner import installer
    installer.add_subparser(sub)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
