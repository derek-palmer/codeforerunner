from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

import pytest

from codeforerunner import providers
from codeforerunner.providers import (
    AnthropicProvider,
    GoogleProvider,
    OllamaProvider,
    OpenAIProvider,
    ProviderError,
)


def _fake_urlopen(response_body: dict, captured: dict):
    """Return a context-manager mock and stash the outbound request in `captured`."""

    def _opener(req, *args, **kwargs):
        captured["url"] = req.full_url
        captured["headers"] = dict(req.header_items())
        captured["body"] = json.loads(req.data.decode("utf-8")) if req.data else None
        cm = MagicMock()
        cm.__enter__.return_value.read.return_value = json.dumps(response_body).encode("utf-8")
        cm.__exit__.return_value = False
        return cm

    return _opener


def test_registry_contains_four_providers():
    assert set(providers.REGISTRY.keys()) == {"anthropic", "openai", "google", "ollama"}


def test_get_unknown_raises():
    with pytest.raises(ProviderError):
        providers.get("xyz")


def test_get_returns_class():
    assert providers.get("anthropic") is AnthropicProvider


def test_anthropic_builds_request_correctly():
    captured: dict = {}
    fake = {
        "content": [{"text": "hello world"}],
        "model": "claude-opus-4-5",
        "usage": {"input_tokens": 5, "output_tokens": 2},
    }
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = AnthropicProvider().complete(prompt="hi", api_key="sk-test")
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    # urllib lowercases header names via header_items keys preservation; compare case-insensitively.
    lower = {k.lower(): v for k, v in captured["headers"].items()}
    assert lower["x-api-key"] == "sk-test"
    assert lower["anthropic-version"] == "2023-06-01"
    assert lower["content-type"] == "application/json"
    assert captured["body"]["model"] == "claude-opus-4-5"
    assert captured["body"]["max_tokens"] == 4096
    assert captured["body"]["messages"] == [{"role": "user", "content": "hi"}]
    assert result.text == "hello world"
    assert result.model == "claude-opus-4-5"
    assert result.usage == {"input_tokens": 5, "output_tokens": 2}


def test_anthropic_missing_api_key_raises():
    with pytest.raises(ProviderError):
        AnthropicProvider().complete(prompt="hi", api_key=None)


def test_openai_builds_request_correctly():
    captured: dict = {}
    fake = {
        "choices": [{"message": {"content": "hi there"}}],
        "model": "gpt-4o",
        "usage": {"prompt_tokens": 3, "completion_tokens": 2},
    }
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = OpenAIProvider().complete(prompt="ping", api_key="sk-openai")
    assert captured["url"] == "https://api.openai.com/v1/chat/completions"
    lower = {k.lower(): v for k, v in captured["headers"].items()}
    assert lower["authorization"] == "Bearer sk-openai"
    assert lower["content-type"] == "application/json"
    assert captured["body"]["model"] == "gpt-4o"
    assert captured["body"]["messages"] == [{"role": "user", "content": "ping"}]
    assert result.text == "hi there"
    assert result.usage == {"prompt_tokens": 3, "completion_tokens": 2}


def test_openai_missing_api_key_raises():
    with pytest.raises(ProviderError):
        OpenAIProvider().complete(prompt="hi", api_key=None)


def test_google_builds_request_correctly():
    captured: dict = {}
    fake = {
        "candidates": [
            {"content": {"parts": [{"text": "gemini reply"}]}}
        ],
        "modelVersion": "gemini-2.5-pro",
    }
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = GoogleProvider().complete(prompt="q", api_key="g-key")
    assert "generativelanguage.googleapis.com" in captured["url"]
    assert "gemini-2.5-pro:generateContent" in captured["url"]
    assert "key=g-key" in captured["url"]
    assert captured["body"] == {"contents": [{"parts": [{"text": "q"}]}]}
    assert result.text == "gemini reply"


def test_google_missing_api_key_raises():
    with pytest.raises(ProviderError):
        GoogleProvider().complete(prompt="hi", api_key=None)


def test_ollama_builds_request_correctly_with_default_host(monkeypatch):
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    captured: dict = {}
    fake = {"response": "local response", "model": "llama3"}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = OllamaProvider().complete(prompt="hello")
    assert captured["url"] == "http://localhost:11434/api/generate"
    assert captured["body"] == {"model": "llama3", "prompt": "hello", "stream": False}
    assert result.text == "local response"
    assert result.model == "llama3"


def test_ollama_respects_host_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://other:9999")
    captured: dict = {}
    fake = {"response": "x"}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        OllamaProvider().complete(prompt="hi")
    assert captured["url"] == "http://other:9999/api/generate"


