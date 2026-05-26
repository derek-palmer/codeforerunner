#!/usr/bin/env bash
# Apply a branch ruleset to main using the GitHub Rulesets API.
# Requires: gh CLI authenticated with repo admin scope.
# Re-runnable — deletes any existing ruleset named "main-protection" first.
set -euo pipefail

REPO="derek-palmer/codeforerunner"
RULESET_NAME="main-protection"

echo "Removing existing ruleset '${RULESET_NAME}' if present..."
EXISTING_ID=$(gh api "repos/${REPO}/rulesets" --jq ".[] | select(.name == \"${RULESET_NAME}\") | .id" 2>/dev/null || true)
if [ -n "$EXISTING_ID" ]; then
  gh api --method DELETE "repos/${REPO}/rulesets/${EXISTING_ID}"
  echo "  Deleted ruleset id=${EXISTING_ID}"
fi

echo "Creating ruleset '${RULESET_NAME}'..."

gh api \
  --method POST \
  "repos/${REPO}/rulesets" \
  --input - <<'JSON'
{
  "name": "main-protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/main"],
      "exclude": []
    }
  },
  "bypass_actors": [
    {
      "actor_id": 5,
      "actor_type": "RepositoryRole",
      "bypass_mode": "always"
    }
  ],
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "check" }
        ]
      }
    },
    { "type": "non_fast_forward" },
    { "type": "deletion" }
  ]
}
JSON

echo "Done."
