#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: scripts/bump-version.sh <semver>" >&2
  exit 1
fi

VERSION="$1"
export VERSION

python <<'PY'
import json
import os
import re
import sys
from pathlib import Path

root = Path.cwd()
version = os.environ["VERSION"]

if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    print(f"error: invalid semver '{version}' (expected X.Y.Z)", file=sys.stderr)
    raise SystemExit(1)

pyproject_path = root / "pyproject.toml"
package_path = root / "package.json"
marketplace_path = root / "plugins" / "codex" / "marketplace.json"

for path in (pyproject_path, package_path, marketplace_path):
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

pyproject_path.write_text(new_pyproject_text)
package_path.write_text(json.dumps(package_data, indent=2) + "\n")
marketplace_path.write_text(json.dumps(marketplace_data, indent=2) + "\n")

print(f"bumped version {current_pyproject} -> {version}")
PY
