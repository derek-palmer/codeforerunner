# codeforerunner skill installer (Windows PowerShell)
# Detects installed agent CLIs and drops forerunner skills into each one.
#
# Usage:
#   .\install.ps1               # auto-detect all agents
#   .\install.ps1 -Only claude
#   .\install.ps1 -Only codex
#   .\install.ps1 -DryRun
#   .\install.ps1 -List
#   .\install.ps1 -Uninstall

param(
    [switch]$DryRun,
    [switch]$Uninstall,
    [switch]$List,
    [string[]]$Only = @()
)

$ErrorActionPreference = "Stop"

$RepoOwner  = "derek-palmer"
$RepoName   = "codeforerunner"
$RawBase    = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/main"
$GitHubUrl  = "https://github.com/$RepoOwner/$RepoName"

$SkillSlugs = @(
    "codeforerunner",
    "forerunner-scan",
    "forerunner-readme",
    "forerunner-api-docs",
    "forerunner-audit",
    "forerunner-changelog",
    "forerunner-check",
    "forerunner-diagrams",
    "forerunner-flows",
    "forerunner-init",
    "forerunner-review",
    "forerunner-stack-docs",
    "forerunner-version-audit"
)

# ── detect source ─────────────────────────────────────────────────────────────

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LocalSkills = Join-Path $ScriptDir "plugins\codeforerunner\skills"
$IsLocal = Test-Path $LocalSkills

# ── helpers ───────────────────────────────────────────────────────────────────

function Log   { param($msg) Write-Host "  $msg" }
function Ok    { param($msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Skip  { param($msg) Write-Host "  – $msg (skipped)" -ForegroundColor DarkGray }
function Err   { param($msg) Write-Host "  ✗ $msg" -ForegroundColor Red }

function ShouldInstall($agent) {
    $Only.Count -eq 0 -or $Only -contains $agent
}

function SkillDestClaude($slug) {
    "$env:USERPROFILE\.claude\plugins\codeforerunner\skills\$slug\SKILL.md"
}

function SkillDestCodex($slug) {
    "$env:USERPROFILE\.codex\skills\$slug\SKILL.md"
}

function CopySkill($slug, $dest) {
    if ($IsLocal) {
        $src = Join-Path $LocalSkills "$slug\SKILL.md"
        if (-not (Test-Path $src)) { Err "source not found: $src"; return $false }
        if (-not $DryRun) {
            New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
            Copy-Item $src $dest -Force
        }
    } else {
        $url = "$RawBase/plugins/codeforerunner/skills/$slug/SKILL.md"
        if (-not $DryRun) {
            New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
            Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        }
    }
    return $true
}

function HasCommand($name) {
    $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
}

# ── detection ─────────────────────────────────────────────────────────────────

$HasClaude = HasCommand "claude"
$HasCodex  = HasCommand "codex"
$HasGemini = HasCommand "gemini"

# ── list mode ─────────────────────────────────────────────────────────────────

if ($List) {
    Write-Host "codeforerunner skill installer — agent detection:"
    Write-Host ""
    Write-Host ("  {0,-12}  {1}" -f "claude", $(if ($HasClaude) {"detected ✓"} else {"not found"}))
    Write-Host ("  {0,-12}  {1}" -f "codex",  $(if ($HasCodex)  {"detected ✓"} else {"not found"}))
    Write-Host ("  {0,-12}  {1}" -f "gemini", $(if ($HasGemini) {"detected ✓"} else {"not found"}))
    Write-Host ""
    Write-Host "Skills ($($SkillSlugs.Count)):"
    foreach ($s in $SkillSlugs) { Write-Host "  /$s" }
    exit 0
}

# ── uninstall ─────────────────────────────────────────────────────────────────

if ($Uninstall) {
    Write-Host "codeforerunner — uninstalling skills"
    foreach ($slug in $SkillSlugs) {
        if (ShouldInstall "claude") {
            $d = SkillDestClaude $slug
            if (Test-Path $d) { if (-not $DryRun) { Remove-Item $d -Force }; Ok "removed $d" }
        }
        if (ShouldInstall "codex") {
            $d = SkillDestCodex $slug
            if (Test-Path $d) { if (-not $DryRun) { Remove-Item $d -Force }; Ok "removed $d" }
        }
    }
    Write-Host "done"
    exit 0
}

# ── install ───────────────────────────────────────────────────────────────────

$Installed = @()
$Skipped   = @()

Write-Host "codeforerunner — installing skills"
Write-Host ""
if ($DryRun) { Write-Host "  (dry-run — no files written)" }
Write-Host ""

# Claude Code
if (ShouldInstall "claude") {
    if ($HasClaude -or $Only.Count -gt 0) {
        Write-Host "Claude Code:"
        if (-not $DryRun) {
            $pluginDir = "$env:USERPROFILE\.claude\plugins\codeforerunner"
            New-Item -ItemType Directory -Force -Path $pluginDir | Out-Null
            $manifestSrc = if ($IsLocal) { Join-Path $ScriptDir ".claude-plugin\plugin.json" } else { "$RawBase/.claude-plugin/plugin.json" }
            if ($IsLocal) { Copy-Item $manifestSrc "$pluginDir\plugin.json" -Force }
            else { Invoke-WebRequest -Uri $manifestSrc -OutFile "$pluginDir\plugin.json" -UseBasicParsing }
        }
        foreach ($slug in $SkillSlugs) {
            $dest = SkillDestClaude $slug
            if (CopySkill $slug $dest) { Ok $dest; $Installed += "claude/$slug" }
        }
    } else {
        Skip "claude (not detected; use -Only claude to force)"
        $Skipped += "claude"
    }
    Write-Host ""
}

# Codex
if (ShouldInstall "codex") {
    if ($HasCodex -or $Only.Count -gt 0) {
        Write-Host "Codex CLI:"
        foreach ($slug in $SkillSlugs) {
            $dest = SkillDestCodex $slug
            if (CopySkill $slug $dest) { Ok $dest; $Installed += "codex/$slug" }
        }
    } else {
        Skip "codex (not detected; use -Only codex to force)"
        $Skipped += "codex"
    }
    Write-Host ""
}

# Gemini — delegates to native extension install
if (ShouldInstall "gemini") {
    if ($HasGemini -or $Only.Count -gt 0) {
        Write-Host "Gemini CLI:"
        if (-not $DryRun) {
            try {
                & gemini extensions install $GitHubUrl
                Ok "installed via gemini extensions install"
                $Installed += "gemini"
            } catch {
                Err "gemini extensions install failed: $_"
            }
        } else {
            Log "would run: gemini extensions install $GitHubUrl"
        }
    } else {
        Skip "gemini (not detected; use -Only gemini to force)"
        $Skipped += "gemini"
    }
    Write-Host ""
}

# ── summary ───────────────────────────────────────────────────────────────────

Write-Host "Summary:"
if ($Installed.Count -gt 0) {
    $agents = ($Installed | ForEach-Object { $_.Split('/')[0] } | Sort-Object -Unique) -join " "
    Write-Host "  installed for: $agents"
}
if ($Skipped.Count -gt 0) {
    Write-Host "  skipped: $($Skipped -join ', ')"
}
if ($Installed.Count -eq 0 -and $Skipped.Count -eq 0) {
    Write-Host "  no agents detected; use -Only <agent> to install for a specific agent"
    Write-Host "  supported: claude, codex, gemini"
}
Write-Host ""
Write-Host "  To add forerunner to a project: forerunner doctor --fix"
Write-Host "  Docs: $GitHubUrl"
