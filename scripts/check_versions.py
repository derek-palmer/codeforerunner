#!/usr/bin/env python3
"""Assert all version fields across pyproject.toml, package.json, marketplace.json, and installer shims match."""

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).parent.parent


def read_pyproject_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as f:
        return tomllib.load(f)["project"]["version"]


def read_package_json_version() -> str:
    data = json.loads((ROOT / "package.json").read_text())
    return data["version"]


def read_marketplace_versions() -> tuple[str, str]:
    data = json.loads((ROOT / "plugins" / "codex" / "marketplace.json").read_text())
    return data["marketplace"]["version"], data["plugins"][0]["version"]


def read_install_sh_version() -> str:
    text = (ROOT / "install.sh").read_text()
    m = re.search(r'^NPM_PKG="codeforerunner@([^"]+)"', text, re.MULTILINE)
    if not m:
        raise ValueError("could not parse NPM_PKG version from install.sh")
    return m.group(1)


def read_install_ps1_version() -> str:
    text = (ROOT / "install.ps1").read_text()
    m = re.search(r'^\$NpmPkg\s*=\s*"codeforerunner@([^"]+)"', text, re.MULTILINE)
    if not m:
        raise ValueError("could not parse $NpmPkg version from install.ps1")
    return m.group(1)


def main() -> int:
    pyproject = read_pyproject_version()
    package = read_package_json_version()
    marketplace, plugin = read_marketplace_versions()
    install_sh = read_install_sh_version()
    install_ps1 = read_install_ps1_version()

    rows = [
        ("pyproject.toml [project].version", pyproject),
        ("package.json .version", package),
        ("marketplace.json .marketplace.version", marketplace),
        ("marketplace.json .plugins[0].version", plugin),
        ("install.sh NPM_PKG", install_sh),
        ("install.ps1 $NpmPkg", install_ps1),
    ]

    col = max(len(r[0]) for r in rows)
    print(f"{'Source':<{col}}  Version")
    print("-" * (col + 12))
    for source, version in rows:
        print(f"{source:<{col}}  {version}")

    versions = {v for _, v in rows}
    if len(versions) == 1:
        print("\nAll versions match.")
        return 0

    print(f"\nERROR: version mismatch — found {', '.join(sorted(versions))}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
