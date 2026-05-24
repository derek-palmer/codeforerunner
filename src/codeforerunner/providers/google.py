"""Google Gemini generateContent provider. Stdlib HTTP only."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Iterator

from codeforerunner.providers.base import CompletionResult, ProviderError


class GoogleProvider:
    name = "google"
    default_env_var = "GOOGLE_API_KEY"
    default_model = "gemini-2.5-pro"

    endpoint_template = (
        "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    )
    stream_endpoint_template = (
        "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"
        "?key={key}&alt=sse"
    )

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
        url = self.endpoint_template.format(
            model=urllib.parse.quote(model, safe=""),
            key=urllib.parse.quote(api_key, safe=""),
        )
        body = json.dumps(
            {"contents": [{"parts": [{"text": prompt}]}]}
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"content-type": "application/json"},
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
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            raise ProviderError(f"malformed response: {e}") from e
        return CompletionResult(
            text=text,
            model=data.get("modelVersion", model),
            usage=data.get("usageMetadata"),
        )

    def stream(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> Iterator[str]:
        if not api_key:
            raise ProviderError(f"missing API key (set ${self.default_env_var})")
        model = model or self.default_model
        url = self.stream_endpoint_template.format(
            model=urllib.parse.quote(model, safe=""),
            key=urllib.parse.quote(api_key, safe=""),
        )
        body = json.dumps(
            {"contents": [{"parts": [{"text": prompt}]}]}
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={"content-type": "application/json"},
        )
        try:
            resp = urllib.request.urlopen(req)
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
                try:
                    event = json.loads(line[6:])
                    text = event["candidates"][0]["content"]["parts"][0]["text"]
                    if text:
                        yield text
                except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                    continue
        finally:
            resp.close()
