"""Distribution Inventory — single source of truth for distribution artifact
identity and install policy.

Owns the packaging facts that were previously duplicated across the installer,
doctor, and validation scripts: the canonical skill path, its distributed copy
paths, the Codex marketplace manifest path, the managed-region markers, and the
default install-destination templates. Consumers consult this module instead of
re-declaring constants, so a packaging change is one edit here.

Mirrors the Task Registry (``tasks.py``) and Release Surface Manifest
(``release_surfaces.py``) single-source pattern.
"""

from __future__ import annotations

from pathlib import Path

# --- artifact identity (repo-relative) ------------------------------------

# Source of truth for the codeforerunner skill body; copies derive from it.
CANONICAL_SKILL_REL = Path("agent/codeforerunner.skill.md")

# Distributed copies whose bodies must match the canonical (V10 body parity).
DISTRIBUTED_SKILL_COPIES_REL: tuple[Path, ...] = (
    Path("plugins/codeforerunner/skills/codeforerunner/SKILL.md"),
    Path("skills/codeforerunner/SKILL.md"),
)

# Codex marketplace manifest shipped as a release asset.
MARKETPLACE_MANIFEST_REL = Path("plugins/codex/marketplace.json")

# --- managed-region markers -----------------------------------------------

# Delimit the installer-owned region in a destination file so re-runs are
# idempotent and unmanaged content is never clobbered.
MARKER_BEGIN = "<!-- forerunner:begin managed=codeforerunner.skill -->"
MARKER_END = "<!-- forerunner:end -->"

# --- install-destination templates ----------------------------------------

# Agents whose default skill destination the inventory can resolve.
SKILL_DEST_AGENTS: tuple[str, ...] = ("codex", "claude")


def skill_destination(agent: str, slug: str, home: Path) -> Path:
    """Default install path for skill ``slug`` under ``agent``, relative to ``home``."""
    if agent == "codex":
        return home / f".codex/skills/{slug}/SKILL.md"
    if agent == "claude":
        return home / f".claude/plugins/codeforerunner/skills/{slug}/SKILL.md"
    raise ValueError(f"no default skill destination for agent {agent!r} (expected: {', '.join(SKILL_DEST_AGENTS)})")


def marketplace_destination(home: Path) -> Path:
    """Default install path for the Codex marketplace manifest, relative to ``home``."""
    return home / ".codex/marketplaces/codeforerunner.json"
