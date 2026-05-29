"""Behavior tests for the Release Surface Manifest (release_surfaces.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codeforerunner import release_surfaces as rs

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_manifest_loads_with_valid_shape():
    surfaces = rs.all_surfaces()
    assert surfaces, "manifest must declare at least one surface"
    for s in surfaces:
        assert s.name, "surface needs a name"
        assert s.kind in rs.KINDS, f"{s.name}: bad kind {s.kind!r}"
        assert s.auth_mode in rs.AUTH_MODES, f"{s.name}: bad auth_mode {s.auth_mode!r}"
        assert isinstance(s.validations, tuple)
        vs = s.version_source
        assert isinstance(vs, dict) and "file" in vs and "kind" in vs
        assert vs["kind"] in rs.VERSION_SOURCE_KINDS, f"{s.name}: bad version_source kind"


def test_surface_names_are_unique():
    names = rs.names()
    assert len(names) == len(set(names)), f"duplicate surface names in {names!r}"


def test_known_release_surfaces_are_represented():
    expected = {
        "pypi",
        "npmjs",
        "github-packages",
        "docker",
        "codex-marketplace",
        "installer-shim-sh",
        "installer-shim-ps1",
    }
    assert expected <= set(rs.names()), f"missing surfaces: {expected - set(rs.names())}"


def test_get_raises_on_unknown_surface():
    with pytest.raises(KeyError):
        rs.get("does-not-exist")


def test_version_sources_resolve_and_agree_in_this_checkout():
    # Manifest-driven version-parity check: every version-bearing surface reads
    # a concrete version from this repo, and they all agree (no drift).
    versions = {
        s.name: rs.read_surface_version(s, REPO_ROOT)
        for s in rs.version_bearing_surfaces()
    }
    assert all(versions.values()), f"a surface resolved an empty version: {versions}"
    assert len(set(versions.values())) == 1, f"version drift across surfaces: {versions}"


def test_socket_badge_surface_is_registered_and_reads_readme_version():
    badge = rs.get("socket-badge")
    assert badge.kind == "badge"
    assert badge.version_source["file"] == "README.md"
    # Reads the version segment of the Socket badge URL straight from README,
    # so a stale badge pin diverging from the canonical version is caught by
    # the version-parity check above.
    assert rs.read_surface_version(badge, REPO_ROOT) == rs.read_surface_version(
        rs.get("pypi"), REPO_ROOT
    )


def test_read_surface_version_detects_drift(tmp_path):
    # Build a fake checkout where pyproject and package.json disagree; the
    # manifest-driven reader must surface two distinct values.
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "codeforerunner"\nversion = "0.4.5"\n', encoding="utf-8"
    )
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "codeforerunner", "version": "0.4.6"}), encoding="utf-8"
    )
    pypi = rs.get("pypi")
    npmjs = rs.get("npmjs")
    assert rs.read_surface_version(pypi, tmp_path) == "0.4.5"
    assert rs.read_surface_version(npmjs, tmp_path) == "0.4.6"
    assert rs.read_surface_version(pypi, tmp_path) != rs.read_surface_version(npmjs, tmp_path)
