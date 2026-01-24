<#
.SYNOPSIS
    Identifies employees with mismatched User Principal Names between Entra ID and the local database.

.DESCRIPTION
    This script:
    1. Pulls all active employees from the local PostgreSQL database
    2. Fetches their Entra ID accounts (by email)
    3. Compares the User Principal Name (UPN) in Entra ID with the email in the database
    4. Flags accounts where UPN != database email (these will fail SSO to Vitec Next)

.PARAMETER TenantId
    Azure AD tenant ID (GUID). Required for authentication.

.PARAMETER ClientId
    Azure App Registration client ID (GUID). Required for authentication.

.PARAMETER CertificateThumbprint
    Thumbprint of the certificate for authentication.

.PARAMETER ClientSecret
    Client secret for authentication.

.PARAMETER DatabaseUrl
    PostgreSQL connection string.
    Defaults to DATABASE_URL environment variable.

.PARAMETER OutputCsv
    Path to output CSV file with results.
    Default: upn-mismatch-report.csv

.EXAMPLE
    .\Check-UPNMismatch.ps1 -TenantId "xxx" -ClientId "yyy" -CertificateThumbprint "zzz"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TenantId,

    [Parameter(Mandatory = $true)]
    [string]$ClientId,

    [Parameter(Mandatory = $false)]
    [string]$CertificateThumbprint,

    [Parameter(Mandatory = $false)]
    [string]$ClientSecret,

    [Parameter(Mandatory = $false)]
    [string]$DatabaseUrl = $env:DATABASE_URL,

    [Parameter(Mandatory = $false)]
    [string]$OutputCsv = "upn-mismatch-report.csv"
)

$ErrorActionPreference = "Stop"
$script:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ============================================================================
# STEP 1: Get employees from database
# ============================================================================
Write-Host "`n[1/3] Fetching employees from database..." -ForegroundColor Cyan

$pythonScript = @"
import sys
import json
sys.path.insert(0, '$($script:ScriptDir -replace '\\', '/')/..')
from sqlalchemy import create_engine, text
import os

db_url = os.environ.get('DATABASE_URL', '$DatabaseUrl')
if not db_url:
    print(json.dumps({'error': 'DATABASE_URL not set'}))
    sys.exit(1)

