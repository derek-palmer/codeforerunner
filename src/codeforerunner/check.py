"""Drift detection for docs that claim files don't exist when they do."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


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


def run(repo: Path) -> list[Violation]:
    """Scan repo docs for drift; return list of violations."""
    repo = Path(repo)
    active_rules = [
        (rid, rx, msg)
        for rid, rx, triggers, msg in _RULES
        if _trigger_exists(repo, triggers)
    ]
    if not active_rules:
        return []

    violations: list[Violation] = []
    for doc in _scanned_docs(repo):
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
