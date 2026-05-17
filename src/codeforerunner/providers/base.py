"""Provider protocol + shared types. See SPEC.md §T38."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CompletionResult:
    text: str
    model: str
    usage: dict | None = None  # provider-reported token counts; None if unknown


class Provider(Protocol):
    name: str
    default_env_var: str  # e.g. "ANTHROPIC_API_KEY"
    default_model: str  # provider's recommended default

    def complete(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> CompletionResult: ...


class ProviderError(Exception):
    """Raised on provider HTTP failures, missing keys, or malformed responses."""
