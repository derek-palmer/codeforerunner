"""Ollama local provider. Stdlib HTTP only."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Iterator

from codeforerunner.providers.base import CompletionResult, ProviderError

DEFAULT_HOST = "http://localhost:11434"


def is_available(host: str | None = None) -> bool:
    """Return True if an Ollama instance is reachable at the configured host."""
    base = (host or os.environ.get("OLLAMA_HOST") or DEFAULT_HOST).rstrip("/")
    try:
        urllib.request.urlopen(f"{base}/api/tags", timeout=2)
        return True
    except Exception:
        return False


class OllamaProvider:
    name = "ollama"
    default_env_var = "OLLAMA_HOST"
    default_model = "llama3"

    def complete(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> CompletionResult:
        # api_key is interpreted as a base URL override; fall back to env then default.
        base = api_key or os.environ.get(self.default_env_var) or DEFAULT_HOST
        base = base.rstrip("/")
        model = model or self.default_model
        url = f"{base}/api/generate"
        body = json.dumps(
            {"model": model, "prompt": prompt, "stream": False}
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
            text = data["response"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ProviderError(f"malformed response: {e}") from e
        usage_keys = ("prompt_eval_count", "eval_count", "total_duration")
        usage = {k: data[k] for k in usage_keys if k in data} or None
        return CompletionResult(text=text, model=data.get("model", model), usage=usage)

    def stream(
        self,
        *,
        prompt: str,
        model: str | None = None,
        api_key: str | None = None,
    ) -> Iterator[str]:
        base = api_key or os.environ.get(self.default_env_var) or DEFAULT_HOST
        base = base.rstrip("/")
        model = model or self.default_model
        url = f"{base}/api/generate"
        body = json.dumps(
            {"model": model, "prompt": prompt, "stream": True}
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
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = event.get("response", "")
                if text:
                    yield text
                if event.get("done", False):
                    break
        finally:
            resp.close()
