"""Drift detection for docs that claim files don't exist when they do."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

from codeforerunner.config import CheckConfig


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    rule_id: str
    message: str


_RULES = [
    (
        "R1-no-cli",
        re.compile(
            r"(?i)no\s+CLI\s+exists"
            r"|CLI\s+does\s+not\s+exist"
            r"|not\s+currently\s+present:[^.]*\bCLI\b"
            r"|Do\s+not\s+run\s+`forerunner`"
        ),
        ("src/codeforerunner/cli.py",),
        "doc claims no CLI exists, but src/codeforerunner/cli.py is present",
    ),
    (
        "R2-no-pre-commit",
        re.compile(r"(?i)no\s+pre[- ]commit(\s+hook)?"),
        (".pre-commit-hooks.yaml",),
        "doc claims no pre-commit hook, but .pre-commit-hooks.yaml is present",
    ),
    (
        "R3-no-ci",
        re.compile(r"(?i)no\s+CI(\s+workflow)?"),
        (".github/workflows/*.yml",),
        "doc claims no CI workflow, but .github/workflows/*.yml is present",
    ),
    (
        "R4-no-installer",
        re.compile(r"(?i)no\s+installer"),
        ("src/codeforerunner/installer.py",),
        "doc claims no installer, but src/codeforerunner/installer.py is present",
    ),
    (
        "R5-no-python-package",
        re.compile(r"(?i)no\s+Python\s+package"),
        ("pyproject.toml",),
        "doc claims no Python package, but pyproject.toml is present",
    ),
    (
        "R6-no-docker",
        re.compile(r"(?i)no\s+Docker(\s+image)?|no\s+Dockerfile"),
        ("Dockerfile", "compose.yml", "docker-compose.yml"),
        "doc claims no Docker, but Dockerfile/compose file is present",
    ),
    (
        "R6b-no-makefile",
        re.compile(r"(?i)no\s+Makefile"),
        ("Makefile",),
        "doc claims no Makefile, but Makefile is present",
    ),
    (
        "R7-no-mcp",
        re.compile(r"(?i)no\s+MCP(\s+server)?"),
        ("src/codeforerunner/mcp_server.py",),
        "doc claims no MCP server, but src/codeforerunner/mcp_server.py is present",
    ),
    (
        "R8-no-marketplace",
        re.compile(r"(?i)no\s+marketplace(\s+manifest)?"),
        ("plugins/codex/marketplace.json",),
        "doc claims no marketplace, but plugins/codex/marketplace.json is present",
    ),
]


def _trigger_exists(repo: Path, patterns: tuple[str, ...]) -> bool:
    for pat in patterns:
        if "*" in pat:
            parent = repo / Path(pat).parent
            name = Path(pat).name
            if parent.is_dir() and any(parent.glob(name)):
                return True
        else:
            if (repo / pat).exists():
                return True
    return False


def _scanned_docs(repo: Path) -> list[Path]:
    docs: list[Path] = []
    readme = repo / "README.md"
    if readme.is_file():
        docs.append(readme)
    docs_dir = repo / "docs"
    if docs_dir.is_dir():
        docs.extend(sorted(p for p in docs_dir.rglob("*.md") if p.is_file()))
    return docs


def _path_ignored(repo: Path, doc: Path, ignore_patterns: tuple[str, ...]) -> bool:
    if not ignore_patterns:
        return False
    try:
        rel = doc.relative_to(repo).as_posix()
    except ValueError:
        rel = doc.as_posix()
    return any(fnmatch.fnmatch(rel, pat) for pat in ignore_patterns)


def run(repo: Path, config: CheckConfig | None = None) -> list[Violation]:
    """Scan repo docs for drift; return list of violations.

    `config` filters rules via `enabled_rules` and skips docs matching `ignore_paths`.
    `None` config (default) preserves the pre-T25 behavior: all rules, no ignores.
    """
    repo = Path(repo)
    enabled = set(config.enabled_rules) if (config and config.enabled_rules is not None) else None
    ignore_patterns = config.ignore_paths if config else ()

    active_rules = [
        (rid, rx, msg)
        for rid, rx, triggers, msg in _RULES
        if _trigger_exists(repo, triggers) and (enabled is None or rid in enabled)
    ]
    if not active_rules:
        return []

    violations: list[Violation] = []
    for doc in _scanned_docs(repo):
        if _path_ignored(repo, doc, ignore_patterns):
            continue
        try:
            text = doc.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rid, rx, msg in active_rules:
                if rx.search(line):
                    violations.append(
                        Violation(path=doc, line=lineno, rule_id=rid, message=msg)
                    )
    return violations


def format_violations(vs: list[Violation]) -> str:
    """Format violations one per line for stderr."""
    return "\n".join(
        f"{v.path}:{v.line}: {v.rule_id}: {v.message}" for v in vs
    )
