"""Tests for scripts/validate_codex_marketplace.py."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO / "scripts" / "validate_codex_marketplace.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_codex_marketplace", SCRIPT_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator()
validate = validator.validate


VALID_MANIFEST = {
    "marketplace": {
        "id": "codeforerunner",
        "name": "codeforerunner",
        "description": "Test marketplace.",
        "version": "0.2.0",
    },
    "plugins": [
        {
            "id": "codeforerunner",
            "name": "codeforerunner",
            "version": "0.2.0",
            "description": "Test plugin.",
            "source": {
                "kind": "git",
                "url": "https://example.com/repo",
                "path": "plugins/codeforerunner",
            },
            "entry": "plugins/codeforerunner/skills/codeforerunner/SKILL.md",
        }
    ],
}


def _write_manifest(tmp_path: Path, data: dict, *, write_entry: bool = True) -> Path:
    manifest_dir = tmp_path / "plugins" / "codex"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "marketplace.json"
    manifest_path.write_text(json.dumps(data), encoding="utf-8")

    if write_entry:
        for plugin in data.get("plugins", []):
            entry = plugin.get("entry")
            if isinstance(entry, str) and entry:
                entry_path = tmp_path / entry
                entry_path.parent.mkdir(parents=True, exist_ok=True)
                if not entry_path.exists():
                    entry_path.write_text("stub", encoding="utf-8")
    return manifest_path


def test_real_manifest_is_valid():
    assert validate(REPO) == []


def test_missing_file_errors(tmp_path):
    errors = validate(tmp_path)
    assert len(errors) >= 1
    assert any("not found" in e for e in errors)


def test_bad_semver_errors(tmp_path):
    data = copy.deepcopy(VALID_MANIFEST)
    data["marketplace"]["version"] = "0.2"
    _write_manifest(tmp_path, data)
    errors = validate(tmp_path)
    assert any("semver" in e for e in errors)


def test_missing_entry_path_errors(tmp_path):
    data = copy.deepcopy(VALID_MANIFEST)
    data["plugins"][0]["entry"] = "does/not/exist/SKILL.md"
    _write_manifest(tmp_path, data, write_entry=False)
    errors = validate(tmp_path)
    assert any("entry" in e for e in errors)


def test_empty_plugins_list_errors(tmp_path):
    data = copy.deepcopy(VALID_MANIFEST)
    data["plugins"] = []
    _write_manifest(tmp_path, data)
    errors = validate(tmp_path)
    assert len(errors) >= 1
    assert any("plugins" in e for e in errors)
