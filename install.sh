#!/usr/bin/env bash
# codeforerunner skill installer
# Detects installed agent CLIs and drops forerunner skills into each one.
#
# Usage:
#   ./install.sh              # auto-detect all agents
#   ./install.sh --only claude
#   ./install.sh --only codex
#   ./install.sh --dry-run
#   ./install.sh --list
#   ./install.sh --uninstall
#
# One-liner (from anywhere):
#   curl -fsSL https://raw.githubusercontent.com/derek-palmer/codeforerunner/main/install.sh | bash

set -euo pipefail

REPO_OWNER="derek-palmer"
REPO_NAME="codeforerunner"
RAW_BASE="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main"
GITHUB_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}"

SKILL_SLUGS=(
  "codeforerunner"
  "forerunner-scan"
  "forerunner-readme"
  "forerunner-api-docs"
  "forerunner-audit"
  "forerunner-changelog"
  "forerunner-check"
  "forerunner-diagrams"
  "forerunner-flows"
  "forerunner-init"
  "forerunner-review"
  "forerunner-stack-docs"
  "forerunner-version-audit"
)

# ── parse args ────────────────────────────────────────────────────────────────

DRY_RUN=false
UNINSTALL=false
LIST_ONLY=false
ONLY_AGENTS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)   DRY_RUN=true; shift ;;
    --uninstall) UNINSTALL=true; shift ;;
    --list)      LIST_ONLY=true; shift ;;
    --only)      ONLY_AGENTS+=("$2"); shift 2 ;;
    --only=*)    ONLY_AGENTS+=("${1#--only=}"); shift ;;
    -h|--help)
      echo "Usage: install.sh [--dry-run] [--uninstall] [--list] [--only <agent>]"
      echo "Agents: claude, codex, gemini"
      exit 0 ;;
    *) echo "unknown flag: $1" >&2; exit 1 ;;
  esac
done

# ── detect source ─────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-install.sh}")" 2>/dev/null && pwd || echo "")"
if [[ -n "$SCRIPT_DIR" && -d "${SCRIPT_DIR}/plugins/codeforerunner/skills" ]]; then
  LOCAL=true
  SKILLS_SRC="${SCRIPT_DIR}/plugins/codeforerunner/skills"
else
  LOCAL=false
  SKILLS_SRC=""
fi

# ── helpers ───────────────────────────────────────────────────────────────────

log()  { echo "  $*"; }
ok()   { echo "  ✓ $*"; }
skip() { echo "  – $* (skipped)"; }
err()  { echo "  ✗ $*" >&2; }

_skill_dest_claude() {
  local slug="$1"
  echo "${HOME}/.claude/plugins/codeforerunner/skills/${slug}/SKILL.md"
}

_skill_dest_codex() {
  local slug="$1"
  echo "${HOME}/.codex/skills/${slug}/SKILL.md"
}

_copy_skill() {
  local slug="$1" dest="$2"
  if [[ "$LOCAL" == "true" ]]; then
    local src="${SKILLS_SRC}/${slug}/SKILL.md"
    if [[ ! -f "$src" ]]; then
      err "source not found: $src"
      return 1
    fi
    if [[ "$DRY_RUN" == "false" ]]; then
      mkdir -p "$(dirname "$dest")"
      cp "$src" "$dest"
    fi
  else
    local url="${RAW_BASE}/plugins/codeforerunner/skills/${slug}/SKILL.md"
    if [[ "$DRY_RUN" == "false" ]]; then
      mkdir -p "$(dirname "$dest")"
      curl -fsSL "$url" -o "$dest"
    fi
  fi
}

_remove_skill() {
  local dest="$1"
  if [[ -f "$dest" ]]; then
    [[ "$DRY_RUN" == "false" ]] && rm -f "$dest"
    ok "removed $dest"
  fi
}

