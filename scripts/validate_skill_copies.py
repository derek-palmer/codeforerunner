#!/usr/bin/env python3
"""Validate V10 skill-copy body parity."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

# Source the canonical/copy paths from the Distribution Inventory so packaging
# changes are a single edit. Add src/ to the path for standalone runs (no
# installed package required).
sys.path.insert(0, str(ROOT / "src"))
from codeforerunner.distribution import (  # noqa: E402
    CANONICAL_SKILL_REL,
    DISTRIBUTED_SKILL_COPIES_REL,
)

CANONICAL = CANONICAL_SKILL_REL
COPIES = list(DISTRIBUTED_SKILL_COPIES_REL)


def strip_frontmatter(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[0] == "---":
        for index in range(1, len(lines)):
            if lines[index] == "---":
                return "\n".join(lines[index + 1 :]).strip()
    return text.strip()


def read_body(path: Path) -> str:
    return strip_frontmatter((ROOT / path).read_text(encoding="utf-8"))


def print_checked_files(*, stream=sys.stdout) -> None:
    print(f"canonical: {CANONICAL}", file=stream)
    for path in COPIES:
        print(f"copy:      {path}", file=stream)


def main() -> int:
    canonical_body = read_body(CANONICAL)
    failures: list[Path] = []

    for copy in COPIES:
        if read_body(copy) != canonical_body:
            failures.append(copy)

    if failures:
        print("V10 violation: distributed skill body drift detected.", file=sys.stderr)
        print_checked_files(stream=sys.stderr)
        for path in failures:
            print(f"mismatch:  {path}", file=sys.stderr)
        return 1

    print("V10 OK: skill copy bodies match.")
    print_checked_files()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
