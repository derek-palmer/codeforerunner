#!/usr/bin/env python3
"""Inspect a packed npm tarball and verify it ships the contents users need.

The packed tarball (``npm pack`` output) is the interface under test: this
checks what gets published, independent of any registry. Run with no argument
to pack the repo and inspect it, or pass a ``.tgz`` to inspect directly.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tarfile
from pathlib import Path

# Files every consumer of the npm artifact relies on.
REQUIRED_FILES = (
    "bin/install.js",
    "package.json",
    "install.sh",
    "install.ps1",
    "skills-lock.json",
)
# Console-script entrypoints package.json must expose.
REQUIRED_BINS = ("codeforerunner", "codeforerunner-install")


def _strip_prefix(name: str) -> str:
    """Drop the leading ``package/`` dir npm wraps every member in."""
    parts = name.split("/", 1)
    return parts[1] if len(parts) == 2 and parts[0] == "package" else name


def _read_members(tar: tarfile.TarFile) -> set[str]:
    return {_strip_prefix(m.name) for m in tar.getmembers() if m.isfile()}


def _read_text(tar: tarfile.TarFile, member: str) -> str | None:
    for m in tar.getmembers():
        if _strip_prefix(m.name) == member and m.isfile():
            f = tar.extractfile(m)
            if f is not None:
                return f.read().decode("utf-8")
    return None


def inspect_package(tarball_path: Path) -> list[str]:
    """Return a list of content problems; empty means the artifact is good."""
    problems: list[str] = []
    with tarfile.open(tarball_path, "r:*") as tar:
        members = _read_members(tar)

        for required in REQUIRED_FILES:
            if required not in members:
                problems.append(f"missing required file: {required}")

        if not any(m.startswith("skills/") for m in members):
            problems.append("missing skill payloads: skills/ is empty")

        problems.extend(_check_bins(tar, members))
        problems.extend(_check_locked_skills(tar, members))

    return problems


def _check_locked_skills(tar: tarfile.TarFile, members: set[str]) -> list[str]:
    """Every skill the lock declares must actually ship in the tarball."""
    if "skills-lock.json" not in members:
        return []  # already reported as a missing required file
    raw = _read_text(tar, "skills-lock.json")
    try:
        skills = json.loads(raw or "").get("skills", {})
    except json.JSONDecodeError:
        return ["skills-lock.json is not valid JSON"]
    problems = []
    for entry in skills.values():
        path = entry.get("skillPath")
        if path and path not in members:
            problems.append(f"skill declared in skills-lock.json but absent from package: {path}")
    return problems


def _check_bins(tar: tarfile.TarFile, members: set[str]) -> list[str]:
    if "package.json" not in members:
        return []  # already reported as a missing required file
    raw = _read_text(tar, "package.json")
    try:
        bins = json.loads(raw or "").get("bin", {})
    except json.JSONDecodeError:
        return ["package.json is not valid JSON"]
    return [
        f"missing bin entrypoint in package.json: {name}"
        for name in REQUIRED_BINS
        if name not in bins
    ]


def main(argv: list[str]) -> int:
    if argv:
        tarball = Path(argv[0])
        created = False
    else:
        tarball = _npm_pack()
        created = True
    try:
        problems = inspect_package(tarball)
    finally:
        if created:
            tarball.unlink(missing_ok=True)

    if problems:
        print("npm package contents FAILED validation:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"npm package contents OK ({tarball.name})")
    return 0


def _npm_pack() -> Path:
    root = Path(__file__).resolve().parent.parent
    out = subprocess.run(
        ["npm", "pack", "--json"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    filename = json.loads(out.stdout)[0]["filename"]
    return root / filename


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
