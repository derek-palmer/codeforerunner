from __future__ import annotations

import json
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
MARKETPLACE = REPO / "plugins/codex/marketplace.json"


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


def test_marketplace_check_dry_run_no_writes(tmp_path, capsys):
    dest = tmp_path / "marketplace.json"
    rc = installer.install(
        agent="codex",
        repo_root=REPO,
        source=None,
        dest_override=dest,
        check_only=True,
        kind="marketplace",
    )
    assert rc == EXIT_OK
    assert not dest.exists()
    assert "would create" in capsys.readouterr().out


def test_marketplace_creates_dest(tmp_path):
    dest = tmp_path / "marketplace.json"
    rc = installer.install(
        agent="codex",
        repo_root=REPO,
        source=None,
        dest_override=dest,
        check_only=False,
        kind="marketplace",
    )
    assert rc == EXIT_OK
    assert dest.is_file()
    data = json.loads(dest.read_text(encoding="utf-8"))
    assert data["marketplace"]["id"] == "codeforerunner"


def test_marketplace_idempotent_second_run(tmp_path, capsys):
    dest = tmp_path / "marketplace.json"
    installer.install(
        agent="codex",
        repo_root=REPO,
        source=None,
        dest_override=dest,
        check_only=False,
        kind="marketplace",
    )
    first = dest.read_bytes()
    capsys.readouterr()
    rc = installer.install(
        agent="codex",
        repo_root=REPO,
        source=None,
        dest_override=dest,
        check_only=False,
        kind="marketplace",
    )
    assert rc == EXIT_OK
    assert dest.read_bytes() == first
    assert "skip" in capsys.readouterr().out


def test_marketplace_abort_on_user_edit(tmp_path):
    dest = tmp_path / "marketplace.json"
    dest.write_text('{"user": "edit"}\n', encoding="utf-8")
    rc = installer.install(
        agent="codex",
        repo_root=REPO,
        source=None,
        dest_override=dest,
        check_only=False,
        kind="marketplace",
    )
    assert rc == EXIT_UNMANAGED_DEST
    assert dest.read_text(encoding="utf-8") == '{"user": "edit"}\n'


def test_marketplace_manifest_file_present_and_valid():
    assert MARKETPLACE.is_file()
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    assert data["marketplace"]["id"] == "codeforerunner"
    assert len(data["plugins"]) >= 1


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


# ── _home / resolve_target / resolve_skill_target ─────────────────────────────

def test_home_returns_path():
    from codeforerunner.installer import _home
    result = _home()
    assert isinstance(result, Path)
    assert result.is_absolute()


def test_resolve_target_codex_default():
    t = installer.resolve_target("codex", None)
    assert t.name == "codex"
    assert ".codex" in str(t.path)


def test_resolve_target_claude_default():
    t = installer.resolve_target("claude", None)
    assert t.name == "claude"
    assert ".claude" in str(t.path)


def test_resolve_target_with_override(tmp_path):
    override = tmp_path / "override.md"
    override.touch()
    t = installer.resolve_target("claude", override)
    assert t.path == override.resolve()


def test_resolve_target_gemini_raises():
    with pytest.raises(ValueError, match="gemini extensions install"):
        installer.resolve_target("gemini", None)


def test_resolve_target_unknown_raises():
    with pytest.raises(ValueError, match="unknown agent"):
        installer.resolve_target("unknown-agent", None)


def test_resolve_skill_target_codex():
    t = installer.resolve_skill_target("codex", "my-skill")
    assert "my-skill" in str(t.path)
    assert ".codex" in str(t.path)


def test_resolve_skill_target_claude():
    t = installer.resolve_skill_target("claude", "my-skill")
    assert "my-skill" in str(t.path)
    assert ".claude" in str(t.path)


def test_resolve_skill_target_unsupported_raises():
    with pytest.raises(ValueError, match="install_all not supported"):
        installer.resolve_skill_target("generic", "my-skill")


def test_task_skill_slugs_include_arch_review():
    assert "forerunner-arch-review" in installer.TASK_SKILL_SLUGS
    assert (REPO / "plugins/codeforerunner/skills/forerunner-arch-review/SKILL.md").is_file()
    assert (REPO / "skills/forerunner-arch-review/SKILL.md").is_file()


# ── install_all_skills ────────────────────────────────────────────────────────

