"""Structured logging utilities for codeforerunner."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, TextIO

LOGGER_NAMESPACE = "codeforerunner"

_LOGGER = logging.getLogger(__name__)
_LOG_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)


class StructuredLogFormatter(logging.Formatter):
    """Format log records as compact JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _LOG_RECORD_FIELDS and key not in {"message", "asctime"}
        }
        if extra_fields:
            if set(extra_fields) == {"context"} and isinstance(extra_fields["context"], Mapping):
                payload["context"] = _json_safe(extra_fields["context"])
            else:
                payload["context"] = _json_safe(extra_fields)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def configure_logging(
    *,
    level: int | str = logging.INFO,
    stream: TextIO | None = None,
) -> logging.Logger:
    """Configure and return the package logger."""

    logger = logging.getLogger(LOGGER_NAMESPACE)
    for handler in logger.handlers:
        try:
            handler.flush()
            handler.close()
        except (OSError, IOError) as exc:
            _LOGGER.warning(
                "failed flushing/closing logging handler %r (%s.%s): %s",
                handler,
                type(handler).__module__,
                type(handler).__qualname__,
                exc,
            )
    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = False

    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(StructuredLogFormatter())
    logger.addHandler(handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger within the package namespace."""

    if name is None or name == LOGGER_NAMESPACE:
        return logging.getLogger(LOGGER_NAMESPACE)

    if name.startswith(f"{LOGGER_NAMESPACE}."):
        return logging.getLogger(name)

    return logging.getLogger(f"{LOGGER_NAMESPACE}.{name}")


def log_context(**values: Any) -> dict[str, dict[str, Any]]:
    """Build a logging extra payload for structured context fields."""

    return {"context": _json_safe(values)}


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value

    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}

    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]

    if isinstance(value, set | frozenset):
        ordered = sorted(value, key=repr)
        return [_json_safe(item) for item in ordered]

    return repr(value)
