param(
    [Parameter(Mandatory = $true)]
    [string]$Message,

    [Parameter(Mandatory = $true)]
    [string[]]$Paths,

    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Message)) {
    throw "Commit message cannot be empty."
}

if ($Paths.Count -eq 0) {
    throw "Provide at least one path."
}

foreach ($path in $Paths) {
    if ([string]::IsNullOrWhiteSpace($path)) {
        throw "Path list contains an empty value."
    }
}

Write-Host "Validating repository state..." -ForegroundColor Cyan
git rev-parse --is-inside-work-tree | Out-Null

Write-Host "Paths to stage:" -ForegroundColor Cyan
$Paths | ForEach-Object { Write-Host " - $_" }

if ($DryRun) {
    Write-Host "`n[DRY RUN] Would run:" -ForegroundColor Yellow
    Write-Host "git add -- <paths>" -ForegroundColor Yellow
    Write-Host "git commit -m <message>" -ForegroundColor Yellow
    exit 0
}

Write-Host "`nStaging selected paths..." -ForegroundColor Cyan
git add -- @Paths

Write-Host "Creating commit..." -ForegroundColor Cyan
git commit -m $Message

Write-Host "`nDone. Current status:" -ForegroundColor Green
git status --short
