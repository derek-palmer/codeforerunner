"""Idempotent skill installer. See SPEC.md §D.installer (cites V8, V10, V11, V12)."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

MARKER_BEGIN = "<!-- forerunner:begin managed=codeforerunner.skill -->"
MARKER_END = "<!-- forerunner:end -->"

CANONICAL_REL = Path("agent/codeforerunner.skill.md")
MARKETPLACE_REL = Path("plugins/codex/marketplace.json")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_BODY_MISMATCH = 3
EXIT_UNMANAGED_DEST = 4

# Per-task skill slugs (source: skills/<slug>/SKILL.md → plugins/codeforerunner/skills/<slug>/SKILL.md)
TASK_SKILL_SLUGS: tuple[str, ...] = (
    "codeforerunner",
    "forerunner-scan",
    "forerunner-readme",
    "forerunner-api-docs",
    "forerunner-audit",
    "forerunner-changelog",
    "forerunner-check",
    "forerunner-diagrams",
    "forerunner-flows",
    "forerunner-init",
    "forerunner-review",
    "forerunner-stack-docs",
    "forerunner-version-audit",
)


@dataclass(frozen=True)
class Target:
    """Resolved install destination: agent name + absolute path."""

    name: str
    path: Path


def _home() -> Path:
    return Path(os.path.expanduser("~"))


def resolve_target(agent: str, override: Path | None) -> Target:
    """Return the default install Target for the given agent, or use override path."""
    if agent == "generic":
        if override is None:
            raise ValueError("generic target requires --path PATH")
        return Target(agent, override.expanduser().resolve())
    if override is not None:
        return Target(agent, override.expanduser().resolve())
    home = _home()
    if agent == "codex":
        return Target(agent, home / ".codex/skills/codeforerunner/SKILL.md")
    if agent == "claude":
        return Target(agent, home / ".claude/plugins/codeforerunner/skills/codeforerunner/SKILL.md")
    if agent == "gemini":
        raise ValueError(
            "gemini install is handled via `gemini extensions install`; "
            "run `./install.sh --only gemini` instead"
        )
    raise ValueError(f"unknown agent '{agent}' (expected: codex, claude, generic)")


def resolve_skill_target(agent: str, slug: str) -> Target:
    """Return install target for a per-task skill slug."""
    home = _home()
    if agent == "codex":
        return Target(agent, home / f".codex/skills/{slug}/SKILL.md")
    if agent == "claude":
        return Target(agent, home / f".claude/plugins/codeforerunner/skills/{slug}/SKILL.md")
    raise ValueError(f"install_all not supported for agent '{agent}' (expected: codex, claude)")


def install_all_skills(
    *,
    agent: str,
    repo_root: Path,
    check_only: bool,
    out=None,
    err=None,
) -> int:
    """Install all per-task skills for the given agent. Returns 0 on full success."""
    out = out or sys.stdout
    err = err or sys.stderr
    any_error = False
    for slug in TASK_SKILL_SLUGS:
        src_path = repo_root / "plugins" / "codeforerunner" / "skills" / slug / "SKILL.md"
        if not src_path.is_file():
            print(f"warning: skill source not found: {src_path}", file=err)
            any_error = True
            continue
        try:
            target = resolve_skill_target(agent, slug)
        except ValueError as e:
            print(f"error: {e}", file=err)
            return EXIT_USAGE
        # For per-task skills use simple copy (no body-parity check against canonical)
        dest = target.path
        prefix = "would " if check_only else ""
        if dest.exists():
            src_trimmed = src_path.read_bytes().rstrip()
            dest_trimmed = dest.read_bytes().rstrip()
            if src_trimmed == dest_trimmed:
                print(f"skip: {dest} (up-to-date)", file=out)
                continue
            action = "update"
        else:
            action = "create"
        print(f"{prefix}{action}: {dest}", file=out)
        if not check_only:
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                dest.write_bytes(src_path.read_bytes())
            except OSError as e:
                print(f"error: failed to write {dest}: {e}", file=err)
                any_error = True
    return EXIT_OK if not any_error else EXIT_BODY_MISMATCH


def resolve_marketplace_target(agent: str, override: Path | None) -> Target:
    """Return the marketplace install Target for the given agent, or use override path."""
    if agent == "generic":
        if override is None:
            raise ValueError("generic marketplace target requires --path PATH")
        return Target(agent, override.expanduser().resolve())
    if override is not None:
        return Target(agent, override.expanduser().resolve())
    if agent == "codex":
        return Target(agent, _home() / ".codex/marketplaces/codeforerunner.json")
    raise ValueError(f"marketplace not supported for agent '{agent}' (expected: codex)")


def strip_frontmatter(text: str) -> str:
    """Body extraction matching scripts/validate_skill_copies.py."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                return "\n".join(lines[i + 1 :]).strip()
    return text.strip()


