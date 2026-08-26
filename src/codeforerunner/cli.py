"""Thin CLI orchestration. Product logic lives in prompts/."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from codeforerunner.bundle import find_prompts_root
from codeforerunner.prompt_session import OutcomeKind, PromptSession
from codeforerunner.tasks import refresh_tasks as _refresh_tasks
SCAN_DONE_ENV = "FORERUNNER_SCAN_DONE"


def _scan_satisfied(repo_root: Path) -> bool:
    """CLI scan-first signal: scan artifact present, env override set, or no config to gate."""
    return (
        (repo_root / ".forerunner" / "scan.md").is_file()
        or bool(os.environ.get(SCAN_DONE_ENV))
        or not (repo_root / "forerunner.config.yaml").is_file()
    )


def _resolve_bundle(repo, task: str) -> tuple[str, int]:
    """Resolve bundle text for *task* under *repo*. Returns (text, exit_code).

    Encodes the session's closed Outcome into CLI exit codes; the gate/order
    lives in the Prompt Session, this is just the encoder.
    """
    try:
        prompts_root = find_prompts_root(repo)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return "", 2

    repo_root = Path(repo).resolve() if repo else Path.cwd()
    session = PromptSession(prompts_root, _scan_satisfied(repo_root))
    outcome = session.resolve(task)
    if outcome.kind is OutcomeKind.ALLOWED:
        return outcome.text, 0
    if outcome.kind is OutcomeKind.UNKNOWN_TASK:
        print(f"error: unknown task '{task}'", file=sys.stderr)
        return "", 2
    if outcome.kind is OutcomeKind.SCAN_REQUIRED:
        print(
            f"error: scan-first required — run `forerunner scan` first "
            f"(writes .forerunner/scan.md). Set {SCAN_DONE_ENV}=1 to skip.",
            file=sys.stderr,
        )
        return "", 1
    # MISSING
    print(f"error: {outcome.message}", file=sys.stderr)
    return "", 2


def _emit_task(repo, task: str) -> int:
    """Resolve *task* under *repo* and write its bundle to stdout. Returns rc."""
    bundle, rc = _resolve_bundle(repo, task)
    if rc != 0:
        return rc
    sys.stdout.write(bundle)
    return 0


def cmd_doc(args: argparse.Namespace) -> int:
    """Resolve base + partials + task bundle to stdout."""
    return _emit_task(args.repo, args.task)


def cmd_init(args: argparse.Namespace) -> int:
    """Emit onboarding bundle; prepend scan bundle when --full is given."""
    repo = getattr(args, "repo", None)
    if getattr(args, "full", False):
        sys.stdout.write("<!-- forerunner init --full: section 1/2 (scan) -->\n")
        rc = _emit_task(repo, "scan")
        if rc != 0:
            return rc
        sys.stdout.write("\n<!-- forerunner init --full: section 2/2 (onboarding) -->\n")
    return _emit_task(repo, "init-agent-onboarding")


def cmd_scan(args: argparse.Namespace) -> int:
    """Emit the scan prompt bundle and hint about scan artifact."""
    rc = _emit_task(getattr(args, "repo", None), "scan")
    if rc == 0:
        print(
            "hint: write the scan result to .forerunner/scan.md to satisfy the "
            f"scan-first gate on follow-up calls. Or set {SCAN_DONE_ENV}=1 to skip.",
            file=sys.stderr,
        )
    return rc


def cmd_check(args: argparse.Namespace) -> int:
    """Run check rules when forerunner.config.yaml present. Silent no-op otherwise."""
    root = Path(args.repo).resolve() if args.repo else Path.cwd()
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
    """Start the stdio MCP server exposing prompt bundles as tools."""
    from codeforerunner import mcp_server
    try:
        prompts_root = find_prompts_root(args.repo)
    except FileNotFoundError as e:
        print(f"mcp_server: {e}", file=sys.stderr)
        return 2
    repo_root = Path(args.repo).resolve() if args.repo else Path.cwd()
    return mcp_server.serve(prompts_root, repo_root=repo_root)


def cmd_refresh(args: argparse.Namespace) -> int:
    """Emit scan + check + all doc-task bundles to stdout for a full doc refresh."""
    repo = getattr(args, "repo", None)
    task_names = [t.name for t in _refresh_tasks()]
    for i, task in enumerate(task_names):
        rc = _emit_task(repo, task)
        if rc != 0:
            return rc
        if i < len(task_names) - 1:
            sys.stdout.write("\n---\n\n")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """Run health checks and print a single-screen report; exit 1 on errors."""
    from codeforerunner import doctor
    from codeforerunner.config import CONFIG_FILENAME
    root = Path(args.repo).resolve() if args.repo else Path.cwd()
    if getattr(args, "fix", False):
        cfg_path = root / CONFIG_FILENAME
        if not cfg_path.is_file():
            cfg_path.write_text(doctor.starter_config(), encoding="utf-8")
            print(f"wrote {cfg_path}", file=sys.stderr)
        else:
            print(f"{cfg_path} already exists; skipping --fix", file=sys.stderr)
    findings = doctor.run(root, run_scripts=getattr(args, "run_scripts", False))
    sys.stdout.write(doctor.format_report(findings) + "\n")
    return 1 if any(f.severity == "error" for f in findings) else 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser with all subcommands registered."""
    p = argparse.ArgumentParser(
        prog="forerunner",
        description="Prompt-first repo documentation tooling. Thin CLI; product logic in prompts/.",
    )
    p.add_argument("--repo", default=argparse.SUPPRESS, help="path to repo root")
    from codeforerunner import __version__ as _version
    p.add_argument("--version", action="version", version=f"forerunner {_version}")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="<cmd>")

    # Every subcommand also accepts `--repo` so `forerunner <cmd> --repo X` and
    # `forerunner --repo X <cmd>` are interchangeable (#108). SUPPRESS keeps the
    # top-level value when the flag is only given before the subcommand.
    repo_parent = argparse.ArgumentParser(add_help=False)
    repo_parent.add_argument("--repo", default=argparse.SUPPRESS, help="path to repo root")

    s_init = sub.add_parser("init", parents=[repo_parent], help="resolve init-agent-onboarding prompt bundle to stdout")
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

    s_scan = sub.add_parser("scan", parents=[repo_parent], help="resolve scan prompt bundle to stdout")
    s_scan.set_defaults(func=cmd_scan)

    s_doc = sub.add_parser("doc", parents=[repo_parent], help="resolve prompt bundle for <task> to stdout")
    s_doc.add_argument("task", help="task name (basename without .md) under prompts/tasks/")
    s_doc.set_defaults(func=cmd_doc)

    s_check = sub.add_parser("check", parents=[repo_parent], help="run drift-detection rules against tracked docs")
    s_check.set_defaults(func=cmd_check)

    s_mcp = sub.add_parser("mcp-server", help="serve prompt bundles as MCP tools over stdio")
    s_mcp.add_argument(
        "--repo",
        default=argparse.SUPPRESS,
        help="path containing prompts/tasks/ (default: package-bundled prompts)",
    )
    s_mcp.set_defaults(func=cmd_mcp_server)

    s_doctor = sub.add_parser("doctor", parents=[repo_parent], help="health report: skill parity + marketplace + installed dests")
    s_doctor.add_argument(
        "--fix",
        action="store_true",
        help="write a starter forerunner.config.yaml if absent",
    )
    s_doctor.add_argument(
        "--run-scripts",
        dest="run_scripts",
        action="store_true",
        default=False,
        help="allow executing Python scripts from the target repo to validate skill copies (off by default)",
    )
    s_doctor.set_defaults(func=cmd_doctor)

    s_refresh = sub.add_parser("refresh", parents=[repo_parent], help="output all doc-refresh bundles in sequence (scan + check + all tasks)")
    s_refresh.set_defaults(func=cmd_refresh)

    from codeforerunner import installer
    installer.add_subparser(sub, parents=[repo_parent])

    return p


def main(argv: Sequence[str] | None = None) -> int:
    """Parse argv and dispatch to the appropriate subcommand handler."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "repo"):
        args.repo = None
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
