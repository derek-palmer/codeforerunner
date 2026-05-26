"""Tests for bundle.py edge cases."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from codeforerunner.bundle import find_prompts_root, resolve_bundle


def test_find_prompts_root_raises_when_repo_arg_has_no_tasks(tmp_path):
    with pytest.raises(FileNotFoundError, match="no prompts/tasks/"):
        find_prompts_root(tmp_path)


def test_find_prompts_root_uses_repo_arg_when_tasks_present(tmp_path):
    (tmp_path / "prompts" / "tasks").mkdir(parents=True)
    result = find_prompts_root(tmp_path)
    assert result == tmp_path / "prompts"


def test_find_prompts_root_walks_cwd_to_find_prompts(tmp_path):
    # Create prompts/tasks/ in tmp_path and change cwd into a subdir
    (tmp_path / "prompts" / "tasks").mkdir(parents=True)
    subdir = tmp_path / "deep" / "nested"
    subdir.mkdir(parents=True)
    with patch("codeforerunner.bundle.Path") as MockPath:
        # Replace cwd() so the walk starts from subdir
        MockPath.cwd.return_value = subdir
        # Make sure Path still works for everything else
        MockPath.side_effect = lambda x=None: Path(x) if x is not None else Path()
        # Directly test the cwd walk logic with the real function
        pass

    # Simpler approach: call find_prompts_root from within a subdir of tmp_path
    import os
    old_cwd = os.getcwd()
    try:
        subdir.mkdir(parents=True, exist_ok=True)
        os.chdir(subdir)
        result = find_prompts_root()
        assert result == tmp_path / "prompts"
    finally:
        os.chdir(old_cwd)


def test_find_prompts_root_raises_when_no_package_prompts(tmp_path, monkeypatch):
    import os
    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        # Patch _package_prompts to point to a dir with no tasks/
        with patch("codeforerunner.bundle._package_prompts", return_value=tmp_path / "pkg"):
            with pytest.raises(FileNotFoundError, match="could not find prompts/tasks"):
                find_prompts_root()
    finally:
        os.chdir(old_cwd)


def test_resolve_bundle_raises_for_unknown_task(tmp_path):
    (tmp_path / "tasks").mkdir()
    with pytest.raises(FileNotFoundError, match="unknown task"):
        resolve_bundle(tmp_path, "nonexistent-task")
