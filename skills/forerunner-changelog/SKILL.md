---
name: forerunner-changelog
description: Generate a Keep-a-Changelog entry from git history since the last release tag. Use when the user wants to write a CHANGELOG entry or document what changed in a release.
---

# forerunner-changelog

Produces a Keep-a-Changelog–style entry for changes since the last release tag. Does not require a full scan — operates on git log and diff output.

## Activate when

User asks to: write the changelog, generate a changelog entry, document the release, write what changed since vX.Y.Z.

## Collect this context

- `git log v<last-tag>...HEAD --oneline` output
- `git diff v<last-tag>...HEAD --stat` output
- (Optional) recent commit messages with full bodies for context
- (Optional) existing `CHANGELOG.md` for format reference

## Execute

Run `forerunner generate --prompt-only changelog` — outputs the assembled prompt bundle to stdout. Read this output and execute the documentation task it describes.

Without CLI, get the prompt from:
- `src/codeforerunner/prompts/tasks/changelog.md`
- `src/codeforerunner/prompts/system/base.md`

## Output

A formatted `## [X.Y.Z] — YYYY-MM-DD` section with `### Added`, `### Changed`, `### Fixed`, `### Removed` subsections. Infer the version from the tag pattern if not specified. Suitable for direct insertion into `CHANGELOG.md`.
