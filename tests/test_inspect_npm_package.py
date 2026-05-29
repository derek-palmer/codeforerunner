"""Behavior tests for scripts/inspect_npm_package.py.

The interface under test is the packed npm tarball: each test builds a tarball
shaped like ``npm pack`` output (every member under a ``package/`` prefix) and
asserts what the inspector reports about its contents.
"""

from __future__ import annotations

import importlib.util
import io
import json
import shutil
import sys
import tarfile
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "inspect_npm_package.py"


def _load_inspector():
    spec = importlib.util.spec_from_file_location("inspect_npm_package", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


inspect_npm_package = _load_inspector()


# --- fixture builder ------------------------------------------------------

_SKILLS_LOCK = {
    "version": 1,
    "skills": {
        "codeforerunner": {"skillPath": "skills/codeforerunner/SKILL.md"},
        "forerunner-scan": {"skillPath": "skills/forerunner-scan/SKILL.md"},
    },
}

_PACKAGE_JSON = {
    "name": "codeforerunner",
    "version": "0.4.5",
    "bin": {
        "codeforerunner": "bin/install.js",
        "codeforerunner-install": "bin/install.js",
    },
}


def _well_formed_members() -> dict[str, str]:
    """Member-path → text content for a complete, valid package."""
    return {
        "bin/install.js": "// installer\n",
        "package.json": json.dumps(_PACKAGE_JSON),
        "install.sh": "#!/bin/sh\n",
        "install.ps1": "# ps1\n",
        "skills-lock.json": json.dumps(_SKILLS_LOCK),
        "skills/codeforerunner/SKILL.md": "# codeforerunner\n",
        "skills/forerunner-scan/SKILL.md": "# scan\n",
    }


def _write_tarball(tmp_path: Path, members: dict[str, str]) -> Path:
    """Pack ``members`` into an npm-style tarball (``package/`` prefix)."""
    tarball = tmp_path / "codeforerunner-0.4.5.tgz"
    with tarfile.open(tarball, "w:gz") as tar:
        for name, content in members.items():
            raw = content.encode("utf-8")
            info = tarfile.TarInfo(name=f"package/{name}")
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
    return tarball


# --- tests ----------------------------------------------------------------


def test_well_formed_package_has_no_problems(tmp_path):
    tarball = _write_tarball(tmp_path, _well_formed_members())
    assert inspect_npm_package.inspect_package(tarball) == []


def test_missing_required_file_is_reported(tmp_path):
    members = _well_formed_members()
    del members["bin/install.js"]
    tarball = _write_tarball(tmp_path, members)
    problems = inspect_npm_package.inspect_package(tarball)
    assert any("bin/install.js" in p for p in problems)


def test_missing_bin_entrypoint_is_reported(tmp_path):
    members = _well_formed_members()
    pkg = dict(_PACKAGE_JSON)
    pkg["bin"] = {"codeforerunner": "bin/install.js"}  # drop codeforerunner-install
    members["package.json"] = json.dumps(pkg)
    tarball = _write_tarball(tmp_path, members)
    problems = inspect_npm_package.inspect_package(tarball)
    assert any("codeforerunner-install" in p for p in problems)


def test_skill_declared_in_lock_but_absent_is_reported(tmp_path):
    members = _well_formed_members()
    del members["skills/forerunner-scan/SKILL.md"]  # lock still declares it
    tarball = _write_tarball(tmp_path, members)
    problems = inspect_npm_package.inspect_package(tarball)
    assert any("forerunner-scan/SKILL.md" in p for p in problems)


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm not available")
def test_real_repo_npm_pack_passes_inspection():
    # End-to-end against actual `npm pack` output: the published artifact this
    # repo produces today must satisfy the inspector.
    tarball = inspect_npm_package._npm_pack()
    try:
        assert inspect_npm_package.inspect_package(tarball) == []
    finally:
        tarball.unlink(missing_ok=True)
