"""Tests for codeforerunner.check drift detection."""
from __future__ import annotations

from pathlib import Path

from codeforerunner.check import Violation, format_violations, run

REPO = Path(__file__).resolve().parents[1]


def test_real_repo_has_no_drift():
    assert run(REPO) == []


def _seed(tmp_path: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def test_phrase_with_trigger_yields_violation(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "Intro\nno CLI exists here\nend\n",
            "src/codeforerunner/cli.py": "# cli\n",
        },
    )
    vs = run(tmp_path)
    assert len(vs) == 1
    v = vs[0]
    assert isinstance(v, Violation)
    assert v.rule_id == "R1-no-cli"
    assert v.line == 2
    assert v.path == tmp_path / "README.md"


def test_phrase_without_trigger_no_violation(tmp_path):
    _seed(tmp_path, {"README.md": "no CLI exists\n"})
    assert run(tmp_path) == []


def test_trigger_without_phrase_no_violation(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "All good here.\n",
            "src/codeforerunner/cli.py": "# cli\n",
            "pyproject.toml": "[project]\n",
        },
    )
    assert run(tmp_path) == []


def test_docs_directory_scanned(tmp_path):
    _seed(
        tmp_path,
        {
            "docs/guide.md": "there is no installer yet\n",
            "src/codeforerunner/installer.py": "# installer\n",
        },
    )
    vs = run(tmp_path)
    assert len(vs) == 1
    assert vs[0].rule_id == "R4-no-installer"
    assert vs[0].path == tmp_path / "docs" / "guide.md"


def test_ci_glob_trigger(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "no CI workflow\n",
            ".github/workflows/test.yml": "name: test\n",
        },
    )
    vs = run(tmp_path)
    assert any(v.rule_id == "R3-no-ci" for v in vs)


def test_format_violations_smoke(tmp_path):
    v = Violation(path=tmp_path / "README.md", line=3, rule_id="R1-no-cli", message="bad")
    out = format_violations([v])
    assert "README.md:3" in out
    assert "R1-no-cli" in out
    assert "bad" in out


def test_format_violations_empty():
    assert format_violations([]) == ""


def test_r6_docker_phrase_with_dockerfile_yields_violation(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "We have no Docker image here\n",
            "Dockerfile": "FROM scratch\n",
        },
    )
    vs = run(tmp_path)
    assert [v.rule_id for v in vs] == ["R6-no-docker"]


def test_r6_docker_phrase_with_compose_yields_violation(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "no Dockerfile in this repo\n",
            "compose.yml": "services: {}\n",
        },
    )
    vs = run(tmp_path)
    assert [v.rule_id for v in vs] == ["R6-no-docker"]


def test_r6_docker_phrase_without_trigger_no_violation(tmp_path):
    _seed(tmp_path, {"README.md": "no Docker image here\n"})
    assert run(tmp_path) == []


def test_r6b_makefile_phrase_with_trigger_yields_violation(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "no Makefile is provided\n",
            "Makefile": "all:\n\techo hi\n",
        },
    )
    vs = run(tmp_path)
    assert [v.rule_id for v in vs] == ["R6b-no-makefile"]


def test_r6b_makefile_phrase_without_trigger_no_violation(tmp_path):
    _seed(tmp_path, {"README.md": "no Makefile here\n"})
    assert run(tmp_path) == []


def test_r7_mcp_phrase_with_trigger_yields_violation(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "There is no MCP server in this repo\n",
            "src/codeforerunner/mcp_server.py": "# mcp\n",
        },
    )
    vs = run(tmp_path)
    assert [v.rule_id for v in vs] == ["R7-no-mcp"]


def test_r7_mcp_phrase_without_trigger_no_violation(tmp_path):
    _seed(tmp_path, {"README.md": "no MCP server here\n"})
    assert run(tmp_path) == []


def test_r8_marketplace_phrase_with_trigger_yields_violation(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "We have no marketplace manifest yet\n",
            "plugins/codex/marketplace.json": "{}\n",
        },
    )
    vs = run(tmp_path)
    assert [v.rule_id for v in vs] == ["R8-no-marketplace"]


def test_r8_marketplace_phrase_without_trigger_no_violation(tmp_path):
    _seed(tmp_path, {"README.md": "no marketplace here\n"})
    assert run(tmp_path) == []


def test_real_repo_r7_r8_triggers_active_but_no_drift():
    """R7 and R8 trigger files exist in the real repo; no doc phrase should fire."""
    vs = run(REPO)
    rule_ids = {v.rule_id for v in vs}
    assert "R7-no-mcp" not in rule_ids
    assert "R8-no-marketplace" not in rule_ids
    assert vs == []


