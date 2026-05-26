from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import codeforerunner
import pytest

from codeforerunner.cli import main

REPO = Path(__file__).resolve().parents[1]
# Prompts are bundled inside the package; use the installed path.
PROMPTS = Path(codeforerunner.__file__).parent / "prompts"


def test_help_exit_zero():
    proc = subprocess.run(
        [sys.executable, "-m", "codeforerunner.cli", "--help"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "forerunner" in proc.stdout


def test_doc_scan_emits_task_body(capsys):
    rc = main(["doc", "scan"])
    out = capsys.readouterr().out
    assert rc == 0
    scan_body = (PROMPTS / "tasks" / "scan.md").read_text(encoding="utf-8")
    first_line = scan_body.splitlines()[0]
    assert first_line in out
    assert "<!-- task: scan.md -->" in out


def test_doc_unknown_task_exits_nonzero(capsys):
    rc = main(["doc", "definitely-not-a-task"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "unknown task" in err


@pytest.mark.parametrize(
    "cmd,task_file",
    [("init", "init-agent-onboarding.md"), ("scan", "scan.md")],
)
def test_init_scan_resolve_bundle(cmd, task_file, capsys):
    rc = main([cmd])
    out = capsys.readouterr().out
    assert rc == 0
    assert f"<!-- task: {task_file} -->" in out
    body = (PROMPTS / "tasks" / task_file).read_text(encoding="utf-8")
    assert body.splitlines()[0] in out


def test_init_agents_only_matches_default(capsys):
    rc = main(["init", "--agents-only"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "<!-- task: init-agent-onboarding.md -->" in out
    assert "<!-- task: scan.md -->" not in out


def test_init_full_prepends_scan(capsys):
    rc = main(["init", "--full"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "section 1/2 (scan)" in out
    assert "<!-- task: scan.md -->" in out
    assert "section 2/2 (onboarding)" in out
    assert "<!-- task: init-agent-onboarding.md -->" in out
    assert out.index("<!-- task: scan.md -->") < out.index(
        "<!-- task: init-agent-onboarding.md -->"
    )


def test_init_full_and_agents_only_mutually_exclusive(capsys):
    with pytest.raises(SystemExit):
        main(["init", "--full", "--agents-only"])


def _seed_repo_with_config(tmp_path):
    (tmp_path / "prompts/system").mkdir(parents=True)
    (tmp_path / "prompts/system/base.md").write_text("# base\n", encoding="utf-8")
    (tmp_path / "prompts/partials").mkdir()
    (tmp_path / "prompts/tasks").mkdir()
    (tmp_path / "prompts/tasks/readme.md").write_text("# readme task\n", encoding="utf-8")
    (tmp_path / "prompts/tasks/scan.md").write_text("# scan task\n", encoding="utf-8")
    (tmp_path / "prompts/tasks/init-agent-onboarding.md").write_text(
        "# onboarding\n", encoding="utf-8"
    )
    (tmp_path / "forerunner.config.yaml").write_text("", encoding="utf-8")


def test_doc_non_exempt_with_config_warns_without_env(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    monkeypatch.delenv("FORERUNNER_SCAN_DONE", raising=False)
    rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" in cap.err
    assert "FORERUNNER_SCAN_DONE" in cap.err


def test_doc_non_exempt_with_env_set_no_warning(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    monkeypatch.setenv("FORERUNNER_SCAN_DONE", "1")
    rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" not in cap.err


def test_doc_exempt_task_no_warning(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    monkeypatch.delenv("FORERUNNER_SCAN_DONE", raising=False)
    rc = main(["--repo", str(tmp_path), "doc", "scan"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" not in cap.err


def test_doc_without_config_no_warning(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    (tmp_path / "forerunner.config.yaml").unlink()
    monkeypatch.delenv("FORERUNNER_SCAN_DONE", raising=False)
    rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "scan-first" not in cap.err


def test_version_flag_prints_package_version(capsys):
    from codeforerunner import __version__
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    cap = capsys.readouterr()
    assert __version__ in cap.out


def test_scan_prints_env_hint(capsys):
    rc = main(["scan"])
    cap = capsys.readouterr()
    assert rc == 0
    assert "FORERUNNER_SCAN_DONE" in cap.err


def test_check_no_config_exits_zero(tmp_path, capsys):
    rc = main(["--repo", str(tmp_path), "check"])
    assert rc == 0


def test_check_with_violations_exits_one(tmp_path, capsys):
    (tmp_path / "README.md").write_text("no CLI exists\n", encoding="utf-8")
    (tmp_path / "src" / "codeforerunner").mkdir(parents=True)
    (tmp_path / "src" / "codeforerunner" / "cli.py").write_text("# cli\n", encoding="utf-8")
    (tmp_path / "forerunner.config.yaml").write_text(
        "enabled_rules:\n  - R1-no-cli\n", encoding="utf-8"
    )
    rc = main(["--repo", str(tmp_path), "check"])
    cap = capsys.readouterr()
    assert rc == 1
    assert "R1-no-cli" in cap.err


def test_check_invalid_config_exits_two(tmp_path, capsys):
    (tmp_path / "forerunner.config.yaml").write_text(
        "approaching_eol_threshold_months: not-a-number\n", encoding="utf-8"
    )
    rc = main(["--repo", str(tmp_path), "check"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "invalid config" in cap.err


# ── refresh ───────────────────────────────────────────────────────────────────

def test_refresh_emits_all_task_bundles(tmp_path, capsys):
    """forerunner refresh outputs scan + check + all doc task bundles separated by ---."""
    task_names = ["scan", "check", "readme", "api-docs", "stack-docs",
                  "diagrams", "flows", "version-audit"]
    tasks_dir = tmp_path / "prompts" / "tasks"
    system_dir = tmp_path / "prompts" / "system"
    system_dir.mkdir(parents=True)
    (system_dir / "base.md").write_text("# base\n", encoding="utf-8")
    (tmp_path / "prompts" / "partials").mkdir()
    tasks_dir.mkdir(parents=True)
    for name in task_names:
        (tasks_dir / f"{name}.md").write_text(f"# {name} task\n", encoding="utf-8")

    rc = main(["--repo", str(tmp_path), "refresh"])
    cap = capsys.readouterr()
    assert rc == 0
    for name in task_names:
        assert f"<!-- task: {name}.md -->" in cap.out
    assert cap.out.count("\n---\n") == len(task_names) - 1


def test_refresh_exits_nonzero_on_missing_task(tmp_path, capsys):
    """refresh returns early with rc=2 when a task file is missing."""
    rc = main(["--repo", str(tmp_path), "refresh"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "error:" in cap.err


# ── Error / edge paths ────────────────────────────────────────────────────────

def test_get_bundle_error_when_repo_has_no_prompts(tmp_path, capsys):
    rc = main(["--repo", str(tmp_path), "doc", "scan"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "error:" in cap.err


def test_get_bundle_catches_resolve_bundle_error(tmp_path, capsys, monkeypatch):
    _seed_repo_with_config(tmp_path)
    with patch("codeforerunner.cli._resolve_bundle", side_effect=FileNotFoundError("gone")):
        rc = main(["--repo", str(tmp_path), "doc", "readme"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "error:" in cap.err


def test_cmd_init_full_exits_when_scan_fails(tmp_path, capsys):
    # no prompts/tasks in tmp_path → scan bundle lookup fails → early return
    rc = main(["--repo", str(tmp_path), "init", "--full"])
    capsys.readouterr()
    assert rc == 2


def test_cmd_mcp_server_bad_repo_exits_two(tmp_path, capsys):
    rc = main(["--repo", str(tmp_path), "mcp-server"])
    cap = capsys.readouterr()
    assert rc == 2
    assert "mcp_server:" in cap.err


def test_cmd_mcp_server_success_path(capsys):
    with patch("codeforerunner.mcp_server.serve", return_value=0) as mock_serve:
        rc = main(["mcp-server"])
    capsys.readouterr()
    assert rc == 0
    mock_serve.assert_called_once()
