# Task: Security and Dependency Audit

Produces a structured security and dependency audit report for the repository.
Requires scan result as input.

## Input
- Scan result
- Manifest/lockfiles: package.json, package-lock.json, pyproject.toml, poetry.lock, go.mod, go.sum, Cargo.toml, Cargo.lock, requirements*.txt, Gemfile.lock
- CI/CD workflow files
- Dockerfile / compose files if present
- .env.example or documented env vars

## Instructions

1. **Dependency inventory** — list all direct dependencies with pinned version (or "unpinned" if range only)
2. **Known-vulnerable versions** — flag any dependency version with a published CVE you know of; note CVE ID and severity
3. **Outdated pins** — flag dependencies pinned to versions that are end-of-life or significantly behind latest stable
4. **Supply-chain risks** — flag: unpinned versions in CI (`uses: action@main`), `curl | bash` install patterns, unverified download steps
5. **Secrets surface** — enumerate all env vars the repo reads; flag any that look like secrets hardcoded in non-.env files
6. **Auth / input validation** — from entry-point and API handler files, flag: missing input sanitisation, direct string interpolation into shell commands or SQL, unauthenticated endpoints

## Rules
- Claims must derive from provided files. If evidence is absent, omit or document in `## Gaps`.
- Do not fabricate CVE IDs. If you are not certain a CVE applies, note the concern without a CVE reference.
- Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO.
- Only report findings with evidence; do not speculate.

## Output Format

```
## Dependency Inventory
| Package | Version | Pinned? |
|---------|---------|---------|
...

## Findings
### [SEVERITY] Title
- **Evidence**: file:line or package@version
- **Detail**: what the risk is
- **Remediation**: concrete fix

## Gaps
- Items not assessable from provided files
```