def test_multiple_violations_in_one_doc(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "no CLI exists\nno pre-commit hook here\n",
            "src/codeforerunner/cli.py": "# cli\n",
            ".pre-commit-hooks.yaml": "- id: check\n",
        },
    )
    vs = run(tmp_path)
    rule_ids = [v.rule_id for v in vs]
    assert "R1-no-cli" in rule_ids
    assert "R2-no-pre-commit" in rule_ids


def test_multiple_docs_both_yield_violations(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "no CLI exists\n",
            "docs/guide.md": "no CLI exists\n",
            "src/codeforerunner/cli.py": "# cli\n",
        },
    )
    vs = run(tmp_path)
    paths = {v.path.name for v in vs}
    assert "README.md" in paths
    assert "guide.md" in paths


def test_enabled_rules_empty_list_skips_all(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "no CLI exists\nno pre-commit hook\n",
            "src/codeforerunner/cli.py": "# cli\n",
            ".pre-commit-hooks.yaml": "- id: check\n",
        },
    )
    from codeforerunner.config import CheckConfig
    cfg = CheckConfig(enabled_rules=())
    assert run(tmp_path, cfg) == []


def test_ignore_paths_glob_pattern(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "no CLI exists\n",
            "docs/guide.md": "no CLI exists\n",
            "docs/ref.md": "no CLI exists\n",
            "src/codeforerunner/cli.py": "# cli\n",
        },
    )
    from codeforerunner.config import CheckConfig
    cfg = CheckConfig(ignore_paths=("docs/*.md",))
    vs = run(tmp_path, cfg)
    paths = {v.path.name for v in vs}
    assert "guide.md" not in paths
    assert "ref.md" not in paths
    assert "README.md" in paths


def test_unicode_error_file_skipped(tmp_path):
    (tmp_path / "src" / "codeforerunner").mkdir(parents=True)
    (tmp_path / "src" / "codeforerunner" / "cli.py").write_text("# cli\n", encoding="utf-8")
    binary = tmp_path / "README.md"
    binary.write_bytes(b"no CLI exists\xff\xfe bad bytes")
    vs = run(tmp_path)
    assert vs == []


def test_no_readme_no_docs_returns_empty(tmp_path):
    (tmp_path / "src" / "codeforerunner").mkdir(parents=True)
    (tmp_path / "src" / "codeforerunner" / "cli.py").write_text("# cli\n", encoding="utf-8")
    assert run(tmp_path) == []


def test_violation_line_number_correct(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "line one\nline two\nno CLI exists here\nline four\n",
            "src/codeforerunner/cli.py": "# cli\n",
        },
    )
    vs = run(tmp_path)
    assert len(vs) == 1
    assert vs[0].line == 3


# ── Inverse rules (RI*) ────────────────────────────────────────────────────


def test_ri1_fires_when_cli_absent(tmp_path):
    _seed(tmp_path, {"README.md": "Run `forerunner init` to get started.\n"})
    vs = run(tmp_path)
    assert any(v.rule_id == "RI1-missing-cli" for v in vs)


def test_ri1_silent_when_cli_present(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "Run `forerunner init` to get started.\n",
            "src/codeforerunner/cli.py": "# cli\n",
        },
    )
    assert not any(v.rule_id == "RI1-missing-cli" for v in run(tmp_path))


def test_ri5_fires_when_pyproject_absent(tmp_path):
    _seed(tmp_path, {"README.md": "Install with `pip install codeforerunner`.\n"})
    vs = run(tmp_path)
    assert any(v.rule_id == "RI5-missing-python-package" for v in vs)


def test_ri5_silent_when_pyproject_present(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "Install with `pip install codeforerunner`.\n",
            "pyproject.toml": '[project]\nname = "codeforerunner"\n',
        },
    )
    assert not any(v.rule_id == "RI5-missing-python-package" for v in run(tmp_path))


def test_ri7_fires_when_mcp_server_absent(tmp_path):
    _seed(tmp_path, {"README.md": "Start with `forerunner mcp-server`.\n"})
    vs = run(tmp_path)
    assert any(v.rule_id == "RI7-missing-mcp" for v in vs)


def test_ri7_silent_when_mcp_server_present(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "Start with `forerunner mcp-server`.\n",
            "src/codeforerunner/mcp_server.py": "# mcp\n",
        },
    )
    assert not any(v.rule_id == "RI7-missing-mcp" for v in run(tmp_path))


# ── Version drift (RV1) ────────────────────────────────────────────────────


