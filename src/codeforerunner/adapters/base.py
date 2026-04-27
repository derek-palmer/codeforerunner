"""Base model adapter protocol and orchestration types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from codeforerunner.config import ForerunnerConfig
from codeforerunner.models import RepositoryModel


@dataclass(frozen=True)
class ModelMessage:
    role: str
    content: str

    def __post_init__(self) -> None:
        _require_non_empty_string(self.role, field_name="role")
        _require_non_empty_string(self.content, field_name="content")

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class ModelRequest:
    purpose: str
    messages: tuple[ModelMessage, ...]
    repository: RepositoryModel | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty_string(self.purpose, field_name="purpose")
        _normalize_tuple(self, "messages")
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "purpose": self.purpose,
            "messages": [message.to_dict() for message in self.messages],
            "repository": self.repository.to_dict() if self.repository is not None else None,
            "metadata": _json_safe(self.metadata),
        }


@dataclass(frozen=True)
class ModelResponse:
    content: str
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.content, str):
            raise ValueError("content must be a string")
        if self.model is not None:
            _require_non_empty_string(self.model, field_name="model")
        object.__setattr__(self, "metadata", dict(self.metadata))
        object.__setattr__(self, "usage", dict(self.usage))

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "metadata": _json_safe(self.metadata),
            "usage": _json_safe(self.usage),
        }


@runtime_checkable
class ModelAdapter(Protocol):
    @property
    def name(self) -> str:
        """Human-readable adapter name for logs and diagnostics."""

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate model-backed content for a request."""


@dataclass(frozen=True)
class PipelineContext:
    config: ForerunnerConfig
    adapter: ModelAdapter | None = None


class ModelAdapterUnavailableError(RuntimeError):
    """Raised when an AI-required path is called without a model adapter."""

    def __init__(self, purpose: str) -> None:
        self.purpose = purpose
        super().__init__(f"Model adapter is required for '{purpose}', but no adapter was supplied.")


def require_model_adapter(context: PipelineContext, purpose: str) -> ModelAdapter:
    """Return the configured adapter or fail clearly for AI-required paths."""

    _require_non_empty_string(purpose, field_name="purpose")
    if context.adapter is None:
        raise ModelAdapterUnavailableError(purpose)

    return context.adapter


def _normalize_tuple(instance: object, field_name: str) -> None:
    value = getattr(instance, field_name)
    if isinstance(value, tuple):
        return

    if isinstance(value, list):
        object.__setattr__(instance, field_name, tuple(value))
        return

    raise TypeError(f"{field_name} must be a tuple or list")


def _require_non_empty_string(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value

    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}

    if isinstance(value, list | tuple | set | frozenset):
        return [_json_safe(item) for item in value]

    return repr(value)
