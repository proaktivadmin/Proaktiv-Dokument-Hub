<#
.SYNOPSIS
    Syncs employee data from PostgreSQL to Microsoft Entra ID and Exchange Online.

.DESCRIPTION
    This script:
    1. Reads active employees from the local PostgreSQL database
    2. Updates their profiles in Microsoft Entra ID (job title, phone, etc.)
    3. Uploads profile photos to Entra ID
    4. Deploys email signatures to Exchange Online

    Supports both certificate and client secret authentication.
    Always use -DryRun first to preview changes.

.PARAMETER TenantId
    Azure AD tenant ID (GUID). Required for authentication.

.PARAMETER ClientId
    Azure App Registration client ID (GUID). Required for authentication.

.PARAMETER CertificateThumbprint
    Thumbprint of the certificate for authentication.
    Mutually exclusive with -ClientSecret.

.PARAMETER ClientSecret
    Client secret for authentication.
    Mutually exclusive with -CertificateThumbprint.
    Can also be set via ENTRA_CLIENT_SECRET environment variable.

.PARAMETER Organization
    Microsoft 365 organization domain (e.g., "proaktiv.onmicrosoft.com").
    Required for Exchange Online connection.

.PARAMETER DatabaseUrl
    PostgreSQL connection string.
    Defaults to DATABASE_URL environment variable.

.PARAMETER FilterEmail
    Process only employees matching this email address.
    Useful for testing with a single user.

.PARAMETER SkipProfile
    Skip Entra ID profile updates (job title, phone, etc.).

.PARAMETER SkipPhoto
    Skip profile photo uploads.

.PARAMETER SkipSignature
    Skip Exchange Online signature deployment.

.PARAMETER SignatureTemplate
    Path to custom HTML signature template.
    Defaults to templates/email-signature.html.

.PARAMETER DelayMs
    Delay in milliseconds between API calls.
    Default: 150. Increase if hitting rate limits.

.PARAMETER DryRun
    Preview changes without making any updates.
    Strongly recommended for first runs.

.PARAMETER Force
    Skip confirmation prompts.

.PARAMETER LogPath
    Path for log file output.
    Default: logs/entra-sync-{timestamp}.log

.EXAMPLE
    # Dry run with single user (test mode)
    .\Sync-EntraIdEmployees.ps1 -TenantId "xxx" -ClientId "yyy" `
        -CertificateThumbprint "zzz" -Organization "proaktiv.onmicrosoft.com" `
        -FilterEmail "ola@proaktiv.no" -DryRun

.EXAMPLE
    # Full sync with certificate auth
    .\Sync-EntraIdEmployees.ps1 -TenantId "xxx" -ClientId "yyy" `
        -CertificateThumbprint "zzz" -Organization "proaktiv.onmicrosoft.com"

.EXAMPLE
    # Profile only sync (skip photos and signatures)
    .\Sync-EntraIdEmployees.ps1 -TenantId "xxx" -ClientId "yyy" `
        -CertificateThumbprint "zzz" -Organization "proaktiv.onmicrosoft.com" `
        -SkipPhoto -SkipSignature

.EXAMPLE
    # Using client secret from environment variable
    $env:ENTRA_CLIENT_SECRET = "your-secret"
    .\Sync-EntraIdEmployees.ps1 -TenantId "xxx" -ClientId "yyy" `
        -Organization "proaktiv.onmicrosoft.com"
#>

