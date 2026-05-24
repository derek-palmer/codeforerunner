# Task: Generate Changelog Entry

Produces a Keep-a-Changelog–style entry for changes since the last release tag.
Does not require a full scan; operates on git log and diff output.

## Input
- `git log v<last-tag>...HEAD --oneline` output
- `git diff v<last-tag>...HEAD --stat` output
- Existing CHANGELOG.md (if present) — for format reference and to avoid duplicating entries
- pyproject.toml / package.json / go.mod — for current version number

## Instructions

1. Determine the version to document (current package version or next semver bump if unreleased)
2. Group commits into Keep-a-Changelog categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. For each commit, write one concise bullet describing the user-visible change — not the implementation detail
4. Skip chore/CI/formatting commits unless they affect behaviour visible to users
5. If the version is not yet tagged, use `[Unreleased]` as the heading
6. Append a comparison link at the footer following the existing pattern in CHANGELOG.md

## Rules
- Claims must derive from provided commits and diff. Do not invent changes.
- Bullets describe what changed from the user's perspective, not how.
- One bullet per logical change; collapse trivially related commits.
- Do not include commit hashes in bullets.

## Output Format

```markdown
## [<version>] — <YYYY-MM-DD>

### Added
- ...

### Fixed
- ...

### Changed
- ...
```

Omit empty sections. Append footer link following the existing CHANGELOG.md pattern.
