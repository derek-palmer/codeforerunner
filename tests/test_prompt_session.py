from __future__ import annotations

from pathlib import Path

import codeforerunner
from codeforerunner.prompt_session import Denial, PromptSession

PROMPTS_ROOT = Path(codeforerunner.__file__).parent / "prompts"


def test_non_exempt_task_denied_when_scan_not_satisfied():
    session = PromptSession(PROMPTS_ROOT, scan_satisfied=False)
    result = session.can_run("readme")
    assert result.allowed is False
    assert result.reason is Denial.SCAN_REQUIRED


def test_exempt_task_allowed_when_scan_not_satisfied():
    session = PromptSession(PROMPTS_ROOT, scan_satisfied=False)
    for name in ("scan", "init-agent-onboarding"):
        result = session.can_run(name)
        assert result.allowed is True, name
        assert result.task.name == name


def test_non_exempt_task_allowed_when_scan_satisfied():
    session = PromptSession(PROMPTS_ROOT, scan_satisfied=True)
    result = session.can_run("readme")
    assert result.allowed is True
    assert result.task.name == "readme"


def test_unknown_task_denied():
    session = PromptSession(PROMPTS_ROOT, scan_satisfied=True)
    result = session.can_run("not-a-real-task")
    assert result.allowed is False
    assert result.reason is Denial.UNKNOWN_TASK


def test_mark_scan_done_unblocks_non_exempt_task():
    session = PromptSession(PROMPTS_ROOT, scan_satisfied=False)
    assert session.can_run("readme").allowed is False
    session.mark_scan_done()
    assert session.can_run("readme").allowed is True


def test_bundle_for_resolves_prompt_text():
    session = PromptSession(PROMPTS_ROOT, scan_satisfied=True)
    text = session.bundle_for("readme")
    assert "<!-- task: readme.md -->" in text
