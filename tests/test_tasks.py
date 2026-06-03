from __future__ import annotations

import pytest

from codeforerunner import tasks


def test_all_tasks_nonempty():
    result = tasks.all_tasks()
    assert len(result) > 0


def test_get_returns_task_fields():
    t = tasks.get("readme")
    assert t.name == "readme"
    assert t.scan_exempt is False
    assert t.skill_slug == "forerunner-readme"


def test_get_scan_is_exempt():
    assert tasks.get("scan").scan_exempt is True


def test_get_init_agent_onboarding_exempt_and_slug():
    t = tasks.get("init-agent-onboarding")
    assert t.scan_exempt is True
    assert t.skill_slug == "forerunner-init"


def test_get_unknown_raises():
    with pytest.raises(KeyError):
        tasks.get("nonexistent-task")


def test_scan_exempt_names():
    assert tasks.scan_exempt_names() == {"scan", "init-agent-onboarding", "gaps"}


def test_refresh_tasks_ordered():
    result = tasks.refresh_tasks()
    names = [t.name for t in result]
    assert names == ["scan", "check", "readme", "api-docs", "stack-docs",
                     "diagrams", "flows", "version-audit", "audit"]


def test_refresh_tasks_excludes_arch_review():
    names = [t.name for t in tasks.refresh_tasks()]
    assert "arch-review" not in names


def test_installable_slugs_starts_with_canonical():
    slugs = tasks.installable_slugs()
    assert slugs[0] == "codeforerunner"


def test_installable_slugs_includes_forerunner_refresh():
    assert "forerunner-refresh" in tasks.installable_slugs()


def test_all_tasks_have_prompt_files():
    import codeforerunner
    from pathlib import Path
    tasks_dir = Path(codeforerunner.__file__).parent / "prompts" / "tasks"
    for task in tasks.all_tasks():
        prompt = tasks_dir / f"{task.name}.md"
        assert prompt.is_file(), f"missing prompt file for task {task.name!r}"


def test_cli_rejects_unregistered_task(tmp_path, capsys):
    from codeforerunner.cli import main
    (tmp_path / "prompts" / "tasks").mkdir(parents=True)
    (tmp_path / "prompts" / "tasks" / "scan.md").write_text("# scan\n")
    rc = main(["--repo", str(tmp_path), "doc", "not-a-real-task"])
    assert rc != 0
    assert "unknown task" in capsys.readouterr().err


def test_gaps_task_registered():
    t = tasks.get("gaps")
    assert t.scan_exempt is True
    assert t.skill_slug == "forerunner-gaps"


def test_gaps_excluded_from_refresh_sequence():
    names = [t.name for t in tasks.refresh_tasks()]
    assert "gaps" not in names


def test_gaps_installable_slug_present():
    assert "forerunner-gaps" in tasks.installable_slugs()


def test_gaps_skill_files_exist():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    assert (root / "skills" / "forerunner-gaps" / "SKILL.md").is_file()
    assert (root / "plugins" / "codeforerunner" / "skills" / "forerunner-gaps" / "SKILL.md").is_file()


def test_gaps_skill_copies_in_sync():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    installed = (root / "skills" / "forerunner-gaps" / "SKILL.md").read_text(encoding="utf-8")
    plugin = (root / "plugins" / "codeforerunner" / "skills" / "forerunner-gaps" / "SKILL.md").read_text(encoding="utf-8")
    assert installed == plugin


def test_mcp_tools_list_matches_registry():
    from codeforerunner.mcp_server import _tools
    import codeforerunner
    from pathlib import Path
    prompts = Path(codeforerunner.__file__).parent / "prompts"
    tool_names = {t["name"] for t in _tools(prompts)}
    registry_names = {t.name for t in tasks.all_tasks()}
    assert tool_names == registry_names