[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = "Certificate")]
param(
    # === Authentication (Required) ===
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")]
    [string]$TenantId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")]
    [string]$ClientId,

    [Parameter(Mandatory = $true, ParameterSetName = "Certificate")]
    [ValidatePattern("^[0-9a-fA-F]{40}$")]
    [string]$CertificateThumbprint,

    [Parameter(Mandatory = $false, ParameterSetName = "Secret")]
    [string]$ClientSecret,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[a-zA-Z0-9-]+\.onmicrosoft\.com$")]
    [string]$Organization,

    # === Database ===
    [Parameter()]
    [string]$DatabaseUrl,

    # === Filtering ===
    [Parameter()]
    [ValidatePattern("^[^@]+@[^@]+\.[^@]+$")]
    [string]$FilterEmail,

    # === Feature Toggles ===
    [Parameter()]
    [switch]$SkipProfile,

    [Parameter()]
    [switch]$SkipPhoto,

    [Parameter()]
    [switch]$SkipSignature,

    # === Customization ===
    [Parameter()]
    [string]$SignatureTemplate,

    # === Rate Limiting ===
    [Parameter()]
    [ValidateRange(50, 5000)]
    [int]$DelayMs = 150,

    # === Safety ===
    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$Force,

    # === Logging ===
    [Parameter()]
    [string]$LogPath
)

# ============================================================================
# INITIALIZATION
# ============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:StartTime = Get-Date
$script:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:BackendDir = Split-Path -Parent $script:ScriptDir
$script:LogFile = $null
$script:Results = @()

# Required PowerShell modules
$RequiredModules = @(
    @{ Name = "Microsoft.Graph.Authentication"; MinVersion = "2.0.0" },
    @{ Name = "Microsoft.Graph.Users"; MinVersion = "2.0.0" },
    @{ Name = "ExchangeOnlineManagement"; MinVersion = "3.0.0" }
)

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

