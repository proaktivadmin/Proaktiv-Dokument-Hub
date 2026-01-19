<#
.SYNOPSIS
  Run the Proaktiv directory sync (offices + employees).

.DESCRIPTION
  Convenience wrapper around:
    py -3.12 -m scripts.sync_proaktiv_directory

  Designed for:
  - Safe, bounded runs (rate-limited + max pages/runtime)
  - Easy switching between Local (Docker) DB and Railway DB

  IMPORTANT:
  - Do NOT commit secrets (Railway DB URLs, passwords, API keys).
  - Prefer setting Railway DB URL via env var: $env:RAILWAY_DATABASE_URL

.EXAMPLE
  # Local bounded run (writes to local docker db)
  .\backend\scripts\run_proaktiv_directory_sync.ps1 -Preset all -Migrate -Overwrite

.EXAMPLE
  # Railway bounded run (writes to Railway DB)
  $env:RAILWAY_DATABASE_URL = "postgresql://.../..."
  .\backend\scripts\run_proaktiv_directory_sync.ps1 -TargetDb railway -Migrate -Preset all -DeepEmployees:$true -Overwrite
#>

[CmdletBinding()]
param(
  # Preset lists of start URLs (ignored if -Start is provided)
  [ValidateSet("all", "rogaland")]
  [string]$Preset = "all",

  # Custom start URLs (repeatable): -Start "https://..." "https://..."
  [string[]]$Start,

  # Where to write data
  [ValidateSet("local", "railway")]
  [string]$TargetDb = "local",

  # Optional explicit DB url override (use with care; ends up in shell history)
  [string]$DatabaseUrl,

  # If -TargetDb railway and -DatabaseUrl not provided, read from env var
  [string]$RailwayDatabaseUrlEnvVar = "RAILWAY_DATABASE_URL",

  # Run Alembic migrations before scraping
  [switch]$Migrate,

  # Safety knobs (bounded by default)
  [int]$DelayMs = 1500,
  [int]$MaxPages = 220,
  [int]$MaxOfficePages = 24,
  [int]$MaxEmployeePages = 220,
  [int]$MaxRuntimeMinutes = 40,

  # Scraper behavior
  [bool]$DeepEmployees = $true,
  [switch]$Overwrite,
  [switch]$DryRun,
  [switch]$UseFirecrawl
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Mask-DatabaseUrl([string]$Url) {
  if (-not $Url) { return "" }
  # Mask password in: postgresql://user:pass@host:port/db?...
  return ($Url -replace "://([^:/?#]+):([^@/?#]+)@", "://`$1:***@")
}

function Get-PresetStartUrls([string]$PresetName) {
  switch ($PresetName) {
    "rogaland" {
      return @(
        "https://proaktiv.no/eiendomsmegler/sandnes",
        "https://proaktiv.no/eiendomsmegler/stavanger",
        "https://proaktiv.no/eiendomsmegler/sola",
        "https://proaktiv.no/eiendomsmegler/j%C3%A6ren"
      )
    }
    default {
      # "all" – matches the most common directory entry points
      return @(
        "https://proaktiv.no/eiendomsmegler/oslo",
        "https://proaktiv.no/eiendomsmegler/drammen-lier",
        "https://proaktiv.no/eiendomsmegler/lillestr%C3%B8m",
        "https://proaktiv.no/eiendomsmegler/l%C3%B8renskog",
        "https://proaktiv.no/eiendomsmegler/bergen",
        "https://proaktiv.no/eiendomsmegler/voss",
        "https://proaktiv.no/eiendomsmegler/stavanger",
        "https://proaktiv.no/eiendomsmegler/sandnes",
        "https://proaktiv.no/eiendomsmegler/sola",
        "https://proaktiv.no/eiendomsmegler/trondheim",
        "https://proaktiv.no/eiendomsmegler/%C3%A5lesund",
        "https://proaktiv.no/eiendomsmegler/skien",
        "https://proaktiv.no/eiendomsmegler/haugesund",
        "https://proaktiv.no/eiendomsmegler/sarpsborg",
        "https://proaktiv.no/eiendomsmegler/kristiansand",
        # Optional "corporate" directory (not under /eiendomsmegler)
        "https://proaktiv.no/om-oss/kjedeledelse"
      )
    }
  }
}

# Resolve backend dir (script lives in backend/scripts)
$backendDir = Resolve-Path (Join-Path $PSScriptRoot "..")

Push-Location $backendDir
try {
  if ($TargetDb -eq "railway") {
    $db = $DatabaseUrl
    if (-not $db) {
      $db = [Environment]::GetEnvironmentVariable($RailwayDatabaseUrlEnvVar)
    }
    if (-not $db) {
      throw "TargetDb=railway requires -DatabaseUrl OR env var $RailwayDatabaseUrlEnvVar to be set."
    }
    $env:DATABASE_URL = $db
  }

  $effectiveDbUrl = $env:DATABASE_URL
  if (-not $effectiveDbUrl) {
    # Let app/config.py load backend/.env; we only print a masked value here.
    $effectiveDbUrl = (& py -3.12 -c "from app.config import settings; print(settings.DATABASE_URL)") -join ""
  }
  Write-Host ("[Proaktiv Sync] TargetDb={0} DB={1}" -f $TargetDb, (Mask-DatabaseUrl $effectiveDbUrl))

  if ($Migrate) {
    Write-Host "[Proaktiv Sync] Running migrations (alembic upgrade head)..."
    & py -3.12 -m alembic upgrade head
  }

  $startUrls = @()
  if ($Start -and $Start.Count -gt 0) {
    $startUrls = $Start
  } else {
    $startUrls = Get-PresetStartUrls -PresetName $Preset
  }

  $args = @(
    "--delay-ms", $DelayMs,
    "--max-pages", $MaxPages,
    "--max-office-pages", $MaxOfficePages,
    "--max-employee-pages", $MaxEmployeePages,
    "--max-runtime-minutes", $MaxRuntimeMinutes
  )

  foreach ($u in $startUrls) {
    if ($u) { $args += @("--start", $u) }
  }

  if ($UseFirecrawl) { $args += "--use-firecrawl" }
  if ($DeepEmployees) { $args += "--deep-employees" }
  if ($Overwrite) { $args += "--overwrite" }
  if ($DryRun) { $args += "--dry-run" }

  Write-Host ("[Proaktiv Sync] Running: py -3.12 -m scripts.sync_proaktiv_directory {0}" -f ($args -join " "))
  & py -3.12 -m scripts.sync_proaktiv_directory @args
}
finally {
  Pop-Location
}

