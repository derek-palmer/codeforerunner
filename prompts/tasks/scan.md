# Task: Scan

First task in every codeforerunner run. Must complete before any other task.
Output is passed as input to all downstream tasks.

## Input
- Full file tree
- Manifest/config files: package.json, pyproject.toml, go.mod, Cargo.toml, etc.
- Entry point files (up to 5)
- .forerunner.config.yaml if present

## Instructions

1. Identify the primary stack (language, runtime, framework)
2. Identify secondary stacks if present
3. Identify the repo type: app, api, library, cli, etl-pipeline, infra, monorepo, or mixed
4. Identify entry points
5. Identify key modules/packages with distinct responsibility
6. Identify external integrations (evidence-based only)
7. Identify configuration surface (env vars, config files, feature flags)
8. Identify test coverage presence
9. Identify CI/CD presence
10. Identify documentation presence
11. Extract all pinned versions from Dockerfiles, manifests, lockfiles, workflow files, and IaC

## Rules
- Claims must derive from provided files. Unverifiable items go under `gaps:` in the output.

## Output Format

```yaml
# forerunner-scan-result
repo_type: api
primary_stack:
  language: python
  runtime: "3.11"
  framework: fastapi
secondary_stacks:
  - type: infra
    tool: terraform
entry_points:
  - src/main.py
key_modules:
  - path: src/api
    responsibility: HTTP route handlers
external_integrations:
  - type: database
    technology: postgresql
    evidence: "src/db/session.py imports asyncpg"
config_surface:
  env_vars:
    - DATABASE_URL
    - API_KEY
  config_files:
    - .env.example
test_coverage:
  present: true
  framework: pytest
  location: tests/
ci_cd:
  present: true
  platform: github-actions
  workflows:
    - .github/workflows/deploy.yml
docs_presence:
  readme: true
  docs_folder: false
  inline_comments: sparse
pinned_versions_found:
  - component: python
    version: "3.11"
    type: runtime
    unpinned: false
    locations:
      - pyproject.toml
  - component: postgres
    version: "16.1"
    type: base-image
    unpinned: false
    locations:
      - docker-compose.yml
  - component: nginx
    version: "latest"
    type: base-image
    unpinned: true
    locations:
      - docker-compose.yml
gaps:
  - "Could not locate auth middleware"
```

Wrap output in a fenced yaml block. No prose before or after.
