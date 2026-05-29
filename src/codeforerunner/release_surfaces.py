"""Release Surface Manifest — single source of truth for release policy.

Catalogs the surfaces codeforerunner publishes to (PyPI, npmjs, GitHub
Packages, Docker, the Codex marketplace, installer shims) and, for each, the
version source, registry target, auth mode, and required validations.

The manifest itself lives in ``release_surfaces.json``; this module is the
typed accessor over it, mirroring the Task Registry (``tasks.py``). Version
values are read lazily via :func:`read_surface_version` from a repo checkout —
nothing here touches the filesystem at import time beyond the packaged JSON.
"""

from __future__ import annotations

import importlib.resources
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

KINDS = frozenset(
    {
        "package_registry",
        "container_registry",
        "plugin_marketplace",
        "installer_shim",
        "badge",
    }
)
AUTH_MODES = frozenset({"oidc", "github_token", "pat", "none"})
VERSION_SOURCE_KINDS = frozenset({"toml_path", "json_path", "regex"})


@dataclass(frozen=True)
class ReleaseSurface:
    name: str
    kind: str
    registry: str
    auth_mode: str
    workflow: str | None
    version_source: dict
    validations: tuple[str, ...]


def _load() -> list[ReleaseSurface]:
    data = json.loads(
        importlib.resources.files("codeforerunner")
        .joinpath("release_surfaces.json")
        .read_text(encoding="utf-8")
    )
    return [
        ReleaseSurface(
            name=entry["name"],
            kind=entry["kind"],
            registry=entry["registry"],
            auth_mode=entry["auth_mode"],
            workflow=entry.get("workflow"),
            version_source=entry["version_source"],
            validations=tuple(entry.get("validations", [])),
        )
        for entry in data["surfaces"]
    ]


_SURFACES = _load()
_BY_NAME: dict[str, ReleaseSurface] = {s.name: s for s in _SURFACES}


def all_surfaces() -> list[ReleaseSurface]:
    return list(_SURFACES)


def names() -> tuple[str, ...]:
    return tuple(s.name for s in _SURFACES)


def get(name: str) -> ReleaseSurface:
    try:
        return _BY_NAME[name]
    except KeyError:
        raise KeyError(f"unknown release surface: {name!r}") from None


def version_bearing_surfaces() -> list[ReleaseSurface]:
    """Surfaces that pin a published version (all of them, currently)."""
    return [s for s in _SURFACES if s.version_source]


def _navigate(data, selector):
    for key in selector:
        data = data[key]
    return data


def read_surface_version(surface: ReleaseSurface, repo_root: Path) -> str:
    """Read a surface's version from its declared source under ``repo_root``.

    Lets version-drift checks be driven entirely by the manifest: read every
    version-bearing surface and assert the values agree.
    """
    src = surface.version_source
    path = repo_root / src["file"]
    kind = src["kind"]
    if kind == "toml_path":
        with path.open("rb") as f:
            return str(_navigate(tomllib.load(f), src["selector"]))
    if kind == "json_path":
        return str(_navigate(json.loads(path.read_text(encoding="utf-8")), src["selector"]))
    if kind == "regex":
        m = re.search(src["selector"], path.read_text(encoding="utf-8"), re.MULTILINE)
        if not m:
            raise ValueError(f"{surface.name}: pattern did not match in {src['file']}")
        return m.group(1)
    raise ValueError(f"{surface.name}: unknown version_source kind {kind!r}")
