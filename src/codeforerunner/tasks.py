"""Task Registry — single source of truth for task identity and policy."""

from __future__ import annotations

import importlib.resources
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    name: str
    scan_exempt: bool
    skill_slug: str | None


def _load() -> tuple[list[Task], list[str], str]:
    """Load and parse tasks.json. Returns (tasks, refresh_sequence, canonical_skill_slug)."""
    data = json.loads(
        importlib.resources.files("codeforerunner").joinpath("tasks.json").read_text(encoding="utf-8")
    )
    task_list = [
        Task(
            name=entry["name"],
            scan_exempt=entry["scan_exempt"],
            skill_slug=entry.get("skill_slug"),
        )
        for entry in data["tasks"]
    ]
    return task_list, data["refresh_sequence"], data["canonical_skill_slug"]


_TASKS, _REFRESH_SEQUENCE, _CANONICAL_SLUG = _load()
_BY_NAME: dict[str, Task] = {t.name: t for t in _TASKS}


def all_tasks() -> list[Task]:
    return list(_TASKS)


def get(name: str) -> Task:
    try:
        return _BY_NAME[name]
    except KeyError:
        raise KeyError(f"unknown task: {name!r}") from None


def refresh_tasks() -> list[Task]:
    return [_BY_NAME[name] for name in _REFRESH_SEQUENCE]


def scan_exempt_names() -> frozenset[str]:
    return frozenset(t.name for t in _TASKS if t.scan_exempt)


def installable_slugs() -> tuple[str, ...]:
    slugs = [_CANONICAL_SLUG]
    slugs.extend(t.skill_slug for t in _TASKS if t.skill_slug and t.skill_slug != _CANONICAL_SLUG)
    return tuple(slugs)