function Write-Log {
    <#
    .SYNOPSIS
        Writes a timestamped log entry to console and file.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO",

        [switch]$NoNewline
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Console output with color
    $color = switch ($Level) {
        "INFO"  { "White" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        "DEBUG" { "Gray" }
    }
    
    if ($NoNewline) {
        Write-Host $logEntry -ForegroundColor $color -NoNewline
    } else {
        Write-Host $logEntry -ForegroundColor $color
    }
    
    # File output
    if ($script:LogFile) {
        $isoTimestamp = Get-Date -Format "o"
        "$isoTimestamp | $($Level.PadRight(5)) | $Message" | Add-Content -Path $script:LogFile
    }
}

function Write-SafeParameters {
    param($Params)
    $safe = @{}
    foreach ($key in $Params.Keys) {
        if ($key -in @("ClientSecret", "DatabaseUrl", "CertificateThumbprint")) {
            $safe[$key] = "***REDACTED***"
        } else {
            $safe[$key] = $Params[$key]
        }
    }
    return $safe
}

# ============================================================================
# RETRY FUNCTION
# ============================================================================

function Invoke-WithRetry {
    <#
    .SYNOPSIS
        Executes a script block with exponential backoff retry.
    #>
    param(
        [Parameter(Mandatory)]
        [scriptblock]$ScriptBlock,

        [int]$MaxRetries = 3,
        [int]$InitialDelayMs = 1000,
        [int[]]$RetryableStatusCodes = @(429, 503)
    )

    $attempt = 0
    $delay = $InitialDelayMs

    while ($true) {
        $attempt++
        try {
            return & $ScriptBlock
        }
        catch {
            $statusCode = $null
            if ($_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            
            if ($attempt -ge $MaxRetries -or ($statusCode -and $statusCode -notin $RetryableStatusCodes)) {
                throw
            }
            
            Write-Log "Attempt $attempt failed. Retrying in $($delay)ms..." -Level WARN
            Start-Sleep -Milliseconds $delay
            $delay = [Math]::Min($delay * 2, 30000)  # Max 30 seconds
        }
    }
}

# ============================================================================
# DEPENDENCY CHECK
# ============================================================================

function Test-Dependencies {
    $missing = @()
    foreach ($module in $RequiredModules) {
        $installed = Get-Module -ListAvailable -Name $module.Name | 
            Where-Object { $_.Version -ge [version]$module.MinVersion }
        if (-not $installed) {
            $missing += "$($module.Name) (>= $($module.MinVersion))"
        }
    }
    if ($missing.Count -gt 0) {
        Write-Log "Missing required modules:" -Level ERROR
        $missing | ForEach-Object { Write-Log "  - $_" -Level ERROR }
        Write-Log "Install with: Install-Module <ModuleName> -Scope CurrentUser" -Level INFO
        exit 5
    }
    
    # Check Python
    try {
        $pythonVersion = & py -3.12 --version 2>&1
        Write-Log "Python: $pythonVersion" -Level DEBUG
    }
    catch {
        Write-Log "Python 3.12 not found. Required for database access." -Level ERROR
        exit 5
    }
}

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

function Get-EmployeesFromDatabase {
    <#
    .SYNOPSIS
        Retrieves active employees with office data from PostgreSQL.
    #>
    param(
        [string]$FilterEmail
    )

    $pythonScript = @"
import sys
import json
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.employee import Employee
from app.models.office import Office
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    query = db.query(Employee).join(Office).filter(
        Employee.status == 'active',
        Employee.email.isnot(None)
    )
    
    filter_email = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    if filter_email:
        query = query.filter(Employee.email == filter_email)
    
    employees = query.order_by(Employee.last_name).all()
    
    result = []
    for e in employees:
        result.append({
            'id': str(e.id),
            'email': e.email,
            'first_name': e.first_name,
            'last_name': e.last_name,
            'title': e.title,
            'phone': e.phone,
            'profile_image_url': e.profile_image_url,
            'office_name': e.office.name if e.office else None,
            'office_city': e.office.city if e.office else None,
            'office_street': e.office.street_address if e.office else None,
            'office_postal': e.office.postal_code if e.office else None,
            'office_phone': e.office.phone if e.office else None,
            'office_email': e.office.email if e.office else None,
        })
    
    print(json.dumps(result))
finally:
    db.close()
"@

    Push-Location $script:BackendDir
    try {
        $filterArg = if ($FilterEmail) { $FilterEmail } else { "" }
        $jsonOutput = & py -3.12 -c $pythonScript $filterArg 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            throw "Python script failed: $jsonOutput"
        }
        
        $employees = $jsonOutput | ConvertFrom-Json
        return $employees
    }
    finally {
        Pop-Location
    }
}

# ============================================================================
# ENTRA ID FUNCTIONS
# ============================================================================

function Find-EntraUser {
    <#
    .SYNOPSIS
        Finds a user in Entra ID by email address.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$Email
    )

    try {
        # Try UPN match first
        $user = Invoke-WithRetry {
            Get-MgUser -UserId $Email -ErrorAction SilentlyContinue
        }
        if ($user) { return $user }
    }
    catch {
        # UPN not found, try mail property
    }
    
    try {
        # Try mail property match
        $users = Invoke-WithRetry {
            Get-MgUser -Filter "mail eq '$Email'" -ErrorAction SilentlyContinue
        }
        if ($users -and $users.Count -gt 0) { 
            return $users[0] 
        }
    }
    catch {
        # Mail not found, try proxyAddresses
    }
    
    try {
        # Try proxyAddresses match
        $users = Invoke-WithRetry {
            Get-MgUser -Filter "proxyAddresses/any(p:p eq 'smtp:$Email')" -ErrorAction SilentlyContinue
        }
        if ($users -and $users.Count -gt 0) { 
            return $users[0] 
        }
    }
    catch {
        # Not found
    }
    
    return $null
}

