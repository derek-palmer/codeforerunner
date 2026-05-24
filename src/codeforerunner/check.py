"""Drift detection for docs vs repo state."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

from codeforerunner.config import CheckConfig


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    rule_id: str
    message: str


@dataclass(frozen=True)
class _Rule:
    id: str
    pattern: re.Pattern
    triggers: tuple[str, ...]
    message: str
    invert: bool = False  # True = fire when triggers ABSENT (doc claims feature exists but file gone)


_RULES: list[_Rule] = [
    # Normal rules: fire when trigger EXISTS and phrase matches (doc denies a thing that's present)
    _Rule(
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
    _Rule(
        "R2-no-pre-commit",
        re.compile(r"(?i)no\s+pre[- ]commit(\s+hook)?"),
        (".pre-commit-hooks.yaml",),
        "doc claims no pre-commit hook, but .pre-commit-hooks.yaml is present",
    ),
    _Rule(
        "R3-no-ci",
        re.compile(r"(?i)no\s+CI(\s+workflow)?"),
        (".github/workflows/*.yml",),
        "doc claims no CI workflow, but .github/workflows/*.yml is present",
    ),
    _Rule(
        "R4-no-installer",
        re.compile(r"(?i)no\s+installer"),
        ("src/codeforerunner/installer.py",),
        "doc claims no installer, but src/codeforerunner/installer.py is present",
    ),
    _Rule(
        "R5-no-python-package",
        re.compile(r"(?i)no\s+Python\s+package"),
        ("pyproject.toml",),
        "doc claims no Python package, but pyproject.toml is present",
    ),
    _Rule(
        "R6-no-docker",
        re.compile(r"(?i)no\s+Docker(\s+image)?|no\s+Dockerfile"),
        ("Dockerfile", "compose.yml", "docker-compose.yml"),
        "doc claims no Docker, but Dockerfile/compose file is present",
    ),
    _Rule(
        "R6b-no-makefile",
        re.compile(r"(?i)no\s+Makefile"),
        ("Makefile",),
        "doc claims no Makefile, but Makefile is present",
    ),
    _Rule(
        "R7-no-mcp",
        re.compile(r"(?i)no\s+MCP(\s+server)?"),
        ("src/codeforerunner/mcp_server.py",),
        "doc claims no MCP server, but src/codeforerunner/mcp_server.py is present",
    ),
    _Rule(
        "R8-no-marketplace",
        re.compile(r"(?i)no\s+marketplace(\s+manifest)?"),
        ("plugins/codex/marketplace.json",),
        "doc claims no marketplace, but plugins/codex/marketplace.json is present",
    ),
    # Inverse rules: fire when trigger ABSENT and phrase matches (doc claims thing exists but file gone)
    _Rule(
        "RI1-missing-cli",
        re.compile(
            r"(?i)\bforerunner\s+(?:init|scan|doc|check|generate|doctor)\b"
        ),
        ("src/codeforerunner/cli.py",),
        "doc references forerunner CLI commands, but src/codeforerunner/cli.py is absent",
        invert=True,
    ),
    _Rule(
        "RI5-missing-python-package",
        re.compile(r"(?i)\bpipx?\s+install\s+codeforerunner\b"),
        ("pyproject.toml",),
        "doc claims package is installable via pip/pipx, but pyproject.toml is absent",
        invert=True,
    ),
    _Rule(
        "RI7-missing-mcp",
        re.compile(r"(?i)\bforerunner\s+mcp-server\b"),
        ("src/codeforerunner/mcp_server.py",),
        "doc references forerunner mcp-server, but src/codeforerunner/mcp_server.py is absent",
        invert=True,
    ),
]

_VERSION_PIN_RE = re.compile(
    r"(?:codeforerunner==|codeforerunner@v)"
    r"(\d+\.\d+\.\d+)"
)
_PYPROJECT_VERSION_RE = re.compile(r'^version\s*=\s*"(\d+\.\d+\.\d+)"', re.MULTILINE)
_CHANGELOG_FILENAME = "CHANGELOG.md"


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


def _current_version(repo: Path) -> str | None:
    pyproject = repo / "pyproject.toml"
    if not pyproject.is_file():
        return None
    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _PYPROJECT_VERSION_RE.search(text)
    return m.group(1) if m else None


def _check_version_drift(
    repo: Path,
    docs: list[Path],
    ignore_patterns: tuple[str, ...],
    enabled: set[str] | None,
) -> list[Violation]:
    if enabled is not None and "RV1-version-drift" not in enabled:
        return []
    current = _current_version(repo)
    if current is None:
        return []
    violations: list[Violation] = []
    for doc in docs:
        if doc.name == _CHANGELOG_FILENAME:
            continue
        if _path_ignored(repo, doc, ignore_patterns):
            continue
        try:
            text = doc.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in _VERSION_PIN_RE.finditer(line):
                pinned = m.group(1)
                if pinned != current:
                    violations.append(
                        Violation(
                            path=doc,
                            line=lineno,
                            rule_id="RV1-version-drift",
                            message=f"version pin {pinned!r} does not match current {current!r}",
                        )
                    )
    return violations


def run(repo: Path, config: CheckConfig | None = None) -> list[Violation]:
    """Scan repo docs for drift; return list of violations.

    `config` filters rules via `enabled_rules` and skips docs matching `ignore_paths`.
    `None` config (default) preserves the pre-T25 behavior: all rules, no ignores.
    """
    repo = Path(repo)
    enabled = set(config.enabled_rules) if (config and config.enabled_rules is not None) else None
    ignore_patterns = config.ignore_paths if config else ()

    docs = _scanned_docs(repo)

    active_rules: list[_Rule] = []
    for rule in _RULES:
        if enabled is not None and rule.id not in enabled:
            continue
        trigger_found = _trigger_exists(repo, rule.triggers)
        if (not rule.invert and trigger_found) or (rule.invert and not trigger_found):
            active_rules.append(rule)

    violations: list[Violation] = []
    for doc in docs:
        if _path_ignored(repo, doc, ignore_patterns):
            continue
        try:
            text = doc.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rule in active_rules:
                if rule.pattern.search(line):
                    violations.append(
                        Violation(path=doc, line=lineno, rule_id=rule.id, message=rule.message)
                    )

    violations.extend(_check_version_drift(repo, docs, ignore_patterns, enabled))
    return violations


def format_violations(vs: list[Violation]) -> str:
    """Format violations one per line for stderr."""
    return "\n".join(
        f"{v.path}:{v.line}: {v.rule_id}: {v.message}" for v in vs
    )
