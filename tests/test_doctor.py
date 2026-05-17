"""Tests for `forerunner doctor`. See SPEC.md §T35."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from codeforerunner.doctor import Finding, format_report, main, run

REPO = Path(__file__).resolve().parent.parent


def _copy_repo_layout(tmp_path: Path) -> Path:
    """Copy the minimal repo layout needed by `run()` to tmp_path."""
    dst = tmp_path / "repo"
    dst.mkdir()
    for rel in (
        "agent/codeforerunner.skill.md",
        "plugins/codeforerunner/skills/codeforerunner/SKILL.md",
        "skills/codeforerunner/SKILL.md",
        "plugins/codex/marketplace.json",
        "scripts/validate_skill_copies.py",
        "scripts/validate_codex_marketplace.py",
    ):
        src = REPO / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    return dst


def test_real_repo_is_healthy():
    findings = run(REPO)
    assert len(findings) >= 4
    severities = {f.severity for f in findings}
    assert "error" not in severities
    assert severities.issubset({"ok", "warn"})


def test_skill_body_drift_reported(tmp_path: Path):
    repo = _copy_repo_layout(tmp_path)
    drifted = repo / "plugins/codeforerunner/skills/codeforerunner/SKILL.md"
    text = drifted.read_text(encoding="utf-8")
    drifted.write_text(text + "\n\nINJECTED DRIFT LINE\n", encoding="utf-8")

    findings = run(repo)
    parity_errors = [
        f for f in findings if f.check == "skill-body-parity" and f.severity == "error"
    ]
    assert len(parity_errors) >= 1


def test_marketplace_invalid_reported(tmp_path: Path):
    repo = _copy_repo_layout(tmp_path)
    bad = repo / "plugins/codex/marketplace.json"
    bad.write_text(json.dumps({"marketplace": {"id": "x", "name": "x", "version": "1.0.0"}}), encoding="utf-8")

    findings = run(repo)
    mp_errors = [
        f for f in findings if f.check == "codex-marketplace" and f.severity == "error"
    ]
    assert len(mp_errors) >= 1


def test_format_report_renders_severity_prefixes():
    out = format_report(
        [Finding("ok", "x", "msg"), Finding("error", "y", "boom")]
    )
    lines = out.splitlines()
    assert any(line.startswith("[ok]") for line in lines)
    assert any(line.startswith("[error]") for line in lines)


def test_main_exits_zero_when_no_errors(capsys):
    rc = main(["--repo", str(REPO)])
    capsys.readouterr()
    assert rc == 0


def test_main_exits_one_when_error_present(tmp_path: Path, capsys):
    repo = _copy_repo_layout(tmp_path)
    drifted = repo / "skills/codeforerunner/SKILL.md"
    drifted.write_text(
        drifted.read_text(encoding="utf-8") + "\nDRIFT\n", encoding="utf-8"
    )
    rc = main(["--repo", str(repo)])
    capsys.readouterr()
    assert rc == 1
