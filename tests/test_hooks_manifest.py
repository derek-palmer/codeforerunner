from __future__ import annotations

from pathlib import Path

from codeforerunner.cli import main

REPO = Path(__file__).resolve().parents[1]
HOOKS = REPO / ".pre-commit-hooks.yaml"
CI = REPO / ".github/workflows/forerunner-check.yml"


def test_pre_commit_manifest_has_required_keys():
    text = HOOKS.read_text(encoding="utf-8")
    for key in ("id: forerunner-check", "entry: forerunner check", "language: system", "pass_filenames: false"):
        assert key in text, f"missing key: {key}"


def test_ci_workflow_present_and_gated():
    text = CI.read_text(encoding="utf-8")
    assert "name: forerunner check" in text
    assert "hashFiles('forerunner.config.yaml')" in text, "CI must skip when config absent (D.hooks)"
    assert "forerunner check" in text


def test_check_exit_zero_without_config(tmp_path):
    assert main(["--repo", str(tmp_path), "check"]) == 0


def test_check_exit_zero_with_config(tmp_path):
    (tmp_path / "forerunner.config.yaml").write_text("# empty\n", encoding="utf-8")
    assert main(["--repo", str(tmp_path), "check"]) == 0