engine = create_engine(db_url)
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT
            e.id,
            e.first_name,
            e.last_name,
            e.email,
            e.vitec_employee_id,
            e.employee_type,
            e.status,
            o.name as office_name
        FROM employees e
        LEFT JOIN offices o ON e.office_id = o.id
        WHERE e.email IS NOT NULL
          AND e.status = 'active'
          AND e.employee_type = 'internal'
        ORDER BY e.last_name, e.first_name
    '''))
    employees = []
    for row in result:
        employees.append({
            'id': str(row[0]),
            'first_name': row[1],
            'last_name': row[2],
            'email': row[3],
            'vitec_id': row[4],
            'employee_type': row[5],
            'status': row[6],
            'office': row[7]
        })
    print(json.dumps(employees))
"@

$employees = python -c $pythonScript | ConvertFrom-Json

if ($employees.error) {
    Write-Host "Error fetching employees: $($employees.error)" -ForegroundColor Red
    exit 1
}

Write-Host "  Found $($employees.Count) active internal employees in database" -ForegroundColor Green

# ============================================================================
# STEP 2: Connect to Microsoft Graph
# ============================================================================
Write-Host "`n[2/3] Connecting to Microsoft Graph..." -ForegroundColor Cyan

# Install module if needed
if (-not (Get-Module -ListAvailable -Name Microsoft.Graph.Users)) {
    Write-Host "  Installing Microsoft.Graph.Users module..." -ForegroundColor Yellow
    Install-Module Microsoft.Graph.Users -Scope CurrentUser -Force
}

Import-Module Microsoft.Graph.Users -ErrorAction Stop

# Determine authentication method
if ($CertificateThumbprint) {
    Write-Host "  Authenticating with certificate..." -ForegroundColor Gray
    Connect-MgGraph -TenantId $TenantId -ClientId $ClientId -CertificateThumbprint $CertificateThumbprint -NoWelcome
} elseif ($ClientSecret -or $env:ENTRA_CLIENT_SECRET) {
    $secret = if ($ClientSecret) { $ClientSecret } else { $env:ENTRA_CLIENT_SECRET }
    Write-Host "  Authenticating with client secret..." -ForegroundColor Gray
    $secureSecret = ConvertTo-SecureString $secret -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential($ClientId, $secureSecret)
    Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential -NoWelcome
} else {
    Write-Host "  No credentials provided. Trying interactive login..." -ForegroundColor Yellow
    Connect-MgGraph -TenantId $TenantId -Scopes "User.Read.All" -NoWelcome
}

Write-Host "  Connected to Microsoft Graph" -ForegroundColor Green

# ============================================================================
# STEP 3: Compare UPNs
# ============================================================================
Write-Host "`n[3/3] Comparing UPNs with database emails..." -ForegroundColor Cyan

$results = @()
$matchCount = 0
$mismatchCount = 0
$notFoundCount = 0

foreach ($emp in $employees) {
    $dbEmail = $emp.email.ToLower().Trim()
    $displayName = "$($emp.first_name) $($emp.last_name)"

    Write-Host "  Checking: $displayName ($dbEmail)..." -NoNewline

    # Try to find user in Entra by UPN first
    $entraUser = $null
    try {
        $entraUser = Get-MgUser -UserId $dbEmail -Property "Id,UserPrincipalName,Mail,DisplayName" -ErrorAction SilentlyContinue
    } catch {
        # UPN lookup failed, try by mail property
    }

    # If not found by UPN, search by mail property
    if (-not $entraUser) {
        try {
            $searchResult = Get-MgUser -Filter "mail eq '$dbEmail'" -Property "Id,UserPrincipalName,Mail,DisplayName" -ErrorAction SilentlyContinue
            if ($searchResult) {
                $entraUser = $searchResult | Select-Object -First 1
            }
        } catch {
            # Search also failed
        }
    }

    # Also try proxyAddresses
    if (-not $entraUser) {
        try {
            $searchResult = Get-MgUser -Filter "proxyAddresses/any(p:p eq 'smtp:$dbEmail')" -Property "Id,UserPrincipalName,Mail,DisplayName" -ErrorAction SilentlyContinue
            if ($searchResult) {
                $entraUser = $searchResult | Select-Object -First 1
            }
        } catch {
            # Search also failed
        }
    }

    $result = [PSCustomObject]@{
        EmployeeId      = $emp.id
        Name            = $displayName
        DatabaseEmail   = $dbEmail
        EntraUPN        = ""
        EntraMail       = ""
        Status          = ""
        Issue           = ""
        Office          = $emp.office
        VitecId         = $emp.vitec_id
    }

    if (-not $entraUser) {
        $result.Status = "NOT_FOUND"
        $result.Issue = "No Entra ID account found for this email"
        Write-Host " NOT FOUND" -ForegroundColor Red
        $notFoundCount++
    } else {
        $result.EntraUPN = $entraUser.UserPrincipalName
        $result.EntraMail = $entraUser.Mail

        $upn = $entraUser.UserPrincipalName.ToLower().Trim()
        $mail = if ($entraUser.Mail) { $entraUser.Mail.ToLower().Trim() } else { "" }

        if ($upn -eq $dbEmail) {
            $result.Status = "OK"
            $result.Issue = ""
            Write-Host " OK" -ForegroundColor Green
            $matchCount++
        } elseif ($mail -eq $dbEmail) {
            $result.Status = "UPN_MISMATCH"
            $result.Issue = "UPN ($upn) differs from DB email - SSO will fail!"
            Write-Host " MISMATCH: UPN=$upn" -ForegroundColor Yellow
            $mismatchCount++
        } else {
            $result.Status = "UPN_MISMATCH"
            $result.Issue = "Neither UPN ($upn) nor Mail ($mail) match DB email"
            Write-Host " MISMATCH: UPN=$upn, Mail=$mail" -ForegroundColor Red
            $mismatchCount++
        }
    }

    $results += $result

    # Small delay to avoid throttling
    Start-Sleep -Milliseconds 100
}

# ============================================================================
# Output Report
# ============================================================================
Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "UPN MISMATCH REPORT" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host "`nSummary:" -ForegroundColor White
Write-Host "  Total employees checked:  $($employees.Count)"
Write-Host "  Matching (OK):            $matchCount" -ForegroundColor Green
Write-Host "  Mismatched (SSO ISSUE):   $mismatchCount" -ForegroundColor $(if ($mismatchCount -gt 0) { "Yellow" } else { "Green" })
Write-Host "  Not found in Entra:       $notFoundCount" -ForegroundColor $(if ($notFoundCount -gt 0) { "Red" } else { "Green" })

# Show affected users
$affected = $results | Where-Object { $_.Status -eq "UPN_MISMATCH" }
if ($affected.Count -gt 0) {
    Write-Host "`n`nAFFECTED USERS (UPN != Database Email):" -ForegroundColor Yellow
    Write-Host "-" * 70 -ForegroundColor Yellow

    foreach ($user in $affected) {
        Write-Host "`n  $($user.Name)" -ForegroundColor White
        Write-Host "    Office:         $($user.Office)"
        Write-Host "    Database Email: $($user.DatabaseEmail)" -ForegroundColor Cyan
        Write-Host "    Entra UPN:      $($user.EntraUPN)" -ForegroundColor Yellow
        Write-Host "    Entra Mail:     $($user.EntraMail)"
        Write-Host "    Issue:          $($user.Issue)" -ForegroundColor Red
    }
}

# Show not found users
$notFound = $results | Where-Object { $_.Status -eq "NOT_FOUND" }
if ($notFound.Count -gt 0) {
    Write-Host "`n`nNOT FOUND IN ENTRA ID:" -ForegroundColor Red
    Write-Host "-" * 70 -ForegroundColor Red

    foreach ($user in $notFound) {
        Write-Host "  $($user.Name) - $($user.DatabaseEmail) ($($user.Office))"
    }
}

# Export to CSV
$outputPath = Join-Path $script:ScriptDir $OutputCsv
$results | Export-Csv -Path $outputPath -NoTypeInformation -Encoding UTF8

Write-Host "`n`nFull report exported to: $outputPath" -ForegroundColor Cyan

# Disconnect
Disconnect-MgGraph -ErrorAction SilentlyContinue

Write-Host "`nDone!" -ForegroundColor Green
