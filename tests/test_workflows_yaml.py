"""Lightweight schema checks for .github/workflows/*.yml.

Catches simple typos in CI even without `actionlint` installed.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


def _workflow_files():
    return sorted(WORKFLOWS_DIR.glob("*.yml"))


def _trigger(doc):
    # In YAML 1.1 (PyYAML default), unquoted `on` parses as the boolean True.
    return doc.get("on", doc.get(True))


def test_workflows_directory_exists_and_nonempty():
    assert WORKFLOWS_DIR.is_dir(), f"missing {WORKFLOWS_DIR}"
    files = _workflow_files()
    assert len(files) >= 1, f"no .yml workflow files in {WORKFLOWS_DIR}"


@pytest.mark.parametrize("wf", _workflow_files(), ids=lambda p: p.name)
def test_each_workflow_parses_as_yaml(wf):
    text = wf.read_text()
    doc = yaml.safe_load(text)
    assert isinstance(doc, dict), f"{wf.name} did not parse as a mapping"


@pytest.mark.parametrize("wf", _workflow_files(), ids=lambda p: p.name)
def test_each_workflow_has_required_top_level_keys(wf):
    doc = yaml.safe_load(wf.read_text())
    assert isinstance(doc.get("name"), str) and doc["name"], (
        f"{wf.name} missing string `name`"
    )
    trigger = _trigger(doc)
    assert trigger is not None, f"{wf.name} missing `on` trigger"
    jobs = doc.get("jobs")
    assert isinstance(jobs, dict) and jobs, (
        f"{wf.name} missing non-empty `jobs` mapping"
    )


@pytest.mark.parametrize("wf", _workflow_files(), ids=lambda p: p.name)
def test_each_job_has_runs_on_and_steps(wf):
    doc = yaml.safe_load(wf.read_text())
    jobs = doc.get("jobs") or {}
    for job_name, job in jobs.items():
        assert isinstance(job, dict), f"{wf.name}: job {job_name} not a mapping"
        assert "runs-on" in job, (
            f"{wf.name}: job {job_name} missing `runs-on`"
        )
        steps = job.get("steps")
        assert isinstance(steps, list) and len(steps) >= 1, (
            f"{wf.name}: job {job_name} has no steps"
        )


def test_marketplace_workflow_triggers_on_version_tag():
    wf = WORKFLOWS_DIR / "codex-marketplace-publish.yml"
    doc = yaml.safe_load(wf.read_text())
    trigger = _trigger(doc)
    assert isinstance(trigger, dict), "trigger must be a mapping"
    push = trigger.get("push")
    assert isinstance(push, dict), "push trigger must be a mapping"
    tags = push.get("tags")
    assert isinstance(tags, list), "push.tags must be a list"
    assert "v*.*.*" in tags, f"expected `v*.*.*` in push.tags, got {tags!r}"


def test_pypi_publish_workflow_uses_version_tag_and_oidc():
    wf = WORKFLOWS_DIR / "publish.yml"
    doc = yaml.safe_load(wf.read_text())
    trigger = _trigger(doc)
    assert isinstance(trigger, dict), "trigger must be a mapping"
    push = trigger.get("push")
    assert isinstance(push, dict), "push trigger must be a mapping"
    assert "v*.*.*" in push.get("tags", [])

    publish = doc["jobs"].get("publish")
    assert isinstance(publish, dict), "missing publish job"
    assert publish.get("permissions", {}).get("id-token") == "write"
    steps_text = "\n".join(str(step) for step in publish.get("steps", []))
    assert "pypa/gh-action-pypi-publish" in steps_text


def test_forerunner_check_workflow_gated_by_config():
    wf = WORKFLOWS_DIR / "forerunner-check.yml"
    text = wf.read_text()
    assert "hashFiles('forerunner.config.yaml')" in text, (
        "forerunner-check.yml must gate on hashFiles('forerunner.config.yaml')"
    )
