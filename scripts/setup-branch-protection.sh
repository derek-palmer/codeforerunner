#!/usr/bin/env bash
# Apply branch protection rules to main.
# Requires: gh CLI authenticated with repo admin scope.
# Re-runnable — PUT replaces existing rules.
set -euo pipefail

REPO="derek-palmer/codeforerunner"
BRANCH="main"

echo "Applying branch protection to ${REPO}:${BRANCH}..."

gh api \
  --method PUT \
  "repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["check"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON

echo "Done."
