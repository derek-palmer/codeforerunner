"""Configuration loading and validation for codeforerunner."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILENAME = "forerunner.config.yaml"


@dataclass(frozen=True)
class AdapterConfig:
    provider: str = "local"


@dataclass(frozen=True)
class DocsConfig:
    readme: str = "README.md"
    api_dir: str = "docs/api"
    diagrams_dir: str = "docs/diagrams"
    flows_dir: str = "docs/flows"


@dataclass(frozen=True)
class EnforcementConfig:
    strict: bool = True


@dataclass(frozen=True)
class ForerunnerConfig:
    include: tuple[str, ...] = ("src/", "app/")
    exclude: tuple[str, ...] = ("tests/", "node_modules/")
    adapters: AdapterConfig = field(default_factory=AdapterConfig)
    docs: DocsConfig = field(default_factory=DocsConfig)
    enforcement: EnforcementConfig = field(default_factory=EnforcementConfig)


class ConfigError(ValueError):
    """Raised when a configuration file cannot be loaded or validated."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)

    def __str__(self) -> str:
        if self.field is None:
            return f"Invalid configuration: {self.args[0]}"
        return f"Invalid configuration field '{self.field}': {self.args[0]}"


def load_config(repo_root: str | Path) -> ForerunnerConfig:
    """Load config from a repository root, returning defaults when absent."""

    config_path = Path(repo_root) / CONFIG_FILENAME
    if not config_path.exists():
        return ForerunnerConfig()

    try:
        raw_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"could not parse YAML: {exc}") from exc

    if raw_config is None:
        return ForerunnerConfig()

    return parse_config(raw_config)


def parse_config(raw_config: Any) -> ForerunnerConfig:
    """Validate raw config data and return the typed config model."""

    if not isinstance(raw_config, dict):
        raise ConfigError("expected a mapping at the top level")

    allowed_top_level = {"include", "exclude", "adapters", "docs", "enforcement"}
    _reject_unknown_fields(raw_config, allowed_top_level)

    defaults = ForerunnerConfig()

    return ForerunnerConfig(
        include=_string_tuple(raw_config.get("include", defaults.include), field_name="include"),
        exclude=_string_tuple(raw_config.get("exclude", defaults.exclude), field_name="exclude"),
        adapters=_adapter_config(raw_config.get("adapters", {}), defaults.adapters),
        docs=_docs_config(raw_config.get("docs", {}), defaults.docs),
        enforcement=_enforcement_config(
            raw_config.get("enforcement", {}),
            defaults.enforcement,
        ),
    )


def _adapter_config(raw_config: Any, defaults: AdapterConfig) -> AdapterConfig:
    config = _mapping(raw_config, field_name="adapters")
    _reject_unknown_fields(config, {"provider"}, prefix="adapters")

    provider = config.get("provider", defaults.provider)
    if not isinstance(provider, str):
        raise ConfigError("expected a string", field="adapters.provider")

    return AdapterConfig(provider=provider)


def _docs_config(raw_config: Any, defaults: DocsConfig) -> DocsConfig:
    config = _mapping(raw_config, field_name="docs")
    _reject_unknown_fields(
        config,
        {"readme", "api_dir", "diagrams_dir", "flows_dir"},
        prefix="docs",
    )

    return DocsConfig(
        readme=_string_value(config.get("readme", defaults.readme), field_name="docs.readme"),
        api_dir=_string_value(config.get("api_dir", defaults.api_dir), field_name="docs.api_dir"),
        diagrams_dir=_string_value(
            config.get("diagrams_dir", defaults.diagrams_dir),
            field_name="docs.diagrams_dir",
        ),
        flows_dir=_string_value(
            config.get("flows_dir", defaults.flows_dir),
            field_name="docs.flows_dir",
        ),
    )


def _enforcement_config(raw_config: Any, defaults: EnforcementConfig) -> EnforcementConfig:
    config = _mapping(raw_config, field_name="enforcement")
    _reject_unknown_fields(config, {"strict"}, prefix="enforcement")

    strict = config.get("strict", defaults.strict)
    if not isinstance(strict, bool):
        raise ConfigError("expected a boolean", field="enforcement.strict")

    return EnforcementConfig(strict=strict)


def _mapping(raw_config: Any, *, field_name: str) -> dict[str, Any]:
    if not isinstance(raw_config, dict):
        raise ConfigError("expected a mapping", field=field_name)

    return raw_config


def _reject_unknown_fields(
    raw_config: dict[Any, Any],
    allowed_fields: set[str],
    *,
    prefix: str | None = None,
) -> None:
    for field_name in raw_config:
        if field_name not in allowed_fields:
            field_path = str(field_name) if prefix is None else f"{prefix}.{field_name}"
            raise ConfigError("unknown field", field=field_path)


def _string_tuple(raw_value: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(raw_value, list | tuple):
        raise ConfigError("expected a list of strings", field=field_name)

    for index, item in enumerate(raw_value):
        if not isinstance(item, str):
            raise ConfigError("expected a string", field=f"{field_name}.{index}")

    return tuple(raw_value)


def _string_value(raw_value: Any, *, field_name: str) -> str:
    if not isinstance(raw_value, str):
        raise ConfigError("expected a string", field=field_name)

    return raw_value