function Sync-UserProfile {
    <#
    .SYNOPSIS
        Updates a user's Entra ID profile with employee data.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$EntraUserId,

        [Parameter(Mandatory)]
        [PSCustomObject]$Employee,

        [switch]$DryRun
    )

    $result = @{
        Success = $false
        Changes = @()
        Error   = $null
    }

    try {
        # Get current user data
        $currentUser = Invoke-WithRetry {
            Get-MgUser -UserId $EntraUserId -Property "displayName,givenName,surname,jobTitle,mobilePhone,department,officeLocation,streetAddress,postalCode,country"
        }
        
        # Build update payload
        $updates = @{}
        $changes = @()
        
        # Display name
        $displayName = "$($Employee.first_name) $($Employee.last_name)"
        if ($currentUser.DisplayName -ne $displayName) {
            $updates["displayName"] = $displayName
            $changes += "displayName: '$($currentUser.DisplayName)' -> '$displayName'"
        }
        
        # Given name
        if ($currentUser.GivenName -ne $Employee.first_name) {
            $updates["givenName"] = $Employee.first_name
            $changes += "givenName: '$($currentUser.GivenName)' -> '$($Employee.first_name)'"
        }
        
        # Surname
        if ($currentUser.Surname -ne $Employee.last_name) {
            $updates["surname"] = $Employee.last_name
            $changes += "surname: '$($currentUser.Surname)' -> '$($Employee.last_name)'"
        }
        
        # Job title
        if ($Employee.title -and $currentUser.JobTitle -ne $Employee.title) {
            $updates["jobTitle"] = $Employee.title
            $changes += "jobTitle: '$($currentUser.JobTitle)' -> '$($Employee.title)'"
        }
        
        # Mobile phone
        if ($Employee.phone -and $currentUser.MobilePhone -ne $Employee.phone) {
            $updates["mobilePhone"] = $Employee.phone
            $changes += "mobilePhone: '$($currentUser.MobilePhone)' -> '$($Employee.phone)'"
        }
        
        # Department (office name)
        if ($Employee.office_name -and $currentUser.Department -ne $Employee.office_name) {
            $updates["department"] = $Employee.office_name
            $changes += "department: '$($currentUser.Department)' -> '$($Employee.office_name)'"
        }
        
        # Office location (city)
        if ($Employee.office_city -and $currentUser.OfficeLocation -ne $Employee.office_city) {
            $updates["officeLocation"] = $Employee.office_city
            $changes += "officeLocation: '$($currentUser.OfficeLocation)' -> '$($Employee.office_city)'"
        }
        
        # Street address
        if ($Employee.office_street -and $currentUser.StreetAddress -ne $Employee.office_street) {
            $updates["streetAddress"] = $Employee.office_street
            $changes += "streetAddress: '$($currentUser.StreetAddress)' -> '$($Employee.office_street)'"
        }
        
        # Postal code
        if ($Employee.office_postal -and $currentUser.PostalCode -ne $Employee.office_postal) {
            $updates["postalCode"] = $Employee.office_postal
            $changes += "postalCode: '$($currentUser.PostalCode)' -> '$($Employee.office_postal)'"
        }
        
        # Country
        if ($currentUser.Country -ne "NO") {
            $updates["country"] = "NO"
            $changes += "country: '$($currentUser.Country)' -> 'NO'"
        }
        
        $result.Changes = $changes
        
        if ($updates.Count -eq 0) {
            Write-Log "  No profile changes needed" -Level DEBUG
            $result.Success = $true
            return $result
        }
        
        if ($DryRun) {
            Write-Log "  [DRY RUN] Would update profile:" -Level INFO
            foreach ($change in $changes) {
                Write-Log "    - $change" -Level INFO
            }
            $result.Success = $true
        }
        else {
            Invoke-WithRetry {
                Update-MgUser -UserId $EntraUserId -BodyParameter $updates
            }
            Write-Log "  Profile updated: $($changes.Count) changes" -Level INFO
            $result.Success = $true
        }
    }
    catch {
        $result.Error = $_.Exception.Message
        Write-Log "  Profile sync failed: $($_.Exception.Message)" -Level ERROR
    }

    return $result
}

