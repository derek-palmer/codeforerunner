"""Anthropic Messages API provider. Stdlib HTTP only."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Iterator

from codeforerunner.providers.base import CompletionResult, ProviderError


class AnthropicProvider:
    """Anthropic Messages API provider using stdlib HTTP."""

    name = "anthropic"
    default_env_var = "ANTHROPIC_API_KEY"
    default_model = "claude-opus-4-7"

    endpoint = "https://api.anthropic.com/v1/messages"

    def generate(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> CompletionResult:
        """Send *prompt* to the Anthropic Messages API and return the full response."""
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
            with urllib.request.urlopen(req, timeout=120) as resp:
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

    def stream(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> Iterator[str]:
        """Yield text chunks from the Anthropic streaming Messages API."""
        if not api_key:
            raise ProviderError(f"missing API key (set ${self.default_env_var})")
        model = model or self.default_model
        body = json.dumps(
            {
                "model": model,
                "max_tokens": 4096,
                "stream": True,
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
            resp = urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as e:
            snippet = (e.read() or b"")[:500].decode("utf-8", errors="replace")
            raise ProviderError(f"HTTP {e.code}: {snippet}") from e
        except urllib.error.URLError as e:
            raise ProviderError(f"network error: {e.reason}") from e
        try:
            for raw_line in resp:
                line = raw_line.decode("utf-8").rstrip("\n")
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    event = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        if text:
                            yield text
        finally:
            resp.close()
