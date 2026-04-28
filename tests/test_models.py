"""Tests for shared codeforerunner domain models."""

from __future__ import annotations

import pytest

from codeforerunner.models import (
    Entity,
    GenerationResult,
    IntegrationHint,
    RepositoryModel,
    SourceLocation,
    StackArea,
)


def test_repository_model_serializes_shared_analysis_shape() -> None:
    marker = SourceLocation(path="pyproject.toml", line=1)
    stack = StackArea(
        id="python-service",
        name="Python service",
        kind="service",
        root_path=".",
        technologies=["python"],
        entrypoints=["src/codeforerunner/cli.py"],
        markers=[marker],
    )
    entity = Entity(
        name="main",
        kind="function",
        location=SourceLocation(path="src/codeforerunner/cli.py", line=62),
        stack_id=stack.id,
        signature="main(argv: Sequence[str] | None = None) -> int",
    )
    integration = IntegrationHint(
        name="model adapter",
        kind="adapter",
        source=stack.id,
        target="configured-provider",
        evidence=[SourceLocation(path="docs/requirements.md", line=94)],
        summary="Generation will call model providers through adapters.",
    )

    repository = RepositoryModel(
        root_path="/workspace/codeforerunner",
        stacks=[stack],
        entities=[entity],
        integrations=[integration],
    )

    assert repository.root_name == "codeforerunner"
    assert repository.stacks == (stack,)
    assert repository.entities == (entity,)
    assert repository.integrations == (integration,)
    assert repository.to_dict() == {
        "root_path": "/workspace/codeforerunner",
        "stacks": [
            {
                "id": "python-service",
                "name": "Python service",
                "kind": "service",
                "root_path": ".",
                "technologies": ["python"],
                "entrypoints": ["src/codeforerunner/cli.py"],
                "markers": [{"path": "pyproject.toml", "line": 1}],
            }
        ],
        "entities": [
            {
                "name": "main",
                "kind": "function",
                "location": {"path": "src/codeforerunner/cli.py", "line": 62},
                "stack_id": "python-service",
                "signature": "main(argv: Sequence[str] | None = None) -> int",
                "summary": None,
                "is_public": True,
            }
        ],
        "integrations": [
            {
                "name": "model adapter",
                "kind": "adapter",
                "source": "python-service",
                "target": "configured-provider",
                "evidence": [{"path": "docs/requirements.md", "line": 94}],
                "summary": "Generation will call model providers through adapters.",
            }
        ],
    }


def test_generation_result_records_artifact_content_sources_and_limitations() -> None:
    result = GenerationResult(
        artifact_path="docs/api/index.md",
        content="# API\n",
        sources=[SourceLocation(path="src/codeforerunner/cli.py")],
        limitations=["Descriptions are placeholder-only until model adapters exist."],
    )

    assert result.sources == (SourceLocation(path="src/codeforerunner/cli.py"),)
    assert result.limitations == ("Descriptions are placeholder-only until model adapters exist.",)
    assert result.to_dict() == {
        "artifact_path": "docs/api/index.md",
        "content": "# API\n",
        "sources": [{"path": "src/codeforerunner/cli.py", "line": None}],
        "limitations": ["Descriptions are placeholder-only until model adapters exist."],
    }


@pytest.mark.parametrize(
    ("model_factory", "expected_error"),
    [
        (lambda: SourceLocation(path=""), "path must be a non-empty string"),
        (lambda: SourceLocation(path="src/app.py", line=0), "line must be a positive integer"),
        (
            lambda: StackArea(id="", name="App", kind="service", root_path="."),
            "id must be a non-empty string",
        ),
        (
            lambda: RepositoryModel(root_path=".", stacks="python"),
            "stacks must be a tuple or list",
        ),
        (
            lambda: GenerationResult(
                artifact_path="docs/out.md",
                content=123,  # type: ignore[arg-type]
            ),
            "content must be a string",
        ),
    ],
)
def test_models_reject_invalid_required_fields(model_factory, expected_error) -> None:
    with pytest.raises((TypeError, ValueError), match=expected_error):
        model_factory()
