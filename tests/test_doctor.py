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


def test_provider_api_key_finding_present_with_config(tmp_path: Path, monkeypatch):
    from unittest.mock import patch
    repo = _copy_repo_layout(tmp_path)
    (repo / "forerunner.config.yaml").write_text("", encoding="utf-8")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Force skill mode off so warn path is exercised
    with patch("codeforerunner.doctor._skill_mode_active", return_value=False):
        findings = run(repo)
    matches = [f for f in findings if f.check == "provider-api-key"]
    assert len(matches) == 1
    assert matches[0].severity == "warn"


def test_provider_api_key_ok_when_env_set(tmp_path: Path, monkeypatch):
    repo = _copy_repo_layout(tmp_path)
    (repo / "forerunner.config.yaml").write_text("", encoding="utf-8")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    findings = run(repo)
    matches = [f for f in findings if f.check == "provider-api-key"]
    assert len(matches) == 1
    assert matches[0].severity == "ok"


def test_provider_api_key_ollama_always_ok(tmp_path: Path, monkeypatch):
    repo = _copy_repo_layout(tmp_path)
    (repo / "forerunner.config.yaml").write_text(
        "provider: ollama\nmodel: llama3\n", encoding="utf-8"
    )
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    findings = run(repo)
    matches = [f for f in findings if f.check == "provider-api-key"]
    assert len(matches) == 1
    assert matches[0].severity == "ok"


def test_provider_api_key_uses_override(tmp_path: Path, monkeypatch):
    repo = _copy_repo_layout(tmp_path)
    (repo / "forerunner.config.yaml").write_text(
        "api_key_env:\n  anthropic: MY_KEY\n", encoding="utf-8"
    )
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("MY_KEY", "x")
    findings = run(repo)
    matches = [f for f in findings if f.check == "provider-api-key"]
    assert len(matches) == 1
    assert matches[0].severity == "ok"


def test_main_exits_one_when_error_present(tmp_path: Path, capsys):
    repo = _copy_repo_layout(tmp_path)
    drifted = repo / "skills/codeforerunner/SKILL.md"
    drifted.write_text(
        drifted.read_text(encoding="utf-8") + "\nDRIFT\n", encoding="utf-8"
    )
    rc = main(["--repo", str(repo)])
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


# ── local-mode surfacing ───────────────────────────────────────────────────────

def test_provider_api_key_local_mode_when_ollama_running_no_config(tmp_path: Path):
    from unittest.mock import patch
    repo = _copy_repo_layout(tmp_path)
    # no forerunner.config.yaml
    with patch("codeforerunner.providers.ollama.is_available", return_value=True):
        findings = run(repo)
    matches = [f for f in findings if f.check == "provider-api-key"]
    assert len(matches) == 1
    assert matches[0].severity == "ok"
    assert "local mode" in matches[0].message


def test_provider_api_key_hint_when_ollama_absent_no_config(tmp_path: Path):
    from unittest.mock import patch
    repo = _copy_repo_layout(tmp_path)
    # no forerunner.config.yaml; no skill installed → fallback message mentions prompt-only
    with patch("codeforerunner.providers.ollama.is_available", return_value=False), \
         patch("codeforerunner.doctor._skill_mode_active", return_value=False):
        findings = run(repo)
    matches = [f for f in findings if f.check == "provider-api-key"]
    assert len(matches) == 1
    assert matches[0].severity == "ok"
    assert "prompt-only" in matches[0].message


def test_provider_api_key_ollama_config_shows_local_mode(tmp_path: Path, monkeypatch):
    repo = _copy_repo_layout(tmp_path)
    (repo / "forerunner.config.yaml").write_text(
        "provider: ollama\nmodel: llama3\n", encoding="utf-8"
    )
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    findings = run(repo)
    matches = [f for f in findings if f.check == "provider-api-key"]
    assert len(matches) == 1
    assert matches[0].severity == "ok"
    assert "local mode" in matches[0].message
