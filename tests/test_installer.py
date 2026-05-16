from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from codeforerunner import installer
from codeforerunner.installer import (
    EXIT_BODY_MISMATCH,
    EXIT_OK,
    EXIT_UNMANAGED_DEST,
    EXIT_USAGE,
    MARKER_BEGIN,
    MARKER_END,
)

REPO = Path(__file__).resolve().parents[1]
CANONICAL = REPO / "agent/codeforerunner.skill.md"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_install_check_dry_run_no_writes(tmp_path, capsys):
    dest = tmp_path / "out.md"
    rc = installer.install(
        agent="generic",
        repo_root=REPO,
        source=None,
        dest_override=dest,
        check_only=True,
    )
    assert rc == EXIT_OK
    assert not dest.exists()
    assert "would create" in capsys.readouterr().out


def test_install_body_parity_mismatch_aborts(tmp_path, capsys):
    bad = tmp_path / "altered.skill.md"
    _write(bad, "---\nname: x\n---\nALTERED BODY ≠ canonical\n")
    dest = tmp_path / "out.md"
    rc = installer.install(
        agent="generic",
        repo_root=REPO,
        source=bad,
        dest_override=dest,
        check_only=False,
    )
    assert rc == EXIT_BODY_MISMATCH
    assert not dest.exists()
    cap = capsys.readouterr()
    assert "body-parity" in cap.out + cap.err


def test_install_creates_dest_with_markers(tmp_path):
    dest = tmp_path / "out.md"
    rc = installer.install(
        agent="generic", repo_root=REPO, source=None, dest_override=dest, check_only=False
    )
    assert rc == EXIT_OK
    text = dest.read_text(encoding="utf-8")
    assert MARKER_BEGIN in text and MARKER_END in text
    canon_body = installer.strip_frontmatter(CANONICAL.read_text(encoding="utf-8"))
    assert canon_body in text


def test_install_idempotent_second_run(tmp_path, capsys):
    dest = tmp_path / "out.md"
    installer.install(
        agent="generic", repo_root=REPO, source=None, dest_override=dest, check_only=False
    )
    first = dest.read_text(encoding="utf-8")
    capsys.readouterr()
    rc = installer.install(
        agent="generic", repo_root=REPO, source=None, dest_override=dest, check_only=False
    )
    second = dest.read_text(encoding="utf-8")
    assert rc == EXIT_OK
    assert first == second
    assert "skip" in capsys.readouterr().out


def test_install_overlay_preserves_user_edits(tmp_path):
    dest = tmp_path / "out.md"
    canon_body = installer.strip_frontmatter(CANONICAL.read_text(encoding="utf-8"))
    seed = dedent(
        f"""\
        # user header
        custom prose user wrote

        {MARKER_BEGIN}
        stale body
        {MARKER_END}

        # user footer
        more custom prose
        """
    )
    _write(dest, seed)
    rc = installer.install(
        agent="generic", repo_root=REPO, source=None, dest_override=dest, check_only=False
    )
    assert rc == EXIT_OK
    out = dest.read_text(encoding="utf-8")
    assert "# user header" in out
    assert "custom prose user wrote" in out
    assert "# user footer" in out
    assert "more custom prose" in out
    assert "stale body" not in out
    assert canon_body in out


def test_install_unmanaged_existing_dest_aborts(tmp_path, capsys):
    dest = tmp_path / "out.md"
    _write(dest, "# entirely user authored, no markers here\n")
    rc = installer.install(
        agent="generic", repo_root=REPO, source=None, dest_override=dest, check_only=False
    )
    assert rc == EXIT_UNMANAGED_DEST
    assert dest.read_text(encoding="utf-8") == "# entirely user authored, no markers here\n"


def test_install_generic_requires_path():
    rc = installer.install(
        agent="generic", repo_root=REPO, source=None, dest_override=None, check_only=True
    )
    assert rc == EXIT_USAGE


def test_install_cli_subcommand_wired(tmp_path):
    from codeforerunner.cli import main

    dest = tmp_path / "out.md"
    rc = main(
        [
            "--repo",
            str(REPO),
            "install",
            "generic",
            "--check",
            "--path",
            str(dest),
        ]
    )
    assert rc == EXIT_OK
    assert not dest.exists()
