#!/usr/bin/env python3
"""Validate plugins/codex/marketplace.json.

Stdlib-only validator. Runnable directly:

    python scripts/validate_codex_marketplace.py

Or imported by tests:

    from scripts.validate_codex_marketplace import validate
    errors = validate(repo_root)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
MANIFEST_RELPATH = Path("plugins") / "codex" / "marketplace.json"
ALLOWED_SOURCE_KINDS = {"git", "local"}


def _is_nonempty_str(value: object) -> bool:
    return isinstance(value, str) and value != ""


def validate(repo_root: Path) -> list[str]:
    """Return a list of error messages. Empty list means the manifest is valid."""
    errors: list[str] = []
    manifest_path = repo_root / MANIFEST_RELPATH

    if not manifest_path.exists():
        errors.append(f"manifest file not found: {manifest_path}")
        return errors

    try:
        raw = manifest_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append(f"manifest is not valid JSON: {exc}")
        return errors
    except OSError as exc:
        errors.append(f"could not read manifest: {exc}")
        return errors

    if not isinstance(data, dict):
        errors.append("manifest top-level must be a JSON object")
        return errors

    if "marketplace" not in data:
        errors.append("missing top-level key: marketplace")
    if "plugins" not in data:
        errors.append("missing top-level key: plugins")
    if errors:
        return errors

    marketplace = data["marketplace"]
    if not isinstance(marketplace, dict):
        errors.append("marketplace must be an object")
    else:
        for key in ("id", "name", "version"):
            if not _is_nonempty_str(marketplace.get(key)):
                errors.append(f"marketplace.{key} must be a non-empty string")
        version = marketplace.get("version")
        if isinstance(version, str) and not SEMVER_RE.match(version):
            errors.append(
                f"marketplace.version '{version}' is not valid semver"
            )

    plugins = data["plugins"]
    if not isinstance(plugins, list):
        errors.append("plugins must be a list")
        return errors
    if len(plugins) < 1:
        errors.append("plugins list must contain at least one entry")
        return errors

    for idx, plugin in enumerate(plugins):
        prefix = f"plugins[{idx}]"
        if not isinstance(plugin, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in ("id", "name", "version", "description", "entry"):
            if not _is_nonempty_str(plugin.get(key)):
                errors.append(f"{prefix}.{key} must be a non-empty string")

        version = plugin.get("version")
        if isinstance(version, str) and not SEMVER_RE.match(version):
            errors.append(
                f"{prefix}.version '{version}' is not valid semver"
            )

        source = plugin.get("source")
        if not isinstance(source, dict):
            errors.append(f"{prefix}.source must be an object")
        else:
            kind = source.get("kind")
            if kind not in ALLOWED_SOURCE_KINDS:
                errors.append(
                    f"{prefix}.source.kind must be one of {sorted(ALLOWED_SOURCE_KINDS)}"
                )
            for key in ("url", "path"):
                if not _is_nonempty_str(source.get(key)):
                    errors.append(f"{prefix}.source.{key} must be a non-empty string")

        entry = plugin.get("entry")
        if isinstance(entry, str) and entry:
            entry_path = repo_root / entry
            if not entry_path.exists():
                errors.append(
                    f"{prefix}.entry path does not exist: {entry}"
                )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    errors = validate(repo_root)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
