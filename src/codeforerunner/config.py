"""`forerunner.config.yaml` schema + loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILENAME = "forerunner.config.yaml"

_KNOWN_SEVERITIES = {"HIGH", "MEDIUM", "LOW"}


class ConfigError(Exception):
    """Schema violation in forerunner.config.yaml."""


@dataclass(frozen=True)
class CheckConfig:
    """Drift-check task configuration: severity gates and path filters."""

    block_on: tuple[str, ...] = ("HIGH", "MEDIUM")
    warn_on: tuple[str, ...] = ("LOW",)
    enabled_rules: tuple[str, ...] | None = None  # None = all rules enabled
    ignore_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class VersionAuditConfig:
    """Version-audit task configuration: staleness window and live EOL data toggle."""

    enabled: bool = True
    stale_after_days: int = 30
    fetch_live_eol_data: bool = False


@dataclass(frozen=True)
class ForerunnerConfig:
    """Top-level forerunner.config.yaml configuration."""

    approaching_eol_threshold_months: int = 6
    ignore_patterns: tuple[str, ...] = ()
    check: CheckConfig = field(default_factory=CheckConfig)
    version_audit: VersionAuditConfig = field(default_factory=VersionAuditConfig)


def _require_type(value: Any, expected: type, field_name: str) -> Any:
    """Raise ConfigError if value is not an instance of expected."""
    if not isinstance(value, expected):
        raise ConfigError(
            f"{field_name}: expected {expected.__name__}, got {type(value).__name__}"
        )
    return value


def _coerce_str_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    """Coerce a list of strings to a tuple, raising ConfigError on bad input."""
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ConfigError(f"{field_name}: expected list, got {type(value).__name__}")
    out: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ConfigError(f"{field_name}[{i}]: expected string, got {type(item).__name__}")
        out.append(item)
    return tuple(out)


def _parse_check(raw: Any) -> CheckConfig:
    """Parse the tasks.check mapping into a CheckConfig."""
    if raw is None:
        return CheckConfig()
    _require_type(raw, dict, "tasks.check")
    block_on = _coerce_str_tuple(raw.get("block_on", ["HIGH", "MEDIUM"]), "tasks.check.block_on")
    warn_on = _coerce_str_tuple(raw.get("warn_on", ["LOW"]), "tasks.check.warn_on")
    for sev in (*block_on, *warn_on):
        if sev not in _KNOWN_SEVERITIES:
            raise ConfigError(
                f"tasks.check: unknown severity '{sev}' (expected one of {sorted(_KNOWN_SEVERITIES)})"
            )
    enabled_rules_raw = raw.get("enabled_rules")
    enabled_rules = (
        _coerce_str_tuple(enabled_rules_raw, "tasks.check.enabled_rules")
        if enabled_rules_raw is not None
        else None
    )
    ignore_paths = _coerce_str_tuple(raw.get("ignore_paths", []), "tasks.check.ignore_paths")
    return CheckConfig(
        block_on=block_on,
        warn_on=warn_on,
        enabled_rules=enabled_rules,
        ignore_paths=ignore_paths,
    )


def _to_int(value: Any, field_name: str) -> int:
    """Convert value to int, raising ConfigError on failure."""
    try:
        return int(value)
    except (TypeError, ValueError) as e:
        raise ConfigError(f"{field_name}: expected integer, got {value!r}") from e


def _parse_version_audit(raw: Any) -> VersionAuditConfig:
    """Parse the tasks.version_audit mapping into a VersionAuditConfig."""
    if raw is None:
        return VersionAuditConfig()
    _require_type(raw, dict, "tasks.version_audit")
    return VersionAuditConfig(
        enabled=bool(raw.get("enabled", True)),
        stale_after_days=_to_int(raw.get("stale_after_days", 30), "tasks.version_audit.stale_after_days"),
        fetch_live_eol_data=bool(raw.get("fetch_live_eol_data", False)),
    )


def parse(raw: dict[str, Any] | None) -> ForerunnerConfig:
    """Validate a parsed YAML mapping into a ForerunnerConfig."""
    if raw is None:
        return ForerunnerConfig()
    _require_type(raw, dict, "<root>")

    tasks_raw = raw.get("tasks")
    tasks = tasks_raw if tasks_raw is not None else {}
    _require_type(tasks, dict, "tasks")

    eol_months = _to_int(
        raw.get("approaching_eol_threshold_months", 6), "approaching_eol_threshold_months"
    )
    if eol_months <= 0:
        raise ConfigError(
            f"approaching_eol_threshold_months: must be a positive integer, got {eol_months}"
        )

    return ForerunnerConfig(
        approaching_eol_threshold_months=eol_months,
        ignore_patterns=_coerce_str_tuple(raw.get("ignore_patterns", []), "ignore_patterns"),
        check=_parse_check(tasks.get("check")),
        version_audit=_parse_version_audit(tasks.get("version_audit")),
    )


def load(path: Path) -> ForerunnerConfig:
    """Load and validate a config file. Empty file = all defaults."""
    text = path.read_text(encoding="utf-8")
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ConfigError(f"{path}: invalid YAML: {e}") from e
    return parse(raw)


def load_from_repo(repo: Path) -> ForerunnerConfig | None:
    """Return parsed config when `forerunner.config.yaml` is present, else None."""
    p = repo / CONFIG_FILENAME
    if not p.is_file():
        return None
    return load(p)