_should_install() {
  local agent="$1"
  [[ ${#ONLY_AGENTS[@]} -eq 0 ]] || [[ " ${ONLY_AGENTS[*]} " =~ " ${agent} " ]]
}

# ── detection ─────────────────────────────────────────────────────────────────

HAS_CLAUDE=false
HAS_CODEX=false
HAS_GEMINI=false

command -v claude &>/dev/null && HAS_CLAUDE=true
command -v codex  &>/dev/null && HAS_CODEX=true
command -v gemini &>/dev/null && HAS_GEMINI=true

# ── list mode ─────────────────────────────────────────────────────────────────

if [[ "$LIST_ONLY" == "true" ]]; then
  echo "codeforerunner skill installer — agent detection:"
  echo ""
  printf "  %-12s  %s\n" "claude"  "$( [[ "$HAS_CLAUDE" == "true" ]] && echo "detected ✓" || echo "not found")"
  printf "  %-12s  %s\n" "codex"   "$( [[ "$HAS_CODEX"  == "true" ]] && echo "detected ✓" || echo "not found")"
  printf "  %-12s  %s\n" "gemini"  "$( [[ "$HAS_GEMINI" == "true" ]] && echo "detected ✓" || echo "not found")"
  echo ""
  echo "Skills that will be installed (${#SKILL_SLUGS[@]}):"
  for s in "${SKILL_SLUGS[@]}"; do echo "  /$s"; done
  exit 0
fi

# ── uninstall ─────────────────────────────────────────────────────────────────

if [[ "$UNINSTALL" == "true" ]]; then
  echo "codeforerunner — uninstalling skills"
  for slug in "${SKILL_SLUGS[@]}"; do
    _should_install "claude" && _remove_skill "$(_skill_dest_claude "$slug")"
    _should_install "codex"  && _remove_skill "$(_skill_dest_codex  "$slug")"
  done
  _should_install "claude" && \
    [[ "$DRY_RUN" == "false" ]] && \
    rmdir "${HOME}/.claude/plugins/codeforerunner" 2>/dev/null || true
  echo "done"
  exit 0
fi

# ── install ───────────────────────────────────────────────────────────────────

INSTALLED=()
SKIPPED=()

echo "codeforerunner — installing skills"
echo ""
[[ "$DRY_RUN" == "true" ]] && echo "  (dry-run — no files written)"
echo ""

# Claude Code
if _should_install "claude"; then
  if [[ "$HAS_CLAUDE" == "true" ]] || [[ ${#ONLY_AGENTS[@]} -gt 0 ]]; then
    echo "Claude Code:"
    # Copy plugin manifest
    if [[ "$DRY_RUN" == "false" ]]; then
      mkdir -p "${HOME}/.claude/plugins/codeforerunner"
      if [[ "$LOCAL" == "true" ]]; then
        cp "${SCRIPT_DIR}/.claude-plugin/plugin.json" "${HOME}/.claude/plugins/codeforerunner/plugin.json"
        cp "${SCRIPT_DIR}/.claude-plugin/marketplace.json" "${HOME}/.claude/plugins/codeforerunner/marketplace.json" 2>/dev/null || true
      else
        curl -fsSL "${RAW_BASE}/.claude-plugin/plugin.json" -o "${HOME}/.claude/plugins/codeforerunner/plugin.json"
        curl -fsSL "${RAW_BASE}/.claude-plugin/marketplace.json" -o "${HOME}/.claude/plugins/codeforerunner/marketplace.json" 2>/dev/null || true
      fi
    fi
    for slug in "${SKILL_SLUGS[@]}"; do
      dest="$(_skill_dest_claude "$slug")"
      if _copy_skill "$slug" "$dest"; then
        ok "$dest"
        INSTALLED+=("claude/$slug")
      fi
    done
  else
    skip "claude (not detected; use --only claude to force)"
    SKIPPED+=("claude")
  fi
  echo ""
fi

# Codex
if _should_install "codex"; then
  if [[ "$HAS_CODEX" == "true" ]] || [[ ${#ONLY_AGENTS[@]} -gt 0 ]]; then
    echo "Codex CLI:"
    for slug in "${SKILL_SLUGS[@]}"; do
      dest="$(_skill_dest_codex "$slug")"
      if _copy_skill "$slug" "$dest"; then
        ok "$dest"
        INSTALLED+=("codex/$slug")
      fi
    done
  else
    skip "codex (not detected; use --only codex to force)"
    SKIPPED+=("codex")
  fi
  echo ""
fi

# Gemini CLI — delegates to native extension install
if _should_install "gemini"; then
  if [[ "$HAS_GEMINI" == "true" ]] || [[ ${#ONLY_AGENTS[@]} -gt 0 ]]; then
    echo "Gemini CLI:"
    if [[ "$DRY_RUN" == "false" ]]; then
      if gemini extensions install "${GITHUB_URL}" 2>/dev/null; then
        ok "installed via gemini extensions install"
        INSTALLED+=("gemini")
      else
        err "gemini extensions install failed; check gemini CLI version"
      fi
    else
      log "would run: gemini extensions install ${GITHUB_URL}"
    fi
  else
    skip "gemini (not detected; use --only gemini to force)"
    SKIPPED+=("gemini")
  fi
  echo ""
fi

# ── summary ───────────────────────────────────────────────────────────────────

echo "Summary:"
if [[ ${#INSTALLED[@]} -gt 0 ]]; then
  unique_agents=$(printf '%s\n' "${INSTALLED[@]}" | cut -d/ -f1 | sort -u | tr '\n' ' ')
  echo "  installed for: ${unique_agents}"
fi
if [[ ${#SKIPPED[@]} -gt 0 ]]; then
  echo "  skipped: ${SKIPPED[*]}"
fi
if [[ ${#INSTALLED[@]} -eq 0 && ${#SKIPPED[@]} -eq 0 ]]; then
  echo "  no agents detected; use --only <agent> to install for a specific agent"
  echo "  supported: claude, codex, gemini"
fi
echo ""
echo "  To add forerunner to a project: forerunner doctor --fix"
echo "  Docs: ${GITHUB_URL}"
