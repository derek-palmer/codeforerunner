from __future__ import annotations

from pathlib import Path

import pytest

from codeforerunner import config


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_load_from_repo_returns_none_when_missing(tmp_path):
    assert config.load_from_repo(tmp_path) is None


def test_load_minimal_defaults(tmp_path):
    _write(tmp_path / "forerunner.config.yaml", "")
    cfg = config.load_from_repo(tmp_path)
    assert cfg is not None
    assert cfg.provider == "anthropic"
    assert cfg.check.block_on == ("HIGH", "MEDIUM")
    assert cfg.check.enabled_rules is None
    assert cfg.check.ignore_paths == ()


def test_load_full_example_shape(tmp_path):
    _write(
        tmp_path / "forerunner.config.yaml",
        """
provider: openai
model: gpt-x
output_dir: documents
context_max_files: 50
ignore_patterns:
  - "*.test.ts"
tasks:
  check:
    block_on: [HIGH]
    warn_on: [MEDIUM, LOW]
    enabled_rules: [R1-no-cli, R3-no-ci]
    ignore_paths: ["docs/legacy/*.md"]
  version_audit:
    enabled: false
    stale_after_days: 7
""",
    )
    cfg = config.load_from_repo(tmp_path)
    assert cfg is not None
    assert cfg.provider == "openai"
    assert cfg.model == "gpt-x"
    assert cfg.output_dir == Path("documents")
    assert cfg.context_max_files == 50
    assert cfg.ignore_patterns == ("*.test.ts",)
    assert cfg.check.block_on == ("HIGH",)
    assert cfg.check.warn_on == ("MEDIUM", "LOW")
    assert cfg.check.enabled_rules == ("R1-no-cli", "R3-no-ci")
    assert cfg.check.ignore_paths == ("docs/legacy/*.md",)
    assert cfg.version_audit.enabled is False
    assert cfg.version_audit.stale_after_days == 7


def test_unknown_provider_raises(tmp_path):
    _write(tmp_path / "forerunner.config.yaml", "provider: bogus\n")
    with pytest.raises(config.ConfigError, match="provider"):
        config.load_from_repo(tmp_path)


def test_unknown_severity_raises(tmp_path):
    _write(
        tmp_path / "forerunner.config.yaml",
        "tasks:\n  check:\n    block_on: [CRITICAL]\n",
    )
    with pytest.raises(config.ConfigError, match="severity"):
        config.load_from_repo(tmp_path)


def test_wrong_type_raises(tmp_path):
    _write(tmp_path / "forerunner.config.yaml", "ignore_patterns: not-a-list\n")
    with pytest.raises(config.ConfigError, match="ignore_patterns"):
        config.load_from_repo(tmp_path)


def test_malformed_yaml_raises_config_error(tmp_path):
    _write(tmp_path / "forerunner.config.yaml", "provider: [unbalanced\n")
    with pytest.raises(config.ConfigError, match="invalid YAML"):
        config.load_from_repo(tmp_path)


def test_example_file_is_valid():
    """The committed example must round-trip through the loader."""
    repo = Path(__file__).resolve().parents[1]
    example = repo / "forerunner.config.yaml.example"
    cfg = config.load(example)
    assert cfg.provider in {"anthropic", "openai", "google", "ollama"}
    assert cfg.check.block_on
