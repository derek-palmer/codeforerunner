from __future__ import annotations

from pathlib import Path

from codeforerunner import check
from codeforerunner.config import CheckConfig


def _seed(tmp_path: Path) -> None:
    """Create a fake repo with one triggering file and a doc containing matches for R1 + R3."""
    (tmp_path / "src/codeforerunner").mkdir(parents=True)
    (tmp_path / "src/codeforerunner/cli.py").write_text("# stub\n", encoding="utf-8")
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/ci.yml").write_text("name: ci\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "no CLI exists\nno CI workflow\n",
        encoding="utf-8",
    )
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/legacy.md").write_text("no CLI exists\n", encoding="utf-8")


def test_no_config_runs_all_rules(tmp_path):
    _seed(tmp_path)
    vs = check.run(tmp_path)
    rule_ids = {v.rule_id for v in vs}
    assert "R1-no-cli" in rule_ids
    assert "R3-no-ci" in rule_ids


def test_enabled_rules_restricts(tmp_path):
    _seed(tmp_path)
    cfg = CheckConfig(enabled_rules=("R1-no-cli",))
    vs = check.run(tmp_path, cfg)
    rule_ids = {v.rule_id for v in vs}
    assert rule_ids == {"R1-no-cli"}


def test_ignore_paths_skips_matching_docs(tmp_path):
    _seed(tmp_path)
    cfg = CheckConfig(ignore_paths=("docs/legacy.md",))
    vs = check.run(tmp_path, cfg)
    paths = {v.path.name for v in vs}
    assert "legacy.md" not in paths
    assert "README.md" in paths
