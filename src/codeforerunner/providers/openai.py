"""OpenAI chat completions provider. Stdlib HTTP only."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Iterator

from codeforerunner.providers.base import CompletionResult, ProviderError


class OpenAIProvider:
    """OpenAI chat completions provider using stdlib HTTP."""

    name = "openai"
    default_env_var = "OPENAI_API_KEY"
    default_model = "gpt-4o"

    endpoint = "https://api.openai.com/v1/chat/completions"

    def complete(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> CompletionResult:
        """Send *prompt* to the OpenAI chat completions endpoint and return the full response."""
        if not api_key:
            raise ProviderError(f"missing API key (set ${self.default_env_var})")
        model = model or self.default_model
        body = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
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
            text = data["choices"][0]["message"]["content"]
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
        """Yield text chunks from the OpenAI streaming chat completions endpoint."""
        if not api_key:
            raise ProviderError(f"missing API key (set ${self.default_env_var})")
        model = model or self.default_model
        body = json.dumps(
            {
                "model": model,
                "stream": True,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
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
                choices = event.get("choices", [])
                if choices:
                    text = choices[0].get("delta", {}).get("content")
                    if text:
                        yield text
        finally:
            resp.close()
