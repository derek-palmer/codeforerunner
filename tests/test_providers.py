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