def test_rv1_fires_when_pin_mismatches(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "Install `pip install codeforerunner==0.1.0`.\n",
            "pyproject.toml": '[project]\nname = "codeforerunner"\nversion = "0.3.1"\n',
        },
    )
    vs = run(tmp_path)
    rv = [v for v in vs if v.rule_id == "RV1-version-drift"]
    assert len(rv) == 1
    assert "0.1.0" in rv[0].message
    assert "0.3.1" in rv[0].message


def test_rv1_silent_when_pin_matches(tmp_path):
    _seed(
        tmp_path,
        {
            "README.md": "Install `pip install codeforerunner==0.3.1`.\n",
            "pyproject.toml": '[project]\nname = "codeforerunner"\nversion = "0.3.1"\n',
        },
    )
    assert not any(v.rule_id == "RV1-version-drift" for v in run(tmp_path))


def test_rv1_skips_changelog_md(tmp_path):
    # CHANGELOG.md not in _scanned_docs; old pins there should not fire
    _seed(
        tmp_path,
        {
            "CHANGELOG.md": "## 0.1.0\n- `pip install codeforerunner==0.1.0`\n",
            "pyproject.toml": '[project]\nname = "codeforerunner"\nversion = "0.3.1"\n',
        },
    )
    assert not any(v.rule_id == "RV1-version-drift" for v in run(tmp_path))


def test_rv1_silent_when_no_pyproject(tmp_path):
    _seed(tmp_path, {"README.md": "See `pip install codeforerunner==0.1.0`.\n"})
    assert not any(v.rule_id == "RV1-version-drift" for v in run(tmp_path))


def test_rv1_not_run_when_excluded_from_enabled_rules(tmp_path):
    from codeforerunner.config import CheckConfig

    _seed(
        tmp_path,
        {
            "README.md": "Install `pip install codeforerunner==0.1.0`.\n",
            "pyproject.toml": '[project]\nname = "codeforerunner"\nversion = "0.3.1"\n',
        },
    )
    cfg = CheckConfig(enabled_rules=("R1-no-cli",))
    assert not any(v.rule_id == "RV1-version-drift" for v in run(tmp_path, cfg))


# ── Version drift internals ────────────────────────────────────────────────────

def test_rv1_skips_changelog_in_docs_dir(tmp_path):
    # CHANGELOG.md inside docs/ is picked up by _scanned_docs but must be skipped
    _seed(
        tmp_path,
        {
            "docs/CHANGELOG.md": "codeforerunner==0.1.0\n",
            "pyproject.toml": '[project]\nname = "codeforerunner"\nversion = "0.3.1"\n',
        },
    )
    vs = [v for v in run(tmp_path) if v.rule_id == "RV1-version-drift"]
    assert vs == []


def test_rv1_skips_ignored_path(tmp_path):
    from codeforerunner.config import CheckConfig
    _seed(
        tmp_path,
        {
            "docs/legacy.md": "codeforerunner==0.1.0\n",
            "pyproject.toml": '[project]\nname = "codeforerunner"\nversion = "0.3.1"\n',
        },
    )
    cfg = CheckConfig(ignore_paths=("docs/legacy.md",))
    vs = [v for v in run(tmp_path, cfg) if v.rule_id == "RV1-version-drift"]
    assert vs == []


def test_rv1_skips_unreadable_doc(tmp_path):
    import pathlib
    from unittest.mock import MagicMock, patch
    from codeforerunner.check import _check_version_drift

    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.0"\n', encoding="utf-8")
    mock_doc = MagicMock()
    mock_doc.name = "guide.md"
    mock_doc.read_text.side_effect = OSError("permission denied")

    violations = _check_version_drift(tmp_path, [mock_doc], (), None)
    assert violations == []


def test_path_ignored_doc_outside_repo(tmp_path):
    from codeforerunner.check import _path_ignored
    repo = tmp_path / "some-repo"
    doc = tmp_path / "other-location" / "README.md"
    # Should not crash; uses abs posix path matching
    result = _path_ignored(repo, doc, ("*.md",))
    assert isinstance(result, bool)


def test_current_version_returns_none_on_oserror(tmp_path):
    import pathlib
    from unittest.mock import patch
    from codeforerunner.check import _current_version

    (tmp_path / "pyproject.toml").touch()
    with patch.object(pathlib.Path, "read_text", side_effect=OSError("denied")):
        result = _current_version(tmp_path)
    assert result is None


def test_workflows_lint_when_actionlint_available():
    import shutil
    import subprocess

    import pytest

    if not shutil.which("actionlint"):
        pytest.skip("actionlint not installed")
    workflow_files = sorted(str(p.relative_to(REPO)) for p in (REPO / ".github/workflows").glob("*.yml"))
    proc = subprocess.run(
        ["actionlint", *workflow_files],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
