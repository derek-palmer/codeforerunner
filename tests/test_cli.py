"""Tests for the initial forerunner CLI scaffold."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*argv: str) -> int:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from codeforerunner.cli import main

    return main(list(argv))


def test_root_help_exits_cleanly(capsys) -> None:
    exit_code = run_cli("--help")

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "usage: forerunner" in captured.out
    assert "Default configuration file: forerunner.config.yaml" in captured.out
    for command in ("init", "generate", "check", "review", "hook", "config", "adapters"):
        assert command in captured.out


def test_nested_help_exits_cleanly(capsys) -> None:
    exit_code = run_cli("hook", "install", "--help")

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "usage: forerunner hook install" in captured.out


def test_placeholder_command_returns_non_zero(capsys) -> None:
    exit_code = run_cli("init")

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert "`forerunner init` is not implemented yet." in captured.err
