"""Tests for the base model adapter interface."""

from __future__ import annotations

import pytest

from codeforerunner.adapters import (
    ModelAdapter,
    ModelAdapterUnavailableError,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    PipelineContext,
    require_model_adapter,
)
from codeforerunner.config import ForerunnerConfig
from codeforerunner.models import RepositoryModel, StackArea


class FakeAdapter:
    def __init__(self) -> None:
        self.received_request: ModelRequest | None = None

    @property
    def name(self) -> str:
        return "fake"

    def generate(self, request: ModelRequest) -> ModelResponse:
        self.received_request = request
        return ModelResponse(
            content="Generated docs",
            model="fake-model",
            metadata={"purpose": request.purpose},
            usage={"input_messages": len(request.messages)},
        )


def test_fake_adapter_satisfies_protocol_and_receives_request() -> None:
    adapter = FakeAdapter()
    request = ModelRequest(
        purpose="readme-summary",
        messages=[ModelMessage(role="user", content="Summarize this repository.")],
    )

    assert isinstance(adapter, ModelAdapter)

    response = adapter.generate(request)

    assert adapter.received_request == request
    assert response.content == "Generated docs"
    assert response.model == "fake-model"
    assert response.metadata == {"purpose": "readme-summary"}
    assert response.usage == {"input_messages": 1}


def test_pipeline_context_allows_no_adapter_for_deterministic_work() -> None:
    context = PipelineContext(config=ForerunnerConfig())

    assert context.config.adapters.provider == "local"
    assert context.adapter is None


def test_require_model_adapter_returns_configured_adapter() -> None:
    adapter = FakeAdapter()
    context = PipelineContext(config=ForerunnerConfig(), adapter=adapter)

    assert require_model_adapter(context, "readme generation") is adapter


def test_require_model_adapter_raises_when_adapter_is_missing() -> None:
    context = PipelineContext(config=ForerunnerConfig())

    with pytest.raises(ModelAdapterUnavailableError, match="readme generation") as exc_info:
        require_model_adapter(context, "readme generation")

    assert exc_info.value.purpose == "readme generation"


def test_model_request_serializes_messages_repository_and_metadata() -> None:
    repository = RepositoryModel(
        root_path="/workspace/example",
        stacks=[StackArea(id="python", name="Python", kind="service", root_path=".")],
    )
    request = ModelRequest(
        purpose="stack-doc",
        messages=[ModelMessage(role="system", content="Write concise docs.")],
        repository=repository,
        metadata={"paths": ("src/",), "opaque": object()},
    )

    assert request.messages == (ModelMessage(role="system", content="Write concise docs."),)
    assert request.to_dict() == {
        "purpose": "stack-doc",
        "messages": [{"role": "system", "content": "Write concise docs."}],
        "repository": repository.to_dict(),
        "metadata": {
            "paths": ["src/"],
            "opaque": repr(request.metadata["opaque"]),
        },
    }


def test_model_response_serializes_metadata_and_usage_defaults() -> None:
    response = ModelResponse(content="", metadata={"paths": ("src/",)}, usage={"tokens": 0})

    assert response.to_dict() == {
        "content": "",
        "model": None,
        "metadata": {"paths": ["src/"]},
        "usage": {"tokens": 0},
    }


@pytest.mark.parametrize(
    ("factory", "expected_error"),
    [
        (lambda: ModelMessage(role="", content="content"), "role must be a non-empty string"),
        (lambda: ModelMessage(role="user", content=""), "content must be a non-empty string"),
        (lambda: ModelRequest(purpose="", messages=[]), "purpose must be a non-empty string"),
        (lambda: ModelRequest(purpose="docs", messages="user"), "messages must be a tuple or list"),
        (lambda: ModelResponse(content=object()), "content must be a string"),
    ],
)
def test_adapter_models_reject_invalid_values(factory, expected_error) -> None:
    with pytest.raises((TypeError, ValueError), match=expected_error):
        factory()
