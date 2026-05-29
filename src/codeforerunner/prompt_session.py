"""Prompt Session — run-scoped owner of task lookup and scan-first enforcement.

CLI and MCP are thin adapters: they construct a session, ask whether a task
can run, and translate the structured Decision into their own surface
(stdout/exit codes for CLI, JSON-RPC for MCP). The session unifies the
scan-first *rule*; each adapter still computes its own scan-satisfied signal
and injects it (see docs/adr/0001).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from codeforerunner import tasks
from codeforerunner.bundle import resolve_bundle


class Denial(Enum):
    UNKNOWN_TASK = auto()
    SCAN_REQUIRED = auto()


@dataclass(frozen=True)
class Decision:
    allowed: bool
    task: tasks.Task | None = None
    reason: Denial | None = None
    message: str | None = None


class PromptSession:
    def __init__(self, prompts_root: Path, scan_satisfied: bool) -> None:
        self._prompts_root = prompts_root
        self._scan_done = scan_satisfied

    def mark_scan_done(self) -> None:
        """Record that scan ran in this session (MCP adapter, after scan tool)."""
        self._scan_done = True

    def can_run(self, name: str) -> Decision:
        try:
            task = tasks.get(name)
        except KeyError:
            return Decision(False, reason=Denial.UNKNOWN_TASK, message=f"unknown task: {name!r}")
        if task.scan_exempt or self._scan_done:
            return Decision(True, task=task)
        return Decision(False, task=task, reason=Denial.SCAN_REQUIRED, message="scan-first required")

    def bundle_for(self, name: str) -> str:
        """Resolve the prompt bundle text for *name*. Call only after can_run allows."""
        return resolve_bundle(self._prompts_root, name)
