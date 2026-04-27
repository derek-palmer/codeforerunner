"""Tests for forerunner configuration loading."""

from __future__ import annotations

import pytest

from codeforerunner.config import ConfigError, load_config


def test_missing_config_returns_defaults(tmp_path) -> None:
    config = load_config(tmp_path)

    assert config.include == ("src/", "app/")
    assert config.exclude == ("tests/", "node_modules/")
    assert config.adapters.provider == "local"
    assert config.docs.readme == "README.md"
    assert config.docs.api_dir == "docs/api"
    assert config.docs.diagrams_dir == "docs/diagrams"
    assert config.docs.flows_dir == "docs/flows"
    assert config.enforcement.strict is True


def test_empty_or_comment_only_config_returns_defaults(tmp_path) -> None:
    config_path = tmp_path / "forerunner.config.yaml"
    config_path.write_text("# placeholder config\n# add fields later\n", encoding="utf-8")

    config = load_config(tmp_path)

    assert config.include == ("src/", "app/")
    assert config.exclude == ("tests/", "node_modules/")
    assert config.adapters.provider == "local"
    assert config.docs.readme == "README.md"
    assert config.docs.api_dir == "docs/api"
    assert config.docs.diagrams_dir == "docs/diagrams"
    assert config.docs.flows_dir == "docs/flows"
    assert config.enforcement.strict is True


def test_valid_config_overrides_defaults(tmp_path) -> None:
    (tmp_path / "forerunner.config.yaml").write_text(
        """
include:
  - services/
  - web/
exclude:
  - vendor/
adapters:
  provider: openai-compatible
docs:
  readme: docs/index.md
  api_dir: generated/api
  diagrams_dir: generated/diagrams
  flows_dir: generated/flows
enforcement:
  strict: false
""",
        encoding="utf-8",
    )

    config = load_config(tmp_path)

    assert config.include == ("services/", "web/")
    assert config.exclude == ("vendor/",)
    assert config.adapters.provider == "openai-compatible"
    assert config.docs.readme == "docs/index.md"
    assert config.docs.api_dir == "generated/api"
    assert config.docs.diagrams_dir == "generated/diagrams"
    assert config.docs.flows_dir == "generated/flows"
    assert config.enforcement.strict is False


def test_invalid_yaml_reports_parse_error(tmp_path) -> None:
    (tmp_path / "forerunner.config.yaml").write_text("include: [src/", encoding="utf-8")

    with pytest.raises(ConfigError, match="could not parse YAML"):
        load_config(tmp_path)


def test_top_level_config_must_be_mapping(tmp_path) -> None:
    (tmp_path / "forerunner.config.yaml").write_text("- src/\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="expected a mapping at the top level"):
        load_config(tmp_path)


def test_unknown_key_reports_offending_field(tmp_path) -> None:
    (tmp_path / "forerunner.config.yaml").write_text("unknown: true\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="'unknown': unknown field"):
        load_config(tmp_path)


def test_wrong_field_type_reports_offending_field(tmp_path) -> None:
    (tmp_path / "forerunner.config.yaml").write_text("include: src/\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="'include': expected a list of strings"):
        load_config(tmp_path)


def test_nested_wrong_field_type_reports_offending_field(tmp_path) -> None:
    (tmp_path / "forerunner.config.yaml").write_text(
        """
docs:
  api_dir: false
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="'docs.api_dir': expected a string"):
        load_config(tmp_path)
