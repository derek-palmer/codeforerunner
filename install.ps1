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

$Repo    = "derek-palmer/codeforerunner"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LocalJs = Join-Path $ScriptDir "bin\install.js"

if (Test-Path $LocalJs) {
    & node $LocalJs @Args
} else {
    & npx -y "github:$Repo" -- @Args
}
