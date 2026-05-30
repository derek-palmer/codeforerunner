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


class OutcomeKind(Enum):
    ALLOWED = auto()
    UNKNOWN_TASK = auto()
    SCAN_REQUIRED = auto()
    MISSING = auto()


@dataclass(frozen=True)
class Outcome:
    """Closed result of resolving a task end-to-end: gate + bundle in one.

    Adapters encode this into their surface (exit codes for CLI, JSON-RPC for
    MCP) without re-deriving the branch order. ``text`` is set only for
    ``ALLOWED``; ``message`` carries the human/error detail otherwise.
    """

    kind: OutcomeKind
    text: str | None = None
    task: tasks.Task | None = None
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

    def resolve(self, name: str) -> Outcome:
        """Gate *name* and, if allowed, resolve its bundle — as one closed Outcome.

        Owns the branch order (unknown → scan-gate → bundle) so adapters only
        encode the result. Scan-state signal sourcing stays with the adapter
        (it injects ``scan_satisfied``); see docs/adr/0001.
        """
        decision = self.can_run(name)
        if not decision.allowed:
            if decision.reason is Denial.UNKNOWN_TASK:
                return Outcome(OutcomeKind.UNKNOWN_TASK, message=decision.message)
            return Outcome(OutcomeKind.SCAN_REQUIRED, task=decision.task, message=decision.message)
        try:
            text = self.bundle_for(name)
        except FileNotFoundError as e:
            return Outcome(OutcomeKind.MISSING, task=decision.task, message=str(e))
        return Outcome(OutcomeKind.ALLOWED, text=text, task=decision.task)
