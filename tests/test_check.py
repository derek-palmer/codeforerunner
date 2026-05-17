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
