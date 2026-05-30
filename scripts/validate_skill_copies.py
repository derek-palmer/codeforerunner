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
from codeforerunner.skill_parity import check_skill_body_parity  # noqa: E402

CANONICAL = CANONICAL_SKILL_REL
COPIES = list(DISTRIBUTED_SKILL_COPIES_REL)


def print_checked_files(*, stream=sys.stdout) -> None:
    print(f"canonical: {CANONICAL}", file=stream)
    for path in COPIES:
        print(f"copy:      {path}", file=stream)


def main() -> int:
    result = check_skill_body_parity(ROOT)

    if not result.ok:
        print("V10 violation: distributed skill body drift detected.", file=sys.stderr)
        print_checked_files(stream=sys.stderr)
        if result.missing_canonical:
            print(f"missing:   {CANONICAL}", file=sys.stderr)
        for path in result.missing_copies:
            print(f"missing:   {path}", file=sys.stderr)
        for path in result.drifted_copies:
            print(f"mismatch:  {path}", file=sys.stderr)
        return 1

    print("V10 OK: skill copy bodies match.")
    print_checked_files()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
