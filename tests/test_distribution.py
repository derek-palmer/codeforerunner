"""Behavior tests for the Distribution Inventory (distribution.py).

The inventory owns codeforerunner's distribution artifact identity — canonical
skill path, distributed copy paths, marketplace manifest path, managed-region
markers — and the default install-destination templates. Installer, doctor, and
validators consult it instead of repeating these constants.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codeforerunner import distribution as dist


def test_canonical_and_copies_are_declared():
    assert dist.CANONICAL_SKILL_REL == Path("agent/codeforerunner.skill.md")
    assert dist.DISTRIBUTED_SKILL_COPIES_REL  # non-empty
    # Canonical is the source of truth, never one of the distributed copies.
    assert dist.CANONICAL_SKILL_REL not in dist.DISTRIBUTED_SKILL_COPIES_REL


def test_marketplace_manifest_path_is_declared():
    assert dist.MARKETPLACE_MANIFEST_REL == Path("plugins/codex/marketplace.json")


def test_managed_region_markers_are_declared():
    assert dist.MARKER_BEGIN.startswith("<!-- forerunner:begin")
    assert "managed=codeforerunner.skill" in dist.MARKER_BEGIN
    assert dist.MARKER_END == "<!-- forerunner:end -->"


def test_skill_destination_resolves_per_agent_and_slug():
    home = Path("/home/u")
    assert (
        dist.skill_destination("codex", "codeforerunner", home)
        == home / ".codex/skills/codeforerunner/SKILL.md"
    )
    assert (
        dist.skill_destination("claude", "forerunner-scan", home)
        == home / ".claude/plugins/codeforerunner/skills/forerunner-scan/SKILL.md"
    )


def test_skill_destination_rejects_unknown_agent():
    with pytest.raises(ValueError):
        dist.skill_destination("emacs", "codeforerunner", Path("/home/u"))


def test_marketplace_destination_resolves_under_home():
    home = Path("/home/u")
    assert dist.marketplace_destination(home) == home / ".codex/marketplaces/codeforerunner.json"
