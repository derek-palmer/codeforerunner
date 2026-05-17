"""Tests for codeforerunner.check drift detection."""
from __future__ import annotations

from pathlib import Path

from codeforerunner.check import Violation, format_violations, run

REPO = Path("/Users/derek/code/codeforerunner")


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


def test_workflows_lint_when_actionlint_available():
    import shutil
    import subprocess

    import pytest

    if not shutil.which("actionlint"):
        pytest.skip("actionlint not installed")
    proc = subprocess.run(
        ["actionlint", ".github/workflows"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
