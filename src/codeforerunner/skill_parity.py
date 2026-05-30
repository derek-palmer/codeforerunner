"""Skill Body Parity — single owner of the canonical-vs-copies body rule.

The codeforerunner skill body is authored once (the canonical skill) and
shipped as several distributed copies. V10 requires every copy's *body*
(frontmatter stripped) to equal the canonical body. That rule, and the
frontmatter parsing it depends on, previously lived in three places — the
installer, the doctor health check, and a standalone validation script. This
module is the single owner: the installer's install planning, the doctor
check, and ``scripts/validate_skill_copies.py`` all consult it.

Artifact paths come from the Distribution Inventory; nothing here executes
target-repo code — it only reads files — so callers can check parity without
the doctor's ``--run-scripts`` opt-in.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from codeforerunner import distribution as _dist


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split *text* into (frontmatter_block, body).

    ``frontmatter_block`` includes the ``---`` fences and a trailing newline,
    or ``""`` when there is no frontmatter. ``body`` is the remainder, trimmed.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                block = "\n".join(lines[: i + 1]) + "\n"
                body = "\n".join(lines[i + 1 :]).strip()
                return block, body
    return "", text.strip()


def body_of(text: str) -> str:
    """Return the body of *text* with any frontmatter removed and trimmed."""
    return split_frontmatter(text)[1]


@dataclass(frozen=True)
class ParityResult:
    """Outcome of a canonical-vs-copies body comparison under a repo root."""

    ok: bool
    missing_canonical: bool
    missing_copies: tuple[Path, ...]
    drifted_copies: tuple[Path, ...]
    checked: int


def check_skill_body_parity(repo_root: Path) -> ParityResult:
    """Compare every distributed skill copy's body to the canonical body.

    Reads the canonical skill and its distributed copies (paths from the
    Distribution Inventory) under ``repo_root`` and reports which copies are
    missing or have drifted bodies.
    """
    canonical_path = repo_root / _dist.CANONICAL_SKILL_REL
    if not canonical_path.is_file():
        return ParityResult(
            ok=False,
            missing_canonical=True,
            missing_copies=(),
            drifted_copies=(),
            checked=0,
        )

    canonical_body = body_of(canonical_path.read_text(encoding="utf-8"))

    missing: list[Path] = []
    drifted: list[Path] = []
    checked = 0
    for rel in _dist.DISTRIBUTED_SKILL_COPIES_REL:
        p = repo_root / rel
        if not p.is_file():
            missing.append(rel)
            continue
        checked += 1
        if body_of(p.read_text(encoding="utf-8")) != canonical_body:
            drifted.append(rel)

    ok = not missing and not drifted
    return ParityResult(
        ok=ok,
        missing_canonical=False,
        missing_copies=tuple(missing),
        drifted_copies=tuple(drifted),
        checked=checked,
    )
