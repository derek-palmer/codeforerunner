# codeforerunner skill installer — thin Node.js shim (Windows PowerShell).
# Delegates to bin\install.js when run from a local clone,
# or fetches and runs it via npx from a remote invocation.
#
# Usage (local clone):
#   .\install.ps1 [flags]
#
# All flags (--dry-run, --force, --only, --all, --minimal, --list, --no-color,
#             --skip-skills, --uninstall, -h/--help) are forwarded to bin\install.js.

param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)

$ErrorActionPreference = "Stop"

# Security: pinned to a specific version so one-liners don't execute unreviewed code.
$NpmPkg  = "codeforerunner@0.4.10"
$Repo    = "derek-palmer/codeforerunner"
$RepoTag = "v0.4.10"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LocalJs = Join-Path $ScriptDir "bin\install.js"

if (Test-Path $LocalJs) {
    & node $LocalJs @Args
} else {
    # Primary: npm registry. Fallback: GitHub source (in case npm is down).
    $npmUp = $false
    try {
        $null = Invoke-WebRequest -Uri "https://registry.npmjs.org/$NpmPkg/latest" -Method Head -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        $npmUp = $true
    } catch {}
    if ($npmUp) {
        & npx --yes $NpmPkg -- @Args
    } else {
        & npx --yes "github:${Repo}#${RepoTag}" -- @Args
    }
}