function Sync-UserPhoto {
    <#
    .SYNOPSIS
        Downloads and uploads a user's profile photo to Entra ID.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$EntraUserId,

        [Parameter(Mandatory)]
        [string]$PhotoUrl,

        [switch]$DryRun
    )

    $result = @{
        Success = $false
        Action  = "skipped"
        Error   = $null
    }

    try {
        # Validate URL
        if (-not $PhotoUrl -or $PhotoUrl -notmatch "^https?://") {
            $result.Action = "skipped"
            $result.Success = $true
            return $result
        }
        
        if ($DryRun) {
            Write-Log "  [DRY RUN] Would upload photo from: $PhotoUrl" -Level INFO
            $result.Success = $true
            $result.Action = "would_upload"
            return $result
        }
        
        # Download photo
        $tempFile = [System.IO.Path]::GetTempFileName() + ".jpg"
        try {
            Invoke-WebRequest -Uri $PhotoUrl -OutFile $tempFile -UseBasicParsing
            
            # Check file size (max 4MB for Graph API)
            $fileInfo = Get-Item $tempFile
            if ($fileInfo.Length -gt 4MB) {
                throw "Photo too large: $($fileInfo.Length / 1MB)MB (max 4MB)"
            }
            
            # Upload to Entra ID
            $photoBytes = [System.IO.File]::ReadAllBytes($tempFile)
            Invoke-WithRetry {
                Set-MgUserPhotoContent -UserId $EntraUserId -Data $photoBytes
            }
            
            Write-Log "  Photo uploaded successfully" -Level INFO
            $result.Success = $true
            $result.Action = "uploaded"
        }
        finally {
            if (Test-Path $tempFile) {
                Remove-Item $tempFile -Force
            }
        }
    }
    catch {
        $result.Error = $_.Exception.Message
        $result.Action = "failed"
        Write-Log "  Photo sync failed: $($_.Exception.Message)" -Level WARN
    }

    return $result
}

# ============================================================================
# EXCHANGE ONLINE FUNCTIONS
# ============================================================================

function Build-SignatureHtml {
    <#
    .SYNOPSIS
        Builds HTML signature from template and employee data.
    #>
    param(
        [Parameter(Mandatory)]
        [PSCustomObject]$Employee,

        [Parameter(Mandatory)]
        [string]$TemplatePath
    )

    if (-not (Test-Path $TemplatePath)) {
        throw "Signature template not found: $TemplatePath"
    }
    
    $template = Get-Content $TemplatePath -Raw -Encoding UTF8
    
    # Replace template variables
    $replacements = @{
        "{{DisplayName}}"    = "$($Employee.first_name) $($Employee.last_name)"
        "{{JobTitle}}"       = $Employee.title
        "{{Email}}"          = $Employee.email
        "{{MobilePhone}}"    = $Employee.phone
        "{{OfficeName}}"     = $Employee.office_name
        "{{OfficeAddress}}"  = $Employee.office_street
        "{{OfficePostal}}"   = "$($Employee.office_postal) $($Employee.office_city)"
        "{{OfficePhone}}"    = $Employee.office_phone
        "{{OfficeEmail}}"    = $Employee.office_email
        "{{ProfileUrl}}"     = $Employee.profile_image_url
    }
    
    foreach ($key in $replacements.Keys) {
        $value = $replacements[$key]
        if (-not $value) { $value = "" }
        $template = $template.Replace($key, $value)
    }
    
    return $template
}

function Build-SignatureText {
    <#
    .SYNOPSIS
        Builds plain text signature from template and employee data.
    #>
    param(
        [Parameter(Mandatory)]
        [PSCustomObject]$Employee,

        [Parameter(Mandatory)]
        [string]$TemplatePath
    )

    if (-not (Test-Path $TemplatePath)) {
        throw "Signature template not found: $TemplatePath"
    }
    
    $template = Get-Content $TemplatePath -Raw -Encoding UTF8
    
    # Replace template variables (same as HTML)
    $replacements = @{
        "{{DisplayName}}"    = "$($Employee.first_name) $($Employee.last_name)"
        "{{JobTitle}}"       = $Employee.title
        "{{Email}}"          = $Employee.email
        "{{MobilePhone}}"    = $Employee.phone
        "{{OfficeName}}"     = $Employee.office_name
        "{{OfficeAddress}}"  = $Employee.office_street
        "{{OfficePostal}}"   = "$($Employee.office_postal) $($Employee.office_city)"
        "{{OfficePhone}}"    = $Employee.office_phone
        "{{OfficeEmail}}"    = $Employee.office_email
        "{{ProfileUrl}}"     = $Employee.profile_image_url
    }
    
    foreach ($key in $replacements.Keys) {
        $value = $replacements[$key]
        if (-not $value) { $value = "" }
        $template = $template.Replace($key, $value)
    }
    
    return $template
}

