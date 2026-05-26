"""Provider protocol + shared types. See SPEC.md §T38."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol


@dataclass(frozen=True)
class CompletionResult:
    """Completed text response returned by a provider."""

    text: str
    model: str
    usage: dict | None = None  # provider-reported token counts; None if unknown


class Provider(Protocol):
    """Structural protocol that all LLM provider classes must satisfy."""

    name: str
    default_env_var: str  # e.g. "ANTHROPIC_API_KEY"
    default_model: str  # provider's recommended default

    def generate(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> CompletionResult:
        """Send *prompt* and return the full completion result."""
        ...

    def stream(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> Iterator[str]:
        """Yield text chunks from *prompt* as they arrive from the provider."""
        ...


class ProviderError(Exception):
    """Raised on provider HTTP failures, missing keys, or malformed responses."""
