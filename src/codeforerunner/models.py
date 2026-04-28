"""Shared domain models for repository analysis and documentation generation."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceLocation:
    path: str
    line: int | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.path, field_name="path")
        if self.line is not None:
            if type(self.line) is not int:
                raise TypeError("line must be an integer")
            if self.line < 1:
                raise ValueError("line must be a positive integer")

    def to_dict(self) -> dict[str, Any]:
        return _to_serializable_dict(self)


@dataclass(frozen=True)
class StackArea:
    id: str
    name: str
    kind: str
    root_path: str
    technologies: tuple[str, ...] = ()
    entrypoints: tuple[str, ...] = ()
    markers: tuple[SourceLocation, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_string(self.id, field_name="id")
        _require_non_empty_string(self.name, field_name="name")
        _require_non_empty_string(self.kind, field_name="kind")
        _require_non_empty_string(self.root_path, field_name="root_path")
        _normalize_tuple(self, "technologies")
        _normalize_tuple(self, "entrypoints")
        _normalize_tuple(self, "markers")

    def to_dict(self) -> dict[str, Any]:
        return _to_serializable_dict(self)


@dataclass(frozen=True)
class Entity:
    name: str
    kind: str
    location: SourceLocation
    stack_id: str | None = None
    signature: str | None = None
    summary: str | None = None
    is_public: bool = True

    def __post_init__(self) -> None:
        _require_non_empty_string(self.name, field_name="name")
        _require_non_empty_string(self.kind, field_name="kind")
        if self.stack_id is not None:
            _require_non_empty_string(self.stack_id, field_name="stack_id")
        if self.signature is not None:
            _require_non_empty_string(self.signature, field_name="signature")
        if self.summary is not None:
            _require_non_empty_string(self.summary, field_name="summary")

    def to_dict(self) -> dict[str, Any]:
        return _to_serializable_dict(self)


@dataclass(frozen=True)
class IntegrationHint:
    name: str
    kind: str
    source: str
    target: str | None = None
    evidence: tuple[SourceLocation, ...] = ()
    summary: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.name, field_name="name")
        _require_non_empty_string(self.kind, field_name="kind")
        _require_non_empty_string(self.source, field_name="source")
        if self.target is not None:
            _require_non_empty_string(self.target, field_name="target")
        if self.summary is not None:
            _require_non_empty_string(self.summary, field_name="summary")
        _normalize_tuple(self, "evidence")

    def to_dict(self) -> dict[str, Any]:
        return _to_serializable_dict(self)


@dataclass(frozen=True)
class RepositoryModel:
    root_path: str
    stacks: tuple[StackArea, ...] = ()
    entities: tuple[Entity, ...] = ()
    integrations: tuple[IntegrationHint, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_string(self.root_path, field_name="root_path")
        _normalize_tuple(self, "stacks")
        _normalize_tuple(self, "entities")
        _normalize_tuple(self, "integrations")

    @property
    def root_name(self) -> str:
        return Path(self.root_path).name

    def to_dict(self) -> dict[str, Any]:
        return _to_serializable_dict(self)


@dataclass(frozen=True)
class GenerationResult:
    artifact_path: str
    content: str
    sources: tuple[SourceLocation, ...] = ()
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_string(self.artifact_path, field_name="artifact_path")
        _require_string(self.content, field_name="content")
        _normalize_tuple(self, "sources")
        _normalize_tuple(self, "limitations")

    def to_dict(self) -> dict[str, Any]:
        return _to_serializable_dict(self)


def _to_serializable_dict(instance: object) -> dict[str, Any]:
    return {
        field.name: _to_serializable_value(getattr(instance, field.name))
        for field in fields(instance)
    }


def _to_serializable_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return _to_serializable_dict(value)

    if isinstance(value, list | tuple):
        return [_to_serializable_value(item) for item in value]

    if isinstance(value, dict):
        return {
            _to_serializable_value(key): _to_serializable_value(item) for key, item in value.items()
        }

    return value


def _normalize_tuple(instance: object, field_name: str) -> None:
    value = getattr(instance, field_name)
    if isinstance(value, tuple):
        return

    if isinstance(value, list):
        object.__setattr__(instance, field_name, tuple(value))
        return

    raise TypeError(f"{field_name} must be a tuple or list")


def _require_string(value: object, *, field_name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")


def _require_non_empty_string(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
