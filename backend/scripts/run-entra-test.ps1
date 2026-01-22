# Load .env file and run Entra ID sync dry-run test
Set-Location $PSScriptRoot\..

# Ensure DATABASE_URL points to local Docker PostgreSQL
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/dokument_hub"

# Load .env
$envFile = ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Strip surrounding quotes if present
            $value = $value -replace '^["'']|["'']$', ''
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
    Write-Host "Loaded .env file" -ForegroundColor Green
}

Write-Host ""
Write-Host "Running Entra ID sync dry-run test for: froyland@proaktiv.no" -ForegroundColor Cyan
Write-Host ""

# Run the sync script with dry-run
# Pass -ClientSecret to use the Secret parameter set
# Skip signature to avoid Exchange Online interactive auth requirement
& "$PSScriptRoot\Sync-EntraIdEmployees.ps1" `
    -TenantId $env:ENTRA_TENANT_ID `
    -ClientId $env:ENTRA_CLIENT_ID `
    -ClientSecret $env:ENTRA_CLIENT_SECRET `
    -Organization $env:ENTRA_ORGANIZATION `
    -FilterEmail "froyland@proaktiv.no" `
    -SkipSignature `
    -DryRun `
    -Force
