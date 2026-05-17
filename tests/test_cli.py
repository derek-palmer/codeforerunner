from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from codeforerunner.cli import main

REPO = Path(__file__).resolve().parents[1]


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
    rc = main(["--repo", str(REPO), "doc", "scan"])
    out = capsys.readouterr().out
    assert rc == 0
    scan_body = (REPO / "prompts" / "tasks" / "scan.md").read_text(encoding="utf-8")
    first_line = scan_body.splitlines()[0]
    assert first_line in out
    assert "<!-- task: scan.md -->" in out


def test_doc_unknown_task_exits_nonzero(capsys):
    rc = main(["--repo", str(REPO), "doc", "definitely-not-a-task"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "unknown task" in err


@pytest.mark.parametrize(
    "cmd,task_file",
    [("init", "init-agent-onboarding.md"), ("scan", "scan.md")],
)
def test_init_scan_resolve_bundle(cmd, task_file, capsys):
    rc = main(["--repo", str(REPO), cmd])
    out = capsys.readouterr().out
    assert rc == 0
    assert f"<!-- task: {task_file} -->" in out
    body = (REPO / "prompts" / "tasks" / task_file).read_text(encoding="utf-8")
    assert body.splitlines()[0] in out


def test_check_no_config_exits_zero(tmp_path, capsys):
    rc = main(["--repo", str(tmp_path), "check"])
    assert rc == 0