def extract_frontmatter(text: str) -> str:
    """Return frontmatter block (incl. fences) or '' if none."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                return "\n".join(lines[: i + 1]) + "\n"
    return ""


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hash_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def render(source_text: str, dest_existing: str | None, agent: str) -> str:
    """Render dest content: preserve dest frontmatter if present; wrap source body in markers."""
    body = strip_frontmatter(source_text)
    if dest_existing:
        fm = extract_frontmatter(dest_existing)
    else:
        fm = ""
    managed = f"{MARKER_BEGIN}\n{body}\n{MARKER_END}\n"
    if fm:
        return fm + managed
    return managed


def find_markers(text: str) -> tuple[int, int] | None:
    """Return (start, end) byte offsets of the managed region, or None if absent."""
    a = text.find(MARKER_BEGIN)
    if a < 0:
        return None
    b = text.find(MARKER_END, a + len(MARKER_BEGIN))
    if b < 0:
        return None
    return (a, b + len(MARKER_END))


def overlay(dest_text: str, source_body: str) -> str:
    """Replace managed region in-place. Caller has verified markers exist."""
    span = find_markers(dest_text)
    if span is None:
        raise RuntimeError("overlay: span is None — this is a bug")
    a, b = span
    managed = f"{MARKER_BEGIN}\n{source_body}\n{MARKER_END}"
    return dest_text[:a] + managed + dest_text[b:]


@dataclass
class Plan:
    """Pending install action computed by plan_install or plan_marketplace."""

    action: str  # "create" | "update" | "skip" | "abort"
    reason: str
    target: Target
    new_content: str | None = None

    def write(self) -> None:
        """Execute the plan: create or update the destination file."""
        if self.action in ("skip", "abort"):
            return
        assert self.new_content is not None
        self.target.path.parent.mkdir(parents=True, exist_ok=True)
        self.target.path.write_text(self.new_content, encoding="utf-8")


def plan_install(
    *,
    source_path: Path,
    canonical_path: Path,
    target: Target,
) -> tuple[Plan, int]:
    """Return (plan, exit_code). exit_code ≠ 0 → abort."""
    src_text = source_path.read_text(encoding="utf-8")
    canonical_text = canonical_path.read_text(encoding="utf-8")

    src_body = strip_frontmatter(src_text)
    canon_body = strip_frontmatter(canonical_text)
    if src_body != canon_body:
        return (
            Plan(
                action="abort",
                reason=(
                    f"body-parity violation (V10): source body differs from canonical "
                    f"{canonical_path}"
                ),
                target=target,
            ),
            EXIT_BODY_MISMATCH,
        )

    dest = target.path
    if dest.exists():
        dest_text = dest.read_text(encoding="utf-8")
        if find_markers(dest_text) is None:
            return (
                Plan(
                    action="abort",
                    reason=(
                        f"destination exists without managed markers ({dest}); refusing "
                        "to overwrite user content"
                    ),
                    target=target,
                ),
                EXIT_UNMANAGED_DEST,
            )
        new_text = overlay(dest_text, src_body)
        if _hash(new_text) == _hash(dest_text):
            return Plan(action="skip", reason="dest matches source (V12 idempotent)", target=target), EXIT_OK
        return Plan(action="update", reason="overlay managed region", target=target, new_content=new_text), EXIT_OK

    new_text = render(src_text, None, target.name)
    return Plan(action="create", reason="dest absent", target=target, new_content=new_text), EXIT_OK


def plan_marketplace(*, source_path: Path, target: Target) -> tuple[Plan, int]:
    """Idempotent JSON manifest install. Hash-equality on whole file (trimmed)."""
    src_bytes = source_path.read_bytes()
    src_trimmed = src_bytes.rstrip()
    src_text = src_bytes.decode("utf-8")
    dest = target.path
    if dest.exists():
        dest_bytes = dest.read_bytes()
        dest_trimmed = dest_bytes.rstrip()
        if _hash_bytes(src_trimmed) == _hash_bytes(dest_trimmed):
            return (
                Plan(action="skip", reason="dest matches source (V12 idempotent)", target=target),
                EXIT_OK,
            )
        return (
            Plan(
                action="abort",
                reason=(
                    f"destination exists and differs from source ({dest}); refusing "
                    "to overwrite user content"
                ),
                target=target,
            ),
            EXIT_UNMANAGED_DEST,
        )
    return (
        Plan(action="create", reason="dest absent", target=target, new_content=src_text),
        EXIT_OK,
    )


def install(
    *,
    agent: str,
    repo_root: Path,
    source: Path | None,
    dest_override: Path | None,
    check_only: bool,
    kind: Literal["skill", "marketplace"] = "skill",
    out=None,
    err=None,
) -> int:
    """Run one install operation (skill or marketplace). Returns an EXIT_* code."""
    out = out or sys.stdout
    err = err or sys.stderr

    if kind == "marketplace":
        try:
            target = resolve_marketplace_target(agent, dest_override)
        except ValueError as e:
            print(f"error: {e}", file=err)
            return EXIT_USAGE
        src_path = source if source is not None else (repo_root / MARKETPLACE_REL)
        if not src_path.is_file():
            print(f"error: marketplace source not found: {src_path}", file=err)
            return EXIT_USAGE
        plan, code = plan_marketplace(source_path=src_path, target=target)
        prefix = "would " if check_only else ""
        stream = err if code != EXIT_OK else out
        print(f"{prefix}{plan.action}: {target.path} ({plan.reason})", file=stream)
        if code != EXIT_OK:
            return code
        if not check_only:
            plan.write()
        return EXIT_OK

    try:
        target = resolve_target(agent, dest_override)
    except ValueError as e:
        print(f"error: {e}", file=err)
        return EXIT_USAGE

    canonical = repo_root / CANONICAL_REL
    src_path = source if source is not None else canonical
    if not src_path.is_file():
        print(f"error: source not found: {src_path}", file=err)
        return EXIT_USAGE
    if not canonical.is_file():
        print(f"error: canonical not found: {canonical}", file=err)
        return EXIT_USAGE

    plan, code = plan_install(source_path=src_path, canonical_path=canonical, target=target)
    prefix = "would " if check_only else ""
    stream = err if code != EXIT_OK else out
    print(f"{prefix}{plan.action}: {target.path} ({plan.reason})", file=stream)
    if code != EXIT_OK:
        return code
    if not check_only:
        plan.write()
    return EXIT_OK


def add_subparser(sub: argparse._SubParsersAction) -> None:
    """Register the `forerunner install` subcommand onto *sub*."""
    p = sub.add_parser("install", help="install skill(s) into agent-specific directories (D.installer)")
    p.add_argument("agent", choices=["codex", "claude", "generic"], nargs="?",
                   help="target agent (omit with --all to install to all detected agents)")
    p.add_argument("--all", action="store_true",
                   help="install all per-task skills for the specified agent")
    p.add_argument("--check", action="store_true", help="dry-run: print plan, write nothing")
    p.add_argument("--path", type=Path, help="dest path override (required for generic)")
    p.add_argument("--source", type=Path, help="source skill file (default: agent/codeforerunner.skill.md)")
    p.add_argument(
        "--marketplace",
        action="store_true",
        help="install a marketplace manifest (codex only) instead of the skill body",
    )
    p.set_defaults(func=_cli_entry)


def _cli_entry(args: argparse.Namespace) -> int:
    root = Path(args.repo).resolve() if args.repo else Path.cwd()

    if getattr(args, "all", False):
        agent = args.agent or "claude"
        return install_all_skills(
            agent=agent,
            repo_root=root,
            check_only=args.check,
        )

    if not args.agent:
        print("error: specify an agent or use --all", file=sys.stderr)
        return EXIT_USAGE

    return install(
        agent=args.agent,
        repo_root=root,
        source=args.source,
        dest_override=args.path,
        check_only=args.check,
        kind="marketplace" if getattr(args, "marketplace", False) else "skill",
    )
