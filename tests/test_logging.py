"""Tests for structured logging utilities."""

from __future__ import annotations

import io
import json

from codeforerunner.logging import configure_logging, get_logger, log_context


def test_configure_logging_writes_json_records() -> None:
    stream = io.StringIO()
    logger = configure_logging(stream=stream)

    logger.info("scan complete", extra=log_context(repo="example", files=3))

    payload = json.loads(stream.getvalue())

    assert payload["level"] == "INFO"
    assert payload["logger"] == "codeforerunner"
    assert payload["message"] == "scan complete"
    assert payload["context"] == {"files": 3, "repo": "example"}
    assert "timestamp" in payload


def test_get_logger_scopes_names_to_package_namespace() -> None:
    assert get_logger().name == "codeforerunner"
    assert get_logger("scanner").name == "codeforerunner.scanner"
    assert get_logger("codeforerunner.generator").name == "codeforerunner.generator"


def test_log_context_serializes_non_json_values() -> None:
    stream = io.StringIO()
    logger = configure_logging(stream=stream)

    logger.info("loaded config", extra=log_context(paths={"include": ("src/",)}, marker=object()))

    payload = json.loads(stream.getvalue())

    assert payload["context"]["paths"] == {"include": ["src/"]}
    assert payload["context"]["marker"].startswith("<object object at ")
