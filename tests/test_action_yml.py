"""Guards on the composite action's check step (`action.yml`).

Regression tests for #108. `--repo` is a top-level flag, so
`forerunner check --repo <path>` exits 2 on argparse before any drift check
runs. Asserting a non-zero exit is not enough — exit 2 (failed to run) and
exit 1 (drift found) are both non-zero — so these tests pin the exit codes:

* the extracted argv parses with the real CLI parser;
* running it against a known-drifting fixture repo exits 1 with the
  violation text on stderr;
* the step's shell logic maps CLI exit codes to job outcomes correctly, and
  never swallows anything but drift.
"""

import os
import re
import shlex
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from codeforerunner.cli import build_parser

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTION_YML = REPO_ROOT / "action.yml"
DRIFTING_REPO = Path(__file__).resolve().parent / "fixtures" / "drifting-repo"


def _check_step():
    doc = yaml.safe_load(ACTION_YML.read_text())
    for step in doc["runs"]["steps"]:
        if "forerunner --repo" in (step.get("run") or "") or re.search(
            r"^\s*forerunner\b", step.get("run") or "", re.M
        ):
            return step
    pytest.fail("action.yml has no step invoking the forerunner CLI")


def _script(repo: str, fail_on_drift: str) -> str:
    """The check step's shell body with its `inputs.*` expressions filled in."""
    script = _check_step()["run"]
    script = script.replace("${{ inputs.repo }}", repo)
    script = script.replace("${{ inputs.fail-on-drift }}", fail_on_drift)
    assert "${{" not in script, f"unsubstituted expression in step: {script}"
    return script


def _forerunner_argvs(repo: str = "/repo"):
    """Every `forerunner ...` invocation in the check step, as argv lists."""
    argvs = []
    for line in _script(repo, "true").splitlines():
        line = line.strip()
        if not line.startswith("forerunner "):
            continue
        line = re.sub(r"\s*\|\|.*$", "", line)
        argvs.append(shlex.split(line)[1:])
    assert argvs, "check step invokes no forerunner command"
    return argvs


def _src_env():
    """Env pinning PYTHONPATH at this checkout's `src/`, so the test exercises it."""
    env = dict(os.environ)
    src = str(REPO_ROOT / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{src}{os.pathsep}{existing}" if existing else src
    return env


# --- argv shape ------------------------------------------------------------


@pytest.mark.parametrize("argv", _forerunner_argvs())
def test_action_invocation_parses(argv):
    """The action's argv must reach `cmd_check`, not die in argparse (exit 2)."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:  # argparse error -> exit 2, never a drift signal
        pytest.fail(f"`forerunner {' '.join(argv)}` failed to parse (exit {exc.code})")
    assert args.cmd == "check"
    assert args.repo == "/repo"


def test_repo_flag_precedes_subcommand():
    for argv in _forerunner_argvs():
        assert argv.index("--repo") < argv.index("check"), (
            f"--repo must precede the subcommand: {argv!r}"
        )


# --- end-to-end against a drifting fixture ---------------------------------


def test_action_argv_reports_drift_as_exit_1():
    """Exit 1 + violation text: proves the check ran, not that it failed to."""
    argv = _forerunner_argvs(str(DRIFTING_REPO))[0]
    proc = subprocess.run(
        [sys.executable, "-m", "codeforerunner.cli", *argv],
        capture_output=True,
        text=True,
        env=_src_env(),
    )
    assert proc.returncode == 1, (
        f"expected exit 1 (drift), got {proc.returncode}: {proc.stderr}"
    )
    assert "RI1-missing-cli" in proc.stderr, proc.stderr


def test_action_argv_is_clean_on_a_repo_without_config(tmp_path):
    argv = _forerunner_argvs(str(tmp_path))[0]
    proc = subprocess.run(
        [sys.executable, "-m", "codeforerunner.cli", *argv],
        capture_output=True,
        text=True,
        env=_src_env(),
    )
    assert proc.returncode == 0, proc.stderr


# --- the step's exit-code mapping ------------------------------------------


def _run_step_with_stub(tmp_path, cli_exit: int, fail_on_drift: str) -> int:
    """Run the check step's shell body against a `forerunner` stub exiting *cli_exit*."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "forerunner"
    stub.write_text(f'#!/bin/sh\nexit {cli_exit}\n')
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)

    script = tmp_path / "step.sh"
    script.write_text(_script(str(tmp_path), fail_on_drift))

    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
    # Mirror the shell GitHub gives a composite `shell: bash` step.
    return subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", str(script)],
        capture_output=True,
        text=True,
        env=env,
    ).returncode


@pytest.mark.parametrize(
    "cli_exit,fail_on_drift,expected",
    [
        (0, "true", 0),   # clean
        (0, "false", 0),
        (1, "true", 1),   # drift, gated
        (1, "false", 0),  # drift, ungated -> warning only
        (2, "true", 2),   # failed to run -> always loud
        (2, "false", 2),  # ...including when drift is ungated (#108)
    ],
)
def test_step_exit_code_mapping(tmp_path, cli_exit, fail_on_drift, expected):
    assert _run_step_with_stub(tmp_path, cli_exit, fail_on_drift) == expected
