# Task: Generate Version Audit

Scans the repository for every pinned runtime, base image, language version,
container version, and key dependency version. Cross-references against
end-of-life data and produces a structured support status report.

EOL data source: https://endoflife.date
Re-run at least monthly. The check task flags this as stale after 30 days.

## Input
- Scan result (pinned_versions_found block)
- All version-bearing files:
  - Dockerfile, docker-compose.yml, *.dockerfile
  - package.json, package-lock.json, .nvmrc, .node-version
  - pyproject.toml, requirements.txt, Pipfile, .python-version, uv.lock
  - go.mod, Cargo.toml
  - *.tf (provider versions, Terraform version constraints)
  - .github/workflows/*.yml (runner images, action versions, language setup steps)
  - *.yaml Kubernetes manifests (image tags)

## Step 1: Extract All Versions
For each pinned version record:
- component: what it is (node, python, postgres, nginx, ubuntu, terraform)
- version: exact pinned version string
- location: file path where found
- type: runtime | base-image | infrastructure-tool | ci-runner | key-dependency

If a version is unpinned (latest, *, >=3.0), record as UNPINNED -- risk flag regardless of EOL.

## Step 2: Determine Support Status

| Status          | Label              | Condition                              |
|-----------------|--------------------|----------------------------------------|
| EOL             | EOL                | EOL date has passed                    |
| APPROACHING_EOL | Approaching EOL    | EOL date is within 6 months from today |
| SUPPORTED       | Supported          | EOL date is more than 6 months away    |
| UNPINNED        | Unpinned           | No specific version pinned             |
| UNKNOWN         | Unknown            | EOL data not available                 |

## Rules
- Claims must derive from provided files. If EOL data is unavailable, mark as UNKNOWN.
- Never fabricate EOL dates -- mark as Unknown if not confident
- Always separate EOL Date (past) from Support Ends (future)
- Unpinned versions are always flagged regardless of what they might resolve to
- Upgrade recommendations must specify exact version targets, never say upgrade to latest
- For major-version breaking upgrades, always note it is a breaking change

## Output Format

<!-- output: docs/version-audit.md -->

# Version Audit
Generated: YYYY-MM-DD
_Re-run monthly or when versions change. Flagged as stale after 30 days._

## Summary
| Status                              | Count |
|-------------------------------------|-------|
| EOL                                 | N     |
| Approaching EOL (within 6 months)   | N     |
| Supported                           | N     |
| Unpinned                            | N     |
| Unknown                             | N     |

> Action required: X component(s) are EOL and should be upgraded immediately.
> (Only render this line if EOL count > 0)

## Runtimes
| Component | Pinned Version | Status        | EOL Date | Support Ends | Location         |
|-----------|----------------|---------------|----------|--------------|------------------|
| Python    | 3.9.18         | EOL           | Oct 2025 | --           | pyproject.toml   |
| Node.js   | 20.11.0        | Supported     | --       | Apr 2026     | package.json     |

## Base Images
| Component | Pinned Version | Status    | EOL Date | Support Ends | Location           |
|-----------|----------------|-----------|----------|--------------|---------------------------------|
| python    | 3.9-slim       | EOL       | Oct 2025 | --           | Dockerfile         |
| postgres  | 16.1           | Supported | --       | Nov 2029     | docker-compose.yml |
| nginx     | latest         | Unpinned  | --       | --           | docker-compose.yml |

## Infrastructure Tools
| Component | Pinned Version | Status          | EOL Date | Support Ends | Location                      |
|-----------|----------------|-----------------|----------|--------------|-------------------------------|
| Terraform | 1.5.7          | Approaching EOL | Jun 2025 | --           | .github/workflows/deploy.yml  |

## CI Runners
| Component       | Pinned Version | Status    | EOL Date | Support Ends | Location                    |
|-----------------|----------------|-----------|----------|--------------|-----------------------------||
| ubuntu runner   | 22.04          | Supported | --       | Apr 2027     | .github/workflows/ci.yml    |

## Key Dependencies
| Component | Pinned Version | Status          | EOL Date | Support Ends | Location          |
|-----------|----------------|-----------------|----------|--------------|-------------------|
| fastapi   | 0.95.2         | Unknown         | --       | --           | requirements.txt  |
| pydantic  | 1.10.13        | Approaching EOL | Jun 2025 | --           | requirements.txt  |

## Unpinned Versions (Risk Flag)
| Component | Found Value | Location           | Risk                                              |
|-----------|-------------|--------------------|---------------------------------------------------|
| nginx     | latest      | docker-compose.yml | Unpredictable upgrades, no EOL assessment possible|

## Upgrade Recommendations

### Immediate Action Required (EOL)
- **Python 3.9** -> Upgrade to 3.12 (LTS, supported until Oct 2028). Update pyproject.toml and Dockerfile.

### Plan Upgrade Within 6 Months (Approaching EOL)
- **Terraform 1.5.x** -> Upgrade to 1.7.x (current stable). Update workflow pin.
- **pydantic v1** -> Migrate to pydantic v2. NOTE: breaking change.

---
_EOL data sourced from https://endoflife.date_
_EOL Date = past date for already-EOL versions. Support Ends = future date for in-support versions._
_This audit reflects pinned versions only -- does not scan transitive dependencies._
