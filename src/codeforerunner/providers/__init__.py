"""Provider registry. See SPEC.md §T38."""

from __future__ import annotations

from codeforerunner.providers.anthropic import AnthropicProvider
from codeforerunner.providers.base import CompletionResult, Provider, ProviderError
from codeforerunner.providers.google import GoogleProvider
from codeforerunner.providers.ollama import OllamaProvider
from codeforerunner.providers.openai import OpenAIProvider

__all__ = [
    "AnthropicProvider",
    "CompletionResult",
    "GoogleProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "Provider",
    "ProviderError",
    "REGISTRY",
    "get",
]

REGISTRY: dict[str, type] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "google": GoogleProvider,
    "ollama": OllamaProvider,
}


def get(name: str) -> type:
    if name not in REGISTRY:
        raise ProviderError(
            f"unknown provider '{name}' (expected one of {sorted(REGISTRY)})"
        )
    return REGISTRY[name]
