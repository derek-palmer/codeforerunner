"""Anthropic Messages API provider. Stdlib HTTP only."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from codeforerunner.providers.base import CompletionResult, ProviderError


class AnthropicProvider:
    name = "anthropic"
    default_env_var = "ANTHROPIC_API_KEY"
    default_model = "claude-opus-4-5"

    endpoint = "https://api.anthropic.com/v1/messages"

    def complete(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> CompletionResult:
        if not api_key:
            raise ProviderError(f"missing API key (set ${self.default_env_var})")
        model = model or self.default_model
        body = json.dumps(
            {
                "model": model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            snippet = (e.read() or b"")[:500].decode("utf-8", errors="replace")
            raise ProviderError(f"HTTP {e.code}: {snippet}") from e
        except urllib.error.URLError as e:
            raise ProviderError(f"network error: {e.reason}") from e
        try:
            data = json.loads(raw.decode("utf-8"))
            text = data["content"][0]["text"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            raise ProviderError(f"malformed response: {e}") from e
        return CompletionResult(
            text=text, model=data.get("model", model), usage=data.get("usage")
        )
