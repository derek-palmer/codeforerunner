"""Guards on the composite action's CLI invocation shape (`action.yml`).

Regression test for #108: `--repo` is a top-level flag, so `forerunner check
--repo <path>` exits 2 on argparse before any drift check runs. Asserting a
non-zero exit is not enough — exit 2 and exit 1 (drift found) are both
non-zero — so these tests parse the extracted argv with the real parser.
"""

import re
import shlex
from pathlib import Path

import pytest
import yaml

from codeforerunner.cli import build_parser

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTION_YML = REPO_ROOT / "action.yml"
FAKE_REPO = "/home/runner/work/example/example"


def _forerunner_argvs():
    """Every `forerunner ...` invocation in the action, as argv lists."""
    doc = yaml.safe_load(ACTION_YML.read_text())
    argvs = []
    for step in doc["runs"]["steps"]:
        # Substitute the only expression the invocation depends on.
        script = (step.get("run") or "").replace("${{ inputs.repo }}", FAKE_REPO)
        for line in script.splitlines():
            line = line.strip()
            if not line.startswith("forerunner "):
                continue
            line = re.sub(r"\s*\|\|\s*true$", "", line)
            argvs.append(shlex.split(line)[1:])
    return argvs


def test_action_invokes_forerunner_in_both_branches():
    argvs = _forerunner_argvs()
    assert len(argvs) == 2, (
        f"expected one invocation per fail-on-drift branch, got {argvs!r}"
    )


@pytest.mark.parametrize("argv", _forerunner_argvs())
def test_action_invocation_parses(argv):
    """The action's argv must reach `cmd_check`, not die in argparse (exit 2)."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:  # argparse error -> exit 2, never a drift signal
        pytest.fail(f"`forerunner {' '.join(argv)}` failed to parse (exit {exc.code})")
    assert args.cmd == "check"
    assert args.repo == FAKE_REPO


def test_repo_flag_precedes_subcommand():
    for argv in _forerunner_argvs():
        assert argv.index("--repo") < argv.index("check"), (
            f"--repo must precede the subcommand: {argv!r}"
        )
