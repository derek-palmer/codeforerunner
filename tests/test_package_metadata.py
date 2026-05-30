"""Guard the npm package.json metadata that feeds the Socket.dev profile.

The license is declared machine-readably via its SPDX `LicenseRef` id (the
project is source-available by design — see
docs/adr/0002-source-available-license-over-socket-score.md), and authorship
is present and consistent with pyproject.toml.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _package_json() -> dict:
    return json.loads((REPO / "package.json").read_text(encoding="utf-8"))


def test_license_is_declared_spdx_licenseref():
    assert _package_json()["license"] == "LicenseRef-Codeforerunner-SAL-0.1"


def test_license_file_for_the_ref_exists():
    assert (REPO / "LICENSES" / "LicenseRef-Codeforerunner-SAL-0.1.txt").is_file()


def test_author_present_and_matches_pyproject():
    author = _package_json().get("author")
    assert author, "package.json must declare an author"
    pyproject = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    py_authors = [a["name"] for a in pyproject["project"]["authors"]]
    assert author in py_authors, f"{author!r} not in pyproject authors {py_authors!r}"
