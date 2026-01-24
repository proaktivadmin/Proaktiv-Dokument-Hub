<#
.SYNOPSIS
    Proof-of-concept test script to push email signature to a single user.
    Uses interactive authentication for testing purposes.

.DESCRIPTION
    This script:
    1. Connects to Exchange Online interactively
    2. Reads employee data from the database
    3. Generates the signature HTML
    4. Sets the signature for the specified user

.PARAMETER Email
    The email address of the employee to update.

.PARAMETER DryRun
    Preview changes without making updates.

.EXAMPLE
    .\Test-SignatureSync.ps1 -Email "froyland@proaktiv.no" -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Email,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n=== EMAIL SIGNATURE SYNC TEST ===" -ForegroundColor Cyan
Write-Host "Email: $Email"
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })"
Write-Host "=================================" -ForegroundColor Cyan

# Step 1: Get employee data
Write-Host "`n[1/4] Getting employee data from database..."
$pythonScript = @"
import sys, json, os
from sqlalchemy import create_engine, text
db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/dokument_hub')
engine = create_engine(db_url)
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT e.first_name, e.last_name, e.email, e.title, e.phone, e.profile_image_url,
               o.name as office_name, o.city, o.street_address, o.postal_code, o.phone as office_phone, o.email as office_email
        FROM employees e
        LEFT JOIN offices o ON e.office_id = o.id
        WHERE e.email = :email
    '''), {'email': '$Email'})
    row = result.fetchone()
    if row:
        print(json.dumps({
            'first_name': row[0], 'last_name': row[1], 'email': row[2], 'title': row[3],
            'phone': row[4], 'profile_image_url': row[5], 'office_name': row[6], 'office_city': row[7],
            'office_street': row[8], 'office_postal': row[9], 'office_phone': row[10], 'office_email': row[11]
        }))
    else:
        print('null')
"@

$jsonOutput = py -3.12 -c $pythonScript 2>&1
if ($LASTEXITCODE -ne 0 -or $jsonOutput -eq 'null') {
    Write-Host "  ERROR: Employee not found or database error" -ForegroundColor Red
    exit 1
}

$employee = $jsonOutput | ConvertFrom-Json
Write-Host "  Found: $($employee.first_name) $($employee.last_name)" -ForegroundColor Green
Write-Host "  Title: $($employee.title)"
Write-Host "  Phone: $($employee.phone)"
Write-Host "  Office: $($employee.office_name)"

# Step 2: Generate signature HTML
Write-Host "`n[2/4] Generating signature HTML..."
$templatePath = Join-Path $ScriptDir "templates\email-signature.html"
$template = Get-Content $templatePath -Raw -Encoding UTF8

$replacements = @{
    "{{DisplayName}}"    = "$($employee.first_name) $($employee.last_name)"
    "{{JobTitle}}"       = if ($employee.title) { $employee.title } else { "" }
    "{{Email}}"          = if ($employee.email) { $employee.email } else { "" }
    "{{MobilePhone}}"    = if ($employee.phone) { $employee.phone } else { "" }
    "{{OfficeName}}"     = if ($employee.office_name) { $employee.office_name } else { "" }
    "{{OfficeAddress}}"  = if ($employee.office_street) { $employee.office_street } else { "" }
    "{{OfficePostal}}"   = "$($employee.office_postal) $($employee.office_city)".Trim()
    "{{OfficePhone}}"    = if ($employee.office_phone) { $employee.office_phone } else { "" }
    "{{OfficeEmail}}"    = if ($employee.office_email) { $employee.office_email } else { "" }
    "{{ProfileUrl}}"     = if ($employee.profile_image_url) { $employee.profile_image_url } else { "" }
}

foreach ($key in $replacements.Keys) {
    $template = $template.Replace($key, $replacements[$key])
}

# Generate plain text version
$textSig = $template -replace "<[^>]+>", "" -replace "\s+", " " -replace "^\s+|\s+$", ""
$textSig = @"
$($employee.first_name) $($employee.last_name)
$($employee.title)

Mobil: $($employee.phone)
E-post: $($employee.email)

Proaktiv Eiendomsmegling $($employee.office_name)
$($employee.office_street), $($employee.office_postal) $($employee.office_city)
Tlf: $($employee.office_phone)
https://proaktiv.no
"@

Write-Host "  HTML Signature: $($template.Length) bytes" -ForegroundColor Green
Write-Host "  Text Signature: $($textSig.Length) bytes" -ForegroundColor Green

# Save preview
$previewPath = Join-Path (Split-Path -Parent $ScriptDir) "signature_preview_$($employee.email.Split('@')[0]).html"
$template | Out-File -FilePath $previewPath -Encoding UTF8
Write-Host "  Preview saved: $previewPath"

# Step 3: Connect to Exchange Online
Write-Host "`n[3/4] Connecting to Exchange Online..."
Write-Host "  (This will open a browser for authentication)" -ForegroundColor Yellow

try {
    # Use device code flow for authentication (works without window handle)
    Connect-ExchangeOnline -Organization "proaktiv.onmicrosoft.com" -ShowBanner:$false -Device
    Write-Host "  Connected successfully" -ForegroundColor Green
}
catch {
    Write-Host "  ERROR: Failed to connect: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Set the signature
Write-Host "`n[4/4] Setting email signature..."
try {
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would set signature for: $Email" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] AutoAddSignature: True"
        Write-Host "  [DRY RUN] AutoAddSignatureOnReply: True"
    }
    else {
        Set-MailboxMessageConfiguration -Identity $Email `
            -SignatureHtml $template `
            -SignatureText $textSig `
            -AutoAddSignature $true `
            -AutoAddSignatureOnMobile $true `
            -AutoAddSignatureOnReply $true
        
        Write-Host "  Signature set successfully!" -ForegroundColor Green
    }
}
catch {
    Write-Host "  ERROR: Failed to set signature: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Disconnect
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
}

Write-Host "`n=== COMPLETE ===" -ForegroundColor Cyan
