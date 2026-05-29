"""Tests for scripts/check_versions.py shim-pin detection and bump-version.sh shim updates."""

from __future__ import annotations

import importlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
BUMP_SCRIPT = SCRIPTS / "bump-version.sh"


@pytest.fixture(autouse=True)
def _check_versions_module(monkeypatch):
    """Import check_versions without polluting sys.path permanently."""
    if "check_versions" not in sys.modules:
        spec = importlib.util.spec_from_file_location("check_versions", SCRIPTS / "check_versions.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules["check_versions"] = mod
    yield


def _cv():
    return sys.modules["check_versions"]


def test_read_install_sh_version_parses_pin(tmp_path, monkeypatch):
    (tmp_path / "install.sh").write_text('NPM_PKG="codeforerunner@1.2.3"\nREPO_TAG="v1.2.3"\n')
    cv = _cv()
    monkeypatch.setattr(cv, "ROOT", tmp_path)
    assert cv.read_install_sh_version() == "1.2.3"


def test_read_install_ps1_version_parses_pin(tmp_path, monkeypatch):
    (tmp_path / "install.ps1").write_text('$NpmPkg  = "codeforerunner@1.2.3"\n$RepoTag = "v1.2.3"\n')
    cv = _cv()
    monkeypatch.setattr(cv, "ROOT", tmp_path)
    assert cv.read_install_ps1_version() == "1.2.3"


def test_check_versions_passes_when_all_match():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_versions.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "All versions match." in result.stdout
    assert "install.sh NPM_PKG" in result.stdout
    assert "install.ps1 $NpmPkg" in result.stdout


def test_check_versions_fails_on_stale_shim_pin(tmp_path, monkeypatch):
    cv = _cv()
    root = cv.ROOT
    for f in ["pyproject.toml", "package.json", "install.ps1"]:
        shutil.copy(root / f, tmp_path / f)
    shutil.copytree(root / "plugins", tmp_path / "plugins")
    current_version = cv.read_install_sh_version()
    stale_sh = (root / "install.sh").read_text().replace(
        f"codeforerunner@{current_version}", "codeforerunner@0.0.1"
    )
    (tmp_path / "install.sh").write_text(stale_sh)
    monkeypatch.setattr(cv, "ROOT", tmp_path)
    assert cv.main() == 1


def _seed_bump_fixture(tmp_path: Path, version: str) -> None:
    """Populate tmp_path with a minimal repo structure at *version* for bump testing."""
    root = _cv().ROOT
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    shutil.copy(BUMP_SCRIPT, scripts_dir / "bump-version.sh")

    text = (root / "pyproject.toml").read_text()
    text = re.sub(r'^(version\s*=\s*")[^"]+(")', rf'\g<1>{version}\g<2>', text, flags=re.MULTILINE)
    (tmp_path / "pyproject.toml").write_text(text)

    pkg = json.loads((root / "package.json").read_text())
    pkg["version"] = version
    (tmp_path / "package.json").write_text(json.dumps(pkg, indent=2, ensure_ascii=False) + "\n")

    shutil.copytree(root / "plugins", tmp_path / "plugins")
    mp_path = tmp_path / "plugins" / "codex" / "marketplace.json"
    mp = json.loads(mp_path.read_text())
    mp["marketplace"]["version"] = version
    mp["plugins"][0]["version"] = version
    mp_path.write_text(json.dumps(mp, indent=2, ensure_ascii=False) + "\n")

    sh = (root / "install.sh").read_text()
    sh = re.sub(r'(NPM_PKG="codeforerunner@)[^"]+(")', rf'\g<1>{version}\g<2>', sh)
    sh = re.sub(r'(REPO_TAG="v)[^"]+(")', rf'\g<1>{version}\g<2>', sh)
    (tmp_path / "install.sh").write_text(sh)

    ps1 = (root / "install.ps1").read_text()
    ps1 = re.sub(r'(\$NpmPkg\s*=\s*"codeforerunner@)[^"]+(")', rf'\g<1>{version}\g<2>', ps1)
    ps1 = re.sub(r'(\$RepoTag\s*=\s*"v)[^"]+(")', rf'\g<1>{version}\g<2>', ps1)
    (tmp_path / "install.ps1").write_text(ps1)

    shutil.copy(root / "README.md", tmp_path / "README.md")


def test_bump_version_updates_shim_pins(tmp_path):
    """bump-version.sh must update install.sh and install.ps1 pin versions."""
    _seed_bump_fixture(tmp_path, "1.0.0")

    result = subprocess.run(
        ["bash", str(tmp_path / "scripts" / "bump-version.sh"), "1.1.0"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    sh_text = (tmp_path / "install.sh").read_text()
    ps1_text = (tmp_path / "install.ps1").read_text()
    assert "codeforerunner@1.1.0" in sh_text
    assert "v1.1.0" in sh_text
    assert "codeforerunner@1.1.0" in ps1_text
    assert "v1.1.0" in ps1_text
