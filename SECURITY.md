# Security Policy

## Reporting a vulnerability

Please report security issues privately through GitHub's **private vulnerability
reporting** for this repository:

- Go to the repository's **Security** tab → **Report a vulnerability**, or visit
  <https://github.com/derek-palmer/codeforerunner/security/advisories/new>.

This opens a private advisory visible only to the maintainers. Please do **not**
open a public issue for a suspected vulnerability. We aim to acknowledge a report
within a few days and will coordinate a fix and disclosure with you.

## Package capabilities

`codeforerunner` is distributed as an **installer**: the npm package
(`bin/install.js`) places codeforerunner's slash-command skills into the
configuration directories of the agent CLIs you already use. By its nature an
installer needs broader system access than a typical library, so supply-chain
scanners (e.g. Socket.dev) flag the following capabilities. They are expected
and intrinsic to what the tool does:

- **Network access** — fetches skill content and probes the npm registry to
  resolve what to install. No telemetry is sent; the package collects nothing
  about you.
- **Filesystem access** — writes skill files under your home directory (for
  example `~/.codex/…`, `~/.claude/…`). Installs are idempotent and confined to
  codeforerunner-managed regions; existing unmanaged content is never
  overwritten.
- **Process/shell access** — detects which agent CLIs are present and invokes
  their own installers (for example `gemini extensions install`).

The package declares **no runtime dependencies**, runs **no install scripts**
(no `postinstall`), and is published with **npm provenance**. If you prefer not
to grant these capabilities, you can inspect `bin/install.js` (it is plain,
unminified JavaScript) or install individual skills manually.

## Supported versions

Only the latest published version receives security fixes.
