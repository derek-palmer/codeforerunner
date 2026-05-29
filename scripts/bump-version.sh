#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "error: no python interpreter found (.venv/bin/python, python3, or python)" >&2
  exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "usage: scripts/bump-version.sh <semver>" >&2
  exit 1
fi

VERSION="$1"
export VERSION
export REPO_ROOT

"$PYTHON_BIN" <<'PY'
import json
import os
import re
import sys
from pathlib import Path

root = Path(os.environ["REPO_ROOT"])
version = os.environ["VERSION"]

if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    print(f"error: invalid semver '{version}' (expected X.Y.Z)", file=sys.stderr)
    raise SystemExit(1)

pyproject_path = root / "pyproject.toml"
package_path = root / "package.json"
marketplace_path = root / "plugins" / "codex" / "marketplace.json"
readme_path = root / "README.md"
install_sh_path = root / "install.sh"
install_ps1_path = root / "install.ps1"

for path in (pyproject_path, package_path, marketplace_path, readme_path, install_sh_path, install_ps1_path):
    if not path.is_file():
        print(f"error: missing required file: {path}", file=sys.stderr)
        raise SystemExit(1)

pyproject_text = pyproject_path.read_text()
in_project = False
current_pyproject = None
pyproject_line = None
for line in pyproject_text.splitlines():
    if re.match(r"^\[project\]", line):
        in_project = True
        continue
    if re.match(r"^\[", line):
        in_project = False
    if in_project:
        m = re.match(r'^(version\s*=\s*")([^"]+)(".*)$', line)
        if m:
            current_pyproject = m.group(2)
            pyproject_line = line
            break

if current_pyproject is None or pyproject_line is None:
    print("error: pyproject.toml missing [project].version", file=sys.stderr)
    raise SystemExit(1)

package_data = json.loads(package_path.read_text())
marketplace_data = json.loads(marketplace_path.read_text())
readme_text = readme_path.read_text()
install_sh_text = install_sh_path.read_text()
install_ps1_text = install_ps1_path.read_text()

try:
    current_package = package_data["version"]
    current_marketplace = marketplace_data["marketplace"]["version"]
    current_plugin = marketplace_data["plugins"][0]["version"]
except (KeyError, IndexError, TypeError) as exc:
    print(f"error: version shape missing from JSON files: {exc}", file=sys.stderr)
    raise SystemExit(1)

current_versions = {
    "pyproject.toml": current_pyproject,
    "package.json": current_package,
    "plugins/codex/marketplace.json marketplace.version": current_marketplace,
    "plugins/codex/marketplace.json plugins[0].version": current_plugin,
}

if len(set(current_versions.values())) != 1:
    print("error: current version files are already out of sync:", file=sys.stderr)
    for name, value in current_versions.items():
        print(f"  {name}: {value}", file=sys.stderr)
    raise SystemExit(1)

if current_pyproject == version:
    print(f"version already at {version}; no changes made")
    raise SystemExit(0)

new_pyproject_text = pyproject_text.replace(
    pyproject_line,
    pyproject_line.replace(current_pyproject, version, 1),
    1,
)
if new_pyproject_text == pyproject_text:
    print("error: failed to update pyproject.toml", file=sys.stderr)
    raise SystemExit(1)

package_data["version"] = version
marketplace_data["marketplace"]["version"] = version
marketplace_data["plugins"][0]["version"] = version

new_readme_text = readme_text
new_readme_text = re.sub(
    rf"(https://badge\.socket\.dev/npm/package/codeforerunner/){re.escape(current_pyproject)}",
    rf"\g<1>{version}",
    new_readme_text,
)
new_readme_text = re.sub(
    rf"(@v){re.escape(current_pyproject)}(\b)",
    rf"\g<1>{version}\g<2>",
    new_readme_text,
)

new_install_sh_text = re.sub(
    rf'(NPM_PKG="codeforerunner@){re.escape(current_pyproject)}(")',
    rf"\g<1>{version}\g<2>",
    install_sh_text,
)
new_install_sh_text = re.sub(
    rf'(REPO_TAG="v){re.escape(current_pyproject)}(")',
    rf"\g<1>{version}\g<2>",
    new_install_sh_text,
)
new_install_ps1_text = re.sub(
    rf'(\$NpmPkg\s*=\s*"codeforerunner@){re.escape(current_pyproject)}(")',
    rf"\g<1>{version}\g<2>",
    install_ps1_text,
)
new_install_ps1_text = re.sub(
    rf'(\$RepoTag\s*=\s*"v){re.escape(current_pyproject)}(")',
    rf"\g<1>{version}\g<2>",
    new_install_ps1_text,
)

if new_install_sh_text == install_sh_text:
    print("error: failed to update install.sh", file=sys.stderr)
    raise SystemExit(1)
if new_install_ps1_text == install_ps1_text:
    print("error: failed to update install.ps1", file=sys.stderr)
    raise SystemExit(1)

pyproject_path.write_text(new_pyproject_text)
package_path.write_text(json.dumps(package_data, indent=2, ensure_ascii=False) + "\n")
marketplace_path.write_text(json.dumps(marketplace_data, indent=2, ensure_ascii=False) + "\n")
readme_path.write_text(new_readme_text)
install_sh_path.write_text(new_install_sh_text)
install_ps1_path.write_text(new_install_ps1_text)

print(f"bumped version {current_pyproject} -> {version}")
PY
