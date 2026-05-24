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

REPO="derek-palmer/codeforerunner"

# Locate bin/install.js relative to this script (works even when piped through bash)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-install.sh}")" 2>/dev/null && pwd || echo "")"
LOCAL_JS="${SCRIPT_DIR}/bin/install.js"

if [[ -n "$SCRIPT_DIR" && -f "$LOCAL_JS" ]]; then
  exec node "$LOCAL_JS" "$@"
else
  exec npx -y "github:${REPO}" -- "$@"
fi
