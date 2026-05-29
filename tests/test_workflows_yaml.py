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


def test_npm_publish_workflow_uses_oidc_trusted_publishing():
    wf = WORKFLOWS_DIR / "npm-publish.yml"
    text = wf.read_text()
    doc = yaml.safe_load(text)
    trigger = _trigger(doc)
    assert isinstance(trigger, dict), "trigger must be a mapping"
    assert "v*.*.*" in trigger.get("push", {}).get("tags", [])

    publish = doc["jobs"].get("publish")
    assert isinstance(publish, dict), "missing publish job"
    # OIDC trusted publishing is tokenless: id-token write, no NPM_TOKEN.
    assert publish.get("permissions", {}).get("id-token") == "write"
    steps_text = "\n".join(str(step) for step in publish.get("steps", []))
    assert "--provenance" in steps_text
    assert "--access public" in steps_text

    # The npmjs publish job must not reuse a long-lived token; that would
    # silently bypass OIDC trusted publishing.
    publish_only = yaml.dump(publish)
    assert "NPM_TOKEN" not in publish_only
    assert "NODE_AUTH_TOKEN" not in publish_only


def test_docker_publish_workflow_uses_version_tag_and_ghcr():
    wf = WORKFLOWS_DIR / "docker-publish.yml"
    doc = yaml.safe_load(wf.read_text())
    trigger = _trigger(doc)
    assert isinstance(trigger, dict), "trigger must be a mapping"
    push = trigger.get("push")
    assert isinstance(push, dict), "push trigger must be a mapping"
    assert "v*.*.*" in push.get("tags", [])

    publish = doc["jobs"].get("publish")
    assert isinstance(publish, dict), "missing publish job"
    assert publish.get("permissions", {}).get("packages") == "write"
    steps = publish.get("steps", [])
    login_steps = [
        step for step in steps
        if isinstance(step, dict) and step.get("uses") == "docker/login-action@v3"
    ]
    # Publishes to GHCR (registry ghcr.io) and Docker Hub (login-action with no
    # `registry`, which defaults to docker.io). The distroless DHI base was
    # dropped (#72), so there must be no dhi.io login left. Compare registry
    # values with equality (not substring `in`) to avoid host-substring checks.
    registries = [step.get("with", {}).get("registry") for step in login_steps]
    assert any(r == "ghcr.io" for r in registries), (
        f"expected a ghcr.io login, got {registries!r}"
    )
    assert any(r is None or r == "docker.io" for r in registries), (
        f"expected a Docker Hub login (no registry / docker.io), got {registries!r}"
    )
    assert all(r != "dhi.io" for r in registries), "dhi.io login should be removed (#72)"

    steps_text = "\n".join(str(step) for step in publish.get("steps", []))
    assert "docker/login-action" in steps_text
    assert "docker/build-push-action" in steps_text
    assert "scripts/check_versions.py" in steps_text

    # Both publish targets must appear in the image metadata. Parse the
    # metadata-action `images` list and match full image refs exactly.
    meta_step = next(
        step for step in steps
        if isinstance(step, dict) and str(step.get("uses", "")).startswith("docker/metadata-action")
    )
    images = [ln.strip() for ln in str(meta_step["with"]["images"]).splitlines() if ln.strip()]
    expected_ghcr = "ghcr.io/${{ github.repository_owner }}/codeforerunner"
    assert expected_ghcr in images, f"expected GHCR image, got {images!r}"
    assert "heyderekp/codeforerunner" in images, f"expected Docker Hub image, got {images!r}"


def test_release_pr_workflow_requires_release_signal_and_uploads_artifacts():
    wf = WORKFLOWS_DIR / "release-pr.yml"
    doc = yaml.safe_load(wf.read_text())
    trigger = _trigger(doc)
    assert isinstance(trigger, dict), "trigger must be a mapping"
    pull_request = trigger.get("pull_request")
    assert isinstance(pull_request, dict), "pull_request trigger must be a mapping"

    validate_build = doc["jobs"].get("validate-build")
    assert isinstance(validate_build, dict), "missing validate-build job"
    validate_if = str(validate_build.get("if", ""))
    assert "release/" in validate_if
    assert "release-prerelease" in validate_if

    steps_text = "\n".join(str(step) for step in validate_build.get("steps", []))
    assert "actions/upload-artifact" in steps_text
    assert "scripts/check_versions.py" in steps_text
    assert "scripts/validate_codex_marketplace.py" in steps_text
    # npm artifact contents are validated before any tagged publish.
    assert "scripts/inspect_npm_package.py" in steps_text


def test_forerunner_check_workflow_always_runs():
    wf = WORKFLOWS_DIR / "forerunner-check.yml"
    text = wf.read_text()
    assert "forerunner check" in text
    # No job-level hashFiles gate: forerunner check exits 0 when config absent.
    # A pre-checkout hashFiles() always returns '' (empty workspace), so it
    # would skip the job unconditionally, making every push show as failed.
    assert "hashFiles('forerunner.config.yaml')" not in text