def test_anthropic_malformed_response_raises():
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen({"bogus": True}, captured)):
        with pytest.raises(ProviderError):
            AnthropicProvider().complete(prompt="hi", api_key="sk")


def _fake_http_error(code: int):
    import urllib.error

    def _opener(req, *args, **kwargs):
        err = urllib.error.HTTPError(
            url=req.full_url, code=code, msg="err", hdrs=None, fp=io.BytesIO(b"details")
        )
        raise err

    return _opener


def _fake_url_error():
    import urllib.error

    def _opener(req, *args, **kwargs):
        raise urllib.error.URLError("connection refused")

    return _opener


# --- Anthropic HTTP/network errors ---

def test_anthropic_http_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_http_error(401)):
        with pytest.raises(ProviderError, match="HTTP 401"):
            AnthropicProvider().complete(prompt="hi", api_key="sk")


def test_anthropic_url_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_url_error()):
        with pytest.raises(ProviderError, match="network error"):
            AnthropicProvider().complete(prompt="hi", api_key="sk")


def test_anthropic_uses_default_model_when_none():
    fake = {"content": [{"text": "ok"}], "model": AnthropicProvider.default_model}
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = AnthropicProvider().complete(prompt="hi", model=None, api_key="sk")
    assert captured["body"]["model"] == AnthropicProvider.default_model
    assert result.model == AnthropicProvider.default_model


# --- OpenAI ---

def test_openai_malformed_response_raises():
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen({"bad": True}, captured)):
        with pytest.raises(ProviderError):
            OpenAIProvider().complete(prompt="hi", api_key="sk")


def test_openai_http_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_http_error(429)):
        with pytest.raises(ProviderError, match="HTTP 429"):
            OpenAIProvider().complete(prompt="hi", api_key="sk")


def test_openai_url_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_url_error()):
        with pytest.raises(ProviderError, match="network error"):
            OpenAIProvider().complete(prompt="hi", api_key="sk")


def test_openai_uses_default_model_when_none():
    fake = {
        "choices": [{"message": {"content": "reply"}}],
        "model": OpenAIProvider.default_model,
    }
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = OpenAIProvider().complete(prompt="hi", model=None, api_key="sk")
    assert captured["body"]["model"] == OpenAIProvider.default_model
    assert result.model == OpenAIProvider.default_model


# --- Google ---

def test_google_malformed_response_raises():
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen({"bad": True}, captured)):
        with pytest.raises(ProviderError):
            GoogleProvider().complete(prompt="hi", api_key="g-key")


def test_google_http_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_http_error(403)):
        with pytest.raises(ProviderError, match="HTTP 403"):
            GoogleProvider().complete(prompt="hi", api_key="g-key")


def test_google_url_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_url_error()):
        with pytest.raises(ProviderError, match="network error"):
            GoogleProvider().complete(prompt="hi", api_key="g-key")


def test_google_falls_back_to_model_when_modelversion_absent():
    fake = {"candidates": [{"content": {"parts": [{"text": "reply"}]}}]}
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = GoogleProvider().complete(prompt="hi", model="gemini-test", api_key="k")
    assert result.model == "gemini-test"


# --- Ollama ---

def test_ollama_malformed_response_raises():
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen({"bad": True}, captured)):
        with pytest.raises(ProviderError):
            OllamaProvider().complete(prompt="hi")


def test_ollama_http_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_http_error(500)):
        with pytest.raises(ProviderError, match="HTTP 500"):
            OllamaProvider().complete(prompt="hi")


def test_ollama_url_error_raises():
    with patch("urllib.request.urlopen", side_effect=_fake_url_error()):
        with pytest.raises(ProviderError, match="network error"):
            OllamaProvider().complete(prompt="hi")


def test_ollama_usage_extracted_when_present():
    fake = {
        "response": "text",
        "model": "llama3",
        "prompt_eval_count": 10,
        "eval_count": 5,
        "total_duration": 123456789,
    }
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = OllamaProvider().complete(prompt="hi")
    assert result.usage == {"prompt_eval_count": 10, "eval_count": 5, "total_duration": 123456789}


def test_ollama_usage_none_when_keys_absent():
    fake = {"response": "text", "model": "llama3"}
    captured: dict = {}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        result = OllamaProvider().complete(prompt="hi")
    assert result.usage is None


def test_ollama_api_key_used_as_base_url(monkeypatch):
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    captured: dict = {}
    fake = {"response": "ok", "model": "llama3"}
    with patch("urllib.request.urlopen", side_effect=_fake_urlopen(fake, captured)):
        OllamaProvider().complete(prompt="hi", api_key="http://custom:8888")
    assert captured["url"] == "http://custom:8888/api/generate"