function Set-UserSignature {
    <#
    .SYNOPSIS
        Deploys an email signature to a user's Exchange Online mailbox.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$Email,

        [Parameter(Mandatory)]
        [string]$HtmlSignature,

        [string]$TextSignature,

        [switch]$DryRun
    )

    $result = @{
        Success = $false
        Action  = "skipped"
        Error   = $null
    }

    try {
        if ($DryRun) {
            Write-Log "  [DRY RUN] Would set email signature ($($HtmlSignature.Length) bytes)" -Level INFO
            $result.Success = $true
            $result.Action = "would_set"
            return $result
        }
        
        # Set the signature using Set-MailboxMessageConfiguration
        # Note: This requires the user to have a mailbox
        Invoke-WithRetry {
            Set-MailboxMessageConfiguration -Identity $Email `
                -SignatureHtml $HtmlSignature `
                -SignatureText $TextSignature `
                -AutoAddSignature $true `
                -AutoAddSignatureOnMobile $true `
                -AutoAddSignatureOnReply $true
        }
        
        Write-Log "  Signature set successfully" -Level INFO
        $result.Success = $true
        $result.Action = "set"
    }
    catch {
        $result.Error = $_.Exception.Message
        $result.Action = "failed"
        Write-Log "  Signature sync failed: $($_.Exception.Message)" -Level WARN
    }

    return $result
}

# ============================================================================
# REPORTING FUNCTIONS
# ============================================================================

function Format-SummaryReport {
    <#
    .SYNOPSIS
        Generates a summary report of the sync operation.
    #>
    param(
        [Parameter(Mandatory)]
        [array]$Results,

        [Parameter(Mandatory)]
        [datetime]$StartTime,

        [Parameter(Mandatory)]
        [datetime]$EndTime
    )

    $duration = $EndTime - $StartTime
    $durationStr = "{0:mm\:ss}" -f $duration
    
    # Ensure Results is an array
    $ResultsArray = @($Results)
    
    $total = $ResultsArray.Count
    $processed = @($ResultsArray | Where-Object { $_.EntraUserId }).Count
    $skipped = $total - $processed
    
    $profileSuccess = @($ResultsArray | Where-Object { $_.ProfileSync.Success }).Count
    $profileFailed = @($ResultsArray | Where-Object { $_.ProfileSync.Error }).Count
    
    $photoUploaded = @($ResultsArray | Where-Object { $_.PhotoSync.Action -in @("uploaded", "would_upload") }).Count
    $photoSkipped = @($ResultsArray | Where-Object { $_.PhotoSync.Action -eq "skipped" }).Count
    $photoFailed = @($ResultsArray | Where-Object { $_.PhotoSync.Action -eq "failed" }).Count
    
    $sigSet = @($ResultsArray | Where-Object { $_.SignatureSync.Action -in @("set", "would_set") }).Count
    $sigFailed = @($ResultsArray | Where-Object { $_.SignatureSync.Action -eq "failed" }).Count

    $report = @"

================================================================================
                           SYNC SUMMARY
================================================================================
Duration:      $durationStr
Total Users:   $total
--------------------------------------------------------------------------------
  Processed:   $processed
  Skipped:     $skipped  (not found in Entra ID)
--------------------------------------------------------------------------------
  Profile:     $profileSuccess updated, $profileFailed failed
  Photo:       $photoUploaded uploaded, $photoSkipped skipped, $photoFailed failed
  Signature:   $sigSet set, $sigFailed failed
================================================================================
"@

    return $report
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    # Setup logging
    $logDir = Join-Path $script:BackendDir "logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    if (-not $LogPath) {
        $timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
        $LogPath = Join-Path $logDir "entra-sync-$timestamp.log"
    }
    $script:LogFile = $LogPath

    # Print banner
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "                     ENTRA ID EMPLOYEE SYNC" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
    
    $modeText = if ($DryRun) { "DRY RUN (no changes will be made)" } else { "LIVE (changes will be applied)" }
    $modeColor = if ($DryRun) { "Yellow" } else { "Green" }
    Write-Host "Mode:        $modeText" -ForegroundColor $modeColor
    Write-Host "Tenant:      $TenantId"
    Write-Host "Client:      $ClientId"
    Write-Host "Organization: $Organization"
    if ($FilterEmail) {
        Write-Host "Filter:      $FilterEmail" -ForegroundColor Yellow
    }
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""

    Write-Log "Script started"
    Write-Log "Parameters: $(Write-SafeParameters $PSBoundParameters | ConvertTo-Json -Compress)"

    # Check dependencies
    Write-Log "Checking dependencies..."
    Test-Dependencies
    Write-Log "Dependencies OK"

    # Connect to Microsoft Graph
    Write-Log "Connecting to Microsoft Graph..."
    if ($CertificateThumbprint) {
        Connect-MgGraph -TenantId $TenantId -ClientId $ClientId -CertificateThumbprint $CertificateThumbprint -NoWelcome
    }
    else {
        # Use client secret (from param or env var)
        $secret = $ClientSecret
        if (-not $secret) {
            $secret = $env:ENTRA_CLIENT_SECRET
        }
        if (-not $secret) {
            throw "Client secret not provided. Use -ClientSecret or set ENTRA_CLIENT_SECRET environment variable."
        }
        
        $secureSecret = ConvertTo-SecureString $secret -AsPlainText -Force
        $credential = [PSCredential]::new($ClientId, $secureSecret)
        Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential -NoWelcome
    }
    Write-Log "Microsoft Graph connected"

    # Connect to Exchange Online (only if signatures are enabled)
    if (-not $SkipSignature) {
        Write-Log "Connecting to Exchange Online..."
        if ($CertificateThumbprint) {
            Connect-ExchangeOnline -CertificateThumbprint $CertificateThumbprint -AppId $ClientId -Organization $Organization -ShowBanner:$false
        }
        else {
            # Client secret auth for Exchange Online
            Connect-ExchangeOnline -AppId $ClientId -Organization $Organization -ShowBanner:$false
        }
        Write-Log "Exchange Online connected"
    }

    # Get employees from database
    Write-Log "Retrieving employees from database..."
    $employees = Get-EmployeesFromDatabase -FilterEmail $FilterEmail
    Write-Log "Found $($employees.Count) active employees"

    if ($employees.Count -eq 0) {
        Write-Log "No employees to process. Exiting." -Level WARN
        exit 0
    }

    # Confirmation prompt (unless -Force or -DryRun)
    if (-not $Force -and -not $DryRun) {
        $confirm = Read-Host "Process $($employees.Count) employees? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Log "Cancelled by user"
            exit 0
        }
    }

    # Resolve template paths
    $htmlTemplatePath = if ($SignatureTemplate) { 
        $SignatureTemplate 
    } else { 
        Join-Path $script:ScriptDir "templates\email-signature.html" 
    }
    $textTemplatePath = $htmlTemplatePath -replace "\.html$", ".txt"

    # Process each employee
    $counter = 0
    foreach ($employee in $employees) {
        $counter++
        
        Write-Host ""
        Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray
        Write-Host "Processing $counter of $($employees.Count): $($employee.first_name) $($employee.last_name) ($($employee.email))" -ForegroundColor White
        Write-Host "--------------------------------------------------------------------------------" -ForegroundColor DarkGray

        $userResult = @{
            Email         = $employee.email
            EntraUserId   = $null
            ProfileSync   = @{ Success = $false; Changes = @(); Error = $null }
            PhotoSync     = @{ Success = $false; Action = "skipped"; Error = $null }
            SignatureSync = @{ Success = $false; Action = "skipped"; Error = $null }
        }

        try {
            # Find user in Entra ID
            Write-Log "  Finding user in Entra ID..."
            $entraUser = Find-EntraUser -Email $employee.email
            
            if (-not $entraUser) {
                Write-Log "  User not found in Entra ID: $($employee.email)" -Level WARN
                $userResult.ProfileSync.Error = "User not found in Entra ID"
                $script:Results += $userResult
                continue
            }
            
            $userResult.EntraUserId = $entraUser.Id
            Write-Log "  Found: $($entraUser.Id)"
            
            # Profile sync
            if (-not $SkipProfile) {
                $userResult.ProfileSync = Sync-UserProfile -EntraUserId $entraUser.Id -Employee $employee -DryRun:$DryRun
                Start-Sleep -Milliseconds $DelayMs
            }
            
            # Photo sync
            if (-not $SkipPhoto -and $employee.profile_image_url) {
                $userResult.PhotoSync = Sync-UserPhoto -EntraUserId $entraUser.Id -PhotoUrl $employee.profile_image_url -DryRun:$DryRun
                Start-Sleep -Milliseconds $DelayMs
            }
            
            # Signature sync
            if (-not $SkipSignature) {
                try {
                    $htmlSig = Build-SignatureHtml -Employee $employee -TemplatePath $htmlTemplatePath
                    $textSig = if (Test-Path $textTemplatePath) {
                        Build-SignatureText -Employee $employee -TemplatePath $textTemplatePath
                    } else {
                        # Generate plain text from HTML
                        $htmlSig -replace "<[^>]+>", "" -replace "\s+", " "
                    }
                    $userResult.SignatureSync = Set-UserSignature -Email $employee.email -HtmlSignature $htmlSig -TextSignature $textSig -DryRun:$DryRun
                }
                catch {
                    $userResult.SignatureSync.Error = $_.Exception.Message
                    $userResult.SignatureSync.Action = "failed"
                    Write-Log "  Signature build/set failed: $($_.Exception.Message)" -Level WARN
                }
            }
        }
        catch {
            Write-Log "  Critical error processing $($employee.email): $($_.Exception.Message)" -Level ERROR
        }

        $script:Results += $userResult
        
        # Inter-user delay
        if ($counter -lt $employees.Count) {
            Start-Sleep -Milliseconds $DelayMs
        }
    }

    # Generate summary
    $endTime = Get-Date
    $report = Format-SummaryReport -Results $script:Results -StartTime $script:StartTime -EndTime $endTime
    Write-Host $report

    # Determine exit code
    $failedCount = @($script:Results | Where-Object { $_.ProfileSync.Error -or $_.PhotoSync.Action -eq "failed" -or $_.SignatureSync.Action -eq "failed" }).Count
    $notFoundCount = @($script:Results | Where-Object { -not $_.EntraUserId }).Count
    
    if ($failedCount -eq 0 -and $notFoundCount -eq 0) {
        Write-Host "Exit Code: 0 (success)" -ForegroundColor Green
        Write-Log "Sync completed successfully"
        $exitCode = 0
    }
    elseif ($failedCount -gt 0 -or $notFoundCount -gt 0) {
        Write-Host "Exit Code: 1 (partial success - some users skipped or failed)" -ForegroundColor Yellow
        Write-Log "Sync completed with warnings"
        $exitCode = 1
    }

    Write-Host ""
    Write-Host "Log saved to: $($script:LogFile)" -ForegroundColor DarkGray
    Write-Host "================================================================================" -ForegroundColor Cyan

}
catch {
    Write-Log "Fatal error: $($_.Exception.Message)" -Level ERROR
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Level ERROR
    
    # Determine error type
    if ($_.Exception.Message -match "authentication|unauthorized|401") {
        Write-Host "Exit Code: 2 (authentication failure)" -ForegroundColor Red
        exit 2
    }
    elseif ($_.Exception.Message -match "database|connection|postgresql") {
        Write-Host "Exit Code: 3 (database connection failure)" -ForegroundColor Red
        exit 3
    }
    elseif ($_.Exception.Message -match "parameter|validation") {
        Write-Host "Exit Code: 4 (invalid parameters)" -ForegroundColor Red
        exit 4
    }
    else {
        Write-Host "Exit Code: 1 (general error)" -ForegroundColor Red
        exit 1
    }
}
finally {
    # Cleanup connections
    try {
        Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null
    } catch {}
    
    try {
        Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
    } catch {}
}

exit $exitCode