def test_install_all_skills_check_only(tmp_path):
    import io
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    rc = installer.install_all_skills(
        agent="claude",
        repo_root=REPO,
        check_only=True,
        out=out_buf,
        err=err_buf,
    )
    assert rc == EXIT_OK
    assert "would create" in out_buf.getvalue() or "skip" in out_buf.getvalue()


def test_install_all_skills_source_missing_reports_warning(tmp_path):
    import io
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    # tmp_path has no skills directory
    rc = installer.install_all_skills(
        agent="claude",
        repo_root=tmp_path,
        check_only=True,
        out=out_buf,
        err=err_buf,
    )
    assert rc == installer.EXIT_BODY_MISMATCH
    assert "warning:" in err_buf.getvalue()


def test_install_all_skills_unsupported_agent_returns_usage(tmp_path):
    import io
    from unittest.mock import patch
    out_buf = io.StringIO()
    err_buf = io.StringIO()

    # Provide a skill file so resolve_skill_target is reached
    skill_dir = tmp_path / "plugins" / "codeforerunner" / "skills" / installer.TASK_SKILL_SLUGS[0]
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("content")

    with patch.object(installer, "TASK_SKILL_SLUGS", (installer.TASK_SKILL_SLUGS[0],)):
        rc = installer.install_all_skills(
            agent="generic",
            repo_root=tmp_path,
            check_only=True,
            out=out_buf,
            err=err_buf,
        )
    assert rc == EXIT_USAGE


def test_install_all_skills_skip_uptodate(tmp_path):
    import io
    from unittest.mock import patch

    slug = "test-skill"
    content = b"skill content"

    src_dir = tmp_path / "plugins" / "codeforerunner" / "skills" / slug
    src_dir.mkdir(parents=True)
    (src_dir / "SKILL.md").write_bytes(content)

    dest_file = tmp_path / "dest" / "SKILL.md"
    dest_file.parent.mkdir(parents=True)
    dest_file.write_bytes(content)  # same content — should be skipped

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    with patch.object(installer, "TASK_SKILL_SLUGS", (slug,)), \
         patch.object(installer, "resolve_skill_target",
                      return_value=installer.Target("claude", dest_file)):
        rc = installer.install_all_skills(
            agent="claude",
            repo_root=tmp_path,
            check_only=False,
            out=out_buf,
            err=err_buf,
        )
    assert rc == EXIT_OK
    assert "skip" in out_buf.getvalue()


def test_install_all_skills_update_when_dest_differs(tmp_path):
    import io
    from unittest.mock import patch

    slug = "test-skill"

    src_dir = tmp_path / "plugins" / "codeforerunner" / "skills" / slug
    src_dir.mkdir(parents=True)
    (src_dir / "SKILL.md").write_bytes(b"new content")

    dest_file = tmp_path / "dest" / "SKILL.md"
    dest_file.parent.mkdir(parents=True)
    dest_file.write_bytes(b"old content")  # different → should update

    out_buf = io.StringIO()
    err_buf = io.StringIO()

    with patch.object(installer, "TASK_SKILL_SLUGS", (slug,)), \
         patch.object(installer, "resolve_skill_target",
                      return_value=installer.Target("claude", dest_file)):
        rc = installer.install_all_skills(
            agent="claude",
            repo_root=tmp_path,
            check_only=False,
            out=out_buf,
            err=err_buf,
        )
    assert rc == EXIT_OK
    assert "update" in out_buf.getvalue()
    assert dest_file.read_bytes() == b"new content"


def test_install_all_skills_write_error(tmp_path):
    import io
    from unittest.mock import patch
    out_buf = io.StringIO()
    err_buf = io.StringIO()

    slug = "test-skill"
    skill_dir = tmp_path / "plugins" / "codeforerunner" / "skills" / slug
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("content")

    import pathlib
    original_write_bytes = pathlib.Path.write_bytes

    def _fail_write(self, data):
        raise OSError("disk full")

    with patch.object(installer, "TASK_SKILL_SLUGS", (slug,)), \
         patch.object(installer, "resolve_skill_target",
                      return_value=installer.Target("claude", tmp_path / "dest" / "SKILL.md")), \
         patch.object(pathlib.Path, "write_bytes", _fail_write):
        rc = installer.install_all_skills(
            agent="claude",
            repo_root=tmp_path,
            check_only=False,
            out=out_buf,
            err=err_buf,
        )
    assert rc == installer.EXIT_BODY_MISMATCH
    assert "error:" in err_buf.getvalue()


