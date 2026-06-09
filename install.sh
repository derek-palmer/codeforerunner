#!/usr/bin/env bash
# codeforerunner skill installer — thin Node.js shim.
# Delegates to bin/install.js when run from a local clone,
# or fetches and runs it via npx from a curl|bash one-liner.
#
# Usage (local clone):
#   ./install.sh [flags]
#
# One-liner:
#   curl -fsSL https://raw.githubusercontent.com/derek-palmer/codeforerunner/main/install.sh | bash
#
# All flags (--dry-run, --force, --only, --all, --minimal, --list, --no-color,
#             --skip-skills, --uninstall, -h/--help) are forwarded to bin/install.js.

set -euo pipefail

# Security: pinned to a specific version so curl|bash one-liners don't silently
# execute whatever the npm registry or GitHub currently serves as "latest".
NPM_PKG="codeforerunner@0.4.10"
REPO="derek-palmer/codeforerunner"
REPO_TAG="v0.4.10"

# Locate bin/install.js relative to this script (works even when piped through bash)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-install.sh}")" 2>/dev/null && pwd || echo "")"
LOCAL_JS="${SCRIPT_DIR}/bin/install.js"

if [[ -n "$SCRIPT_DIR" && -f "$LOCAL_JS" ]]; then
  exec node "$LOCAL_JS" "$@"
else
  # Primary: npm registry. Fallback: GitHub source (in case npm is down).
  # Probe the registry with a HEAD request to avoid running npx twice.
  if curl -sf --head "https://registry.npmjs.org/codeforerunner/latest" &>/dev/null; then
    exec npx --yes "${NPM_PKG}" -- "$@"
  else
    exec npx --yes "github:${REPO}#${REPO_TAG}" -- "$@"
  fi
fi
