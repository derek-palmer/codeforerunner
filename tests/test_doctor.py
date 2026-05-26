"""Tests for `forerunner doctor`. See SPEC.md §T35."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from codeforerunner.doctor import Finding, format_report, main, run, starter_config

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

    findings = run(repo, run_scripts=True)
    parity_errors = [
        f for f in findings if f.check == "skill-body-parity" and f.severity == "error"
    ]
    assert len(parity_errors) >= 1


def test_marketplace_invalid_reported(tmp_path: Path):
    repo = _copy_repo_layout(tmp_path)
    bad = repo / "plugins/codex/marketplace.json"
    bad.write_text(json.dumps({"marketplace": {"id": "x", "name": "x", "version": "1.0.0"}}), encoding="utf-8")

    findings = run(repo, run_scripts=True)
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
    rc = main(["--repo", str(repo), "--run-scripts"])
    capsys.readouterr()
    assert rc == 1


# ── starter_config / --fix ─────────────────────────────────────────────────


def test_starter_config_contains_expected_rules():
    cfg = starter_config()
    assert "R1-no-cli" in cfg
    assert "R7-no-mcp" in cfg
    assert "R8-no-marketplace" in cfg
    assert "ignore_paths" in cfg


def test_doctor_fix_writes_config_when_absent(tmp_path: Path, capsys):
    from codeforerunner.cli import main as cli_main

    repo = _copy_repo_layout(tmp_path)
    cfg_path = repo / "forerunner.config.yaml"
    assert not cfg_path.exists()

    cli_main(["--repo", str(repo), "doctor", "--fix"])
    capsys.readouterr()

    assert cfg_path.is_file()
    content = cfg_path.read_text(encoding="utf-8")
    assert "R1-no-cli" in content


def test_doctor_fix_does_not_overwrite_existing_config(tmp_path: Path, capsys):
    from codeforerunner.cli import main as cli_main

    repo = _copy_repo_layout(tmp_path)
    cfg_path = repo / "forerunner.config.yaml"
    cfg_path.write_text("# my custom config\n", encoding="utf-8")

    cli_main(["--repo", str(repo), "doctor", "--fix"])
    capsys.readouterr()

    assert cfg_path.read_text(encoding="utf-8") == "# my custom config\n"


# ── skill-body-parity edge cases ──────────────────────────────────────────────

def test_skill_body_parity_canonical_missing(tmp_path: Path):
    from codeforerunner.doctor import _check_skill_body_parity
    repo = _copy_repo_layout(tmp_path)
    (repo / "agent" / "codeforerunner.skill.md").unlink()

    findings = _check_skill_body_parity(repo, run_scripts=True)
    assert any(f.severity == "error" and "canonical skill missing" in f.message for f in findings)


def test_skill_body_parity_copy_missing(tmp_path: Path):
    from codeforerunner.doctor import _check_skill_body_parity
    repo = _copy_repo_layout(tmp_path)
    (repo / "skills" / "codeforerunner" / "SKILL.md").unlink()

    findings = _check_skill_body_parity(repo, run_scripts=True)
    assert any(f.severity == "error" and "copy missing" in f.message for f in findings)


# ── _check_installed_destinations edge cases ──────────────────────────────────

def test_installed_destinations_oserror(tmp_path: Path):
    import pathlib
    from unittest.mock import patch
    from codeforerunner.doctor import _check_installed_destinations

    skill_dest = tmp_path / "SKILL.md"
    skill_dest.write_text("content", encoding="utf-8")
    mp_dest = tmp_path / "nomp.json"

    original_read_text = pathlib.Path.read_text

    def _selective_raise(self, *args, **kwargs):
        if self == skill_dest:
            raise OSError("denied")
        return original_read_text(self, *args, **kwargs)

    with patch("codeforerunner.doctor._installed_skill_destinations", return_value=[skill_dest]), \
         patch("codeforerunner.doctor._installed_marketplace_destination", return_value=mp_dest), \
         patch.object(pathlib.Path, "read_text", _selective_raise):
        findings = _check_installed_destinations(tmp_path)

    assert any("unreadable" in f.message for f in findings)


def test_installed_destinations_with_markers_ok(tmp_path: Path):
    from unittest.mock import patch
    from codeforerunner.doctor import MARKER_BEGIN, MARKER_END, _check_installed_destinations

    skill_dest = tmp_path / "SKILL.md"
    skill_dest.write_text(f"{MARKER_BEGIN}\nbody\n{MARKER_END}\n", encoding="utf-8")
    mp_dest = tmp_path / "nomp.json"

    with patch("codeforerunner.doctor._installed_skill_destinations", return_value=[skill_dest]), \
         patch("codeforerunner.doctor._installed_marketplace_destination", return_value=mp_dest):
        findings = _check_installed_destinations(tmp_path)

    assert any(f.severity == "ok" and "managed" in f.message for f in findings)


def test_installed_destinations_without_markers(tmp_path: Path):
    from unittest.mock import patch
    from codeforerunner.doctor import _check_installed_destinations

    skill_dest = tmp_path / "SKILL.md"
    skill_dest.write_text("# user file, no markers", encoding="utf-8")
    mp_dest = tmp_path / "nomp.json"

    with patch("codeforerunner.doctor._installed_skill_destinations", return_value=[skill_dest]), \
         patch("codeforerunner.doctor._installed_marketplace_destination", return_value=mp_dest):
        findings = _check_installed_destinations(tmp_path)

    assert any("without managed-region markers" in f.message for f in findings)


def test_installed_destinations_marketplace_matches(tmp_path: Path):
    from unittest.mock import patch
    from codeforerunner.doctor import _check_installed_destinations

    skill_dest = tmp_path / "SKILL.md"
    skill_dest.write_text("# no markers")

    mp_content = '{"marketplace": {"id": "test"}}'
    mp_src = tmp_path / "plugins" / "codex" / "marketplace.json"
    mp_src.parent.mkdir(parents=True)
    mp_src.write_text(mp_content, encoding="utf-8")

    mp_dest = tmp_path / "mp.json"
    mp_dest.write_text(mp_content, encoding="utf-8")

    with patch("codeforerunner.doctor._installed_skill_destinations", return_value=[skill_dest]), \
         patch("codeforerunner.doctor._installed_marketplace_destination", return_value=mp_dest):
        findings = _check_installed_destinations(tmp_path)

    assert any(f.severity == "ok" and "matches" in f.message for f in findings)


def test_installed_destinations_marketplace_drifted(tmp_path: Path):
    from unittest.mock import patch
    from codeforerunner.doctor import _check_installed_destinations

    skill_dest = tmp_path / "SKILL.md"
    skill_dest.write_text("# no markers")

    mp_src = tmp_path / "plugins" / "codex" / "marketplace.json"
    mp_src.parent.mkdir(parents=True)
    mp_src.write_text('{"id": "canonical"}', encoding="utf-8")

    mp_dest = tmp_path / "mp.json"
    mp_dest.write_text('{"id": "old"}', encoding="utf-8")

    with patch("codeforerunner.doctor._installed_skill_destinations", return_value=[skill_dest]), \
         patch("codeforerunner.doctor._installed_marketplace_destination", return_value=mp_dest):
        findings = _check_installed_destinations(tmp_path)

    assert any("drifted" in f.message for f in findings)


def test_installed_destinations_marketplace_oserror(tmp_path: Path):
    import pathlib
    from unittest.mock import patch
    from codeforerunner.doctor import _check_installed_destinations

    skill_dest = tmp_path / "SKILL.md"
    skill_dest.write_text("# no markers")

    mp_dest = tmp_path / "mp.json"
    mp_dest.write_text("{}", encoding="utf-8")

    original_read_text = pathlib.Path.read_text

    def _raise_for_mp(self, *args, **kwargs):
        if self == mp_dest:
            raise OSError("denied")
        return original_read_text(self, *args, **kwargs)

    with patch("codeforerunner.doctor._installed_skill_destinations", return_value=[skill_dest]), \
         patch("codeforerunner.doctor._installed_marketplace_destination", return_value=mp_dest), \
         patch.object(pathlib.Path, "read_text", _raise_for_mp):
        findings = _check_installed_destinations(tmp_path)

    assert any("unreadable" in f.message for f in findings)


# ── _check_config_loadable error path ─────────────────────────────────────────

def test_check_config_loadable_reports_error_on_invalid_config(tmp_path: Path):
    from codeforerunner.doctor import _check_config_loadable
    (tmp_path / "forerunner.config.yaml").write_text(
        "approaching_eol_threshold_months: not-a-number\n", encoding="utf-8"
    )
    findings = _check_config_loadable(tmp_path)
    assert any(f.severity == "error" for f in findings)