# ── resolve_marketplace_target ────────────────────────────────────────────────

def test_resolve_marketplace_target_generic_no_path_raises():
    with pytest.raises(ValueError, match="generic marketplace target"):
        installer.resolve_marketplace_target("generic", None)


def test_resolve_marketplace_target_with_override(tmp_path):
    override = tmp_path / "mp.json"
    override.touch()
    t = installer.resolve_marketplace_target("generic", override)
    assert t.path == override.resolve()


def test_resolve_marketplace_target_codex_default():
    t = installer.resolve_marketplace_target("codex", None)
    assert ".codex" in str(t.path)
    assert "codeforerunner" in str(t.path)


def test_resolve_marketplace_target_unsupported_raises():
    with pytest.raises(ValueError, match="marketplace not supported"):
        installer.resolve_marketplace_target("claude", None)


# ── strip_frontmatter / extract_frontmatter / render ─────────────────────────

def test_strip_frontmatter_no_frontmatter():
    assert installer.strip_frontmatter("plain text") == "plain text"


def test_extract_frontmatter_with_frontmatter():
    result = installer.extract_frontmatter("---\nname: x\nversion: 1\n---\nbody")
    assert result == "---\nname: x\nversion: 1\n---\n"


def test_extract_frontmatter_no_frontmatter():
    assert installer.extract_frontmatter("plain text") == ""


def test_render_preserves_dest_frontmatter():
    source = "---\nname: src\n---\nbody content\n"
    dest_fm = "---\nagent: claude\n---\n"
    dest_existing = dest_fm + installer.MARKER_BEGIN + "\nold\n" + installer.MARKER_END + "\n"
    result = installer.render(source, dest_existing, "claude")
    assert result.startswith(dest_fm)
    assert installer.MARKER_BEGIN in result
    assert "body content" in result


# ── find_markers / overlay edge cases ────────────────────────────────────────

def test_find_markers_no_end_returns_none():
    text = installer.MARKER_BEGIN + "\nbody\n"  # no MARKER_END
    assert installer.find_markers(text) is None


def test_overlay_raises_when_no_markers():
    with pytest.raises(RuntimeError, match="overlay: span is None"):
        installer.overlay("no markers here at all", "new body")


# ── install() error paths ─────────────────────────────────────────────────────

def test_install_marketplace_invalid_agent_returns_usage(tmp_path, capsys):
    rc = installer.install(
        agent="claude",
        repo_root=REPO,
        source=None,
        dest_override=None,
        check_only=True,
        kind="marketplace",
    )
    assert rc == EXIT_USAGE


def test_install_marketplace_source_not_found(tmp_path, capsys):
    rc = installer.install(
        agent="codex",
        repo_root=tmp_path,  # no marketplace.json here
        source=None,
        dest_override=tmp_path / "out.json",
        check_only=True,
        kind="marketplace",
    )
    assert rc == EXIT_USAGE


def test_install_skill_source_not_found(tmp_path, capsys):
    rc = installer.install(
        agent="generic",
        repo_root=tmp_path,
        source=tmp_path / "nonexistent.md",  # doesn't exist
        dest_override=tmp_path / "out.md",
        check_only=True,
    )
    assert rc == EXIT_USAGE


def test_install_skill_canonical_not_found(tmp_path, capsys):
    fake_source = tmp_path / "fake.md"
    fake_source.write_text("content")
    rc = installer.install(
        agent="generic",
        repo_root=tmp_path,  # no agent/codeforerunner.skill.md
        source=fake_source,
        dest_override=tmp_path / "out.md",
        check_only=True,
    )
    assert rc == EXIT_USAGE


# ── _cli_entry paths ──────────────────────────────────────────────────────────

def test_cli_entry_all_flag(tmp_path, capsys, monkeypatch):
    from codeforerunner.cli import main as cli_main
    monkeypatch.setenv("HOME", str(tmp_path))
    rc = cli_main(["--repo", str(REPO), "install", "--all", "--check"])
    capsys.readouterr()
    assert isinstance(rc, int)


def test_cli_entry_no_agent_returns_usage(tmp_path, capsys):
    from codeforerunner.cli import main as cli_main
    rc = cli_main(["install"])
    capsys.readouterr()
    assert rc == EXIT_USAGE
