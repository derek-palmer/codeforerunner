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
    assert cfg.check.block_on == ("HIGH", "MEDIUM")
    assert cfg.check.enabled_rules is None
    assert cfg.check.ignore_paths == ()
    assert cfg.approaching_eol_threshold_months == 6


def test_load_full_example_shape(tmp_path):
    _write(
        tmp_path / "forerunner.config.yaml",
        """
approaching_eol_threshold_months: 3
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
    assert cfg.approaching_eol_threshold_months == 3
    assert cfg.ignore_patterns == ("*.test.ts",)
    assert cfg.check.block_on == ("HIGH",)
    assert cfg.check.warn_on == ("MEDIUM", "LOW")
    assert cfg.check.enabled_rules == ("R1-no-cli", "R3-no-ci")
    assert cfg.check.ignore_paths == ("docs/legacy/*.md",)
    assert cfg.version_audit.enabled is False
    assert cfg.version_audit.stale_after_days == 7


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
    _write(tmp_path / "forerunner.config.yaml", "ignore_patterns: [unbalanced\n")
    with pytest.raises(config.ConfigError, match="invalid YAML"):
        config.load_from_repo(tmp_path)


# ── Internal validator edge cases ─────────────────────────────────────────────

def test_require_type_raises_config_error(tmp_path):
    # tasks.check must be a dict; passing a string triggers _require_type
    _write(tmp_path / "forerunner.config.yaml", "tasks:\n  check: not-a-dict\n")
    with pytest.raises(config.ConfigError, match=r"tasks\.check"):
        config.load_from_repo(tmp_path)


def test_coerce_str_tuple_not_list_raises(tmp_path):
    _write(tmp_path / "forerunner.config.yaml", "ignore_patterns: 42\n")
    with pytest.raises(config.ConfigError, match="ignore_patterns"):
        config.load_from_repo(tmp_path)


def test_coerce_str_tuple_non_string_item_raises(tmp_path):
    _write(tmp_path / "forerunner.config.yaml", "ignore_patterns:\n  - 123\n")
    with pytest.raises(config.ConfigError, match=r"ignore_patterns\[0\]"):
        config.load_from_repo(tmp_path)


def test_to_int_raises_config_error(tmp_path):
    # version_audit.stale_after_days must be int-convertible
    _write(
        tmp_path / "forerunner.config.yaml",
        "tasks:\n  version_audit:\n    stale_after_days: not-a-number\n",
    )
    with pytest.raises(config.ConfigError, match="stale_after_days"):
        config.load_from_repo(tmp_path)


def test_coerce_str_tuple_none_returns_empty(tmp_path):
    # ignore_patterns: null -> None -> _coerce_str_tuple returns ()
    _write(tmp_path / "forerunner.config.yaml", "ignore_patterns: null\n")
    cfg = config.load_from_repo(tmp_path)
    assert cfg.ignore_patterns == ()


def test_approaching_eol_threshold_not_int_raises(tmp_path):
    _write(
        tmp_path / "forerunner.config.yaml",
        "approaching_eol_threshold_months: not-a-number\n",
    )
    with pytest.raises(config.ConfigError, match="approaching_eol_threshold_months"):
        config.load_from_repo(tmp_path)


def test_example_file_is_valid():
    """The committed example must round-trip through the loader."""
    repo = Path(__file__).resolve().parents[1]
    example = repo / "forerunner.config.yaml.example"
    cfg = config.load(example)
    assert cfg.check.block_on
    assert cfg.approaching_eol_threshold_months > 0
