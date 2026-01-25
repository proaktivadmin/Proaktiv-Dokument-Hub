<#
.SYNOPSIS
    POC: Deploy Outlook signature from Entra ID profile data.

.DESCRIPTION
    This script:
    1. Authenticates to Microsoft Graph using client credentials
    2. Fetches user profile data from Entra ID
    3. Generates HTML signature from template
    4. Deploys to local Outlook signature folder
    5. Sets as default signature (optional)

.PARAMETER UserEmail
    Email address of the user to generate signature for.
    Defaults to current user (interactive) or required for app-only auth.

.PARAMETER TemplatePath
    Path to HTML signature template.
    Defaults to templates/email-signature.html

.PARAMETER SignatureName
    Name for the signature in Outlook.
    Defaults to "Proaktiv"

.PARAMETER SetAsDefault
    Set this signature as default for new emails and replies.

.PARAMETER DryRun
    Generate signature but don't deploy to Outlook folder.

.PARAMETER PreviewOnly
    Generate signature and open in browser for preview.

.EXAMPLE
    # Preview signature for your account
    .\Deploy-OutlookSignature.ps1 -UserEmail "froyland@proaktiv.no" -PreviewOnly

.EXAMPLE
    # Deploy signature to Outlook
    .\Deploy-OutlookSignature.ps1 -UserEmail "froyland@proaktiv.no" -SetAsDefault

.EXAMPLE
    # Dry run (show what would happen)
    .\Deploy-OutlookSignature.ps1 -UserEmail "froyland@proaktiv.no" -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[^@]+@[^@]+\.[^@]+$")]
    [string]$UserEmail,

    [Parameter()]
    [string]$TemplatePath,

    [Parameter()]
    [string]$SignatureName = "Proaktiv",

    [Parameter()]
    [switch]$SetAsDefault,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$PreviewOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ============================================================================
# Configuration
# ============================================================================

$script:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:BackendDir = Split-Path -Parent $script:ScriptDir

# Load .env file
$envFile = Join-Path $script:BackendDir ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Remove quotes if present
            $value = $value -replace '^["'']|["'']$', ''
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
    Write-Host "[OK] Loaded .env file" -ForegroundColor Green
}

# Get credentials from environment
$TenantId = $env:ENTRA_TENANT_ID
$ClientId = $env:ENTRA_CLIENT_ID
$ClientSecret = $env:ENTRA_CLIENT_SECRET

if (-not $TenantId -or -not $ClientId -or -not $ClientSecret) {
    throw "Missing ENTRA_TENANT_ID, ENTRA_CLIENT_ID, or ENTRA_CLIENT_SECRET in .env"
}

# Default template path
if (-not $TemplatePath) {
    $TemplatePath = Join-Path $script:ScriptDir "templates\email-signature.html"
}

if (-not (Test-Path $TemplatePath)) {
    throw "Template not found: $TemplatePath"
}

# Outlook signature folder
$SignatureFolder = Join-Path $env:APPDATA "Microsoft\Signatures"

# ============================================================================
# Functions
# ============================================================================

function Get-GraphAccessToken {
    <#
    .SYNOPSIS
        Get access token for Microsoft Graph using client credentials.
    #>
    param(
        [string]$TenantId,
        [string]$ClientId,
        [string]$ClientSecret
    )

    $tokenUrl = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"
    
    $body = @{
        client_id     = $ClientId
        client_secret = $ClientSecret
        scope         = "https://graph.microsoft.com/.default"
        grant_type    = "client_credentials"
    }

    try {
        $response = Invoke-RestMethod -Uri $tokenUrl -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
        return $response.access_token
    }
    catch {
        throw "Failed to get access token: $($_.Exception.Message)"
    }
}

function Get-UserProfile {
    <#
    .SYNOPSIS
        Fetch user profile from Microsoft Graph.
    #>
    param(
        [string]$AccessToken,
        [string]$UserEmail
    )

    $headers = @{
        Authorization = "Bearer $AccessToken"
        "Content-Type" = "application/json"
    }

    # Fetch user with specific properties
    $select = "displayName,givenName,surname,jobTitle,department,mobilePhone,mail,officeLocation,streetAddress,city,postalCode,country"
    $url = "https://graph.microsoft.com/v1.0/users/$UserEmail`?`$select=$select"

    try {
        $user = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
        return $user
    }
    catch {
        throw "Failed to fetch user profile for $UserEmail`: $($_.Exception.Message)"
    }
}

function Get-OfficeInfo {
    <#
    .SYNOPSIS
        Get office info based on department/location.
        Returns default Proaktiv info if not found.
    #>
    param(
        [object]$UserProfile
    )

    # Office mapping based on department (using HTML entities for Norwegian chars)
    # å = &#229;  ø = &#248;  æ = &#230;
    $offices = @{
        "Stavanger" = @{
            Name = "Proaktiv Stavanger"
            Address = "Lag&#229;rdsveien 78"
            Postal = "4010 Stavanger"
        }
        "Sandnes" = @{
            Name = "Proaktiv Sandnes"
            Address = "Langgata 54"
            Postal = "4306 Sandnes"
        }
        "Sola" = @{
            Name = "Proaktiv Sola"
            Address = "Solakrossen 12"
            Postal = "4050 Sola"
        }
        "Bryne" = @{
            Name = "Proaktiv Bryne"
            Address = "Hetlandsgata 5"
            Postal = "4340 Bryne"
        }
        "Klepp" = @{
            Name = "Proaktiv Klepp"
            Address = "J&#230;rveien 70"
            Postal = "4352 Kleppe"
        }
        "Voss" = @{
            Name = "Proaktiv Voss"
            Address = "Vangsgata 22"
            Postal = "5700 Voss"
        }
    }

    $dept = $UserProfile.department
    if ($dept -and $offices.ContainsKey($dept)) {
        return $offices[$dept]
    }

    # Fallback to Stavanger (headquarters)
    return @{
        Name = "Proaktiv Eiendomsmegling"
        Address = "Lag&#229;rdsveien 78"
        Postal = "4010 Stavanger"
    }
}

function New-SignatureHtml {
    <#
    .SYNOPSIS
        Generate signature HTML from template and user data.
    #>
    param(
        [string]$TemplatePath,
        [object]$UserProfile,
        [hashtable]$OfficeInfo
    )

    # Read template with proper UTF-8 encoding (handle BOM correctly)
    $template = [System.IO.File]::ReadAllText($TemplatePath, [System.Text.Encoding]::UTF8)

    # Build replacements (using if/else for PS 5.1 compatibility)
    $replacements = @{
        "{{DisplayName}}"   = if ($UserProfile.displayName) { $UserProfile.displayName } else { "" }
        "{{JobTitle}}"      = if ($UserProfile.jobTitle) { $UserProfile.jobTitle } else { "" }
        "{{MobilePhone}}"   = if ($UserProfile.mobilePhone) { $UserProfile.mobilePhone } else { "" }
        "{{Email}}"         = if ($UserProfile.mail) { $UserProfile.mail } else { "" }
        "{{OfficeName}}"    = $OfficeInfo.Name
        "{{OfficeAddress}}" = $OfficeInfo.Address
        "{{OfficePostal}}"  = $OfficeInfo.Postal
    }

    # Apply replacements
    $html = $template
    foreach ($key in $replacements.Keys) {
        $html = $html -replace [regex]::Escape($key), $replacements[$key]
    }

    return $html
}

function New-SignatureTxt {
    <#
    .SYNOPSIS
        Generate plain text signature from user data.
    #>
    param(
        [object]$UserProfile,
        [hashtable]$OfficeInfo
    )

    $txt = @"
Med vennlig hilsen

$($UserProfile.displayName)
$($UserProfile.jobTitle)

Mobil: $($UserProfile.mobilePhone)
E-post: $($UserProfile.mail)

$($OfficeInfo.Name)
$($OfficeInfo.Address), $($OfficeInfo.Postal)
Org. nr. 912 404 447

proaktiv.no
"@

    return $txt
}

function Deploy-Signature {
    <#
    .SYNOPSIS
        Deploy signature files to Outlook signature folder.
    #>
    param(
        [string]$SignatureFolder,
        [string]$SignatureName,
        [string]$HtmlContent,
        [string]$TxtContent
    )

    # Create signature folder if it doesn't exist
    if (-not (Test-Path $SignatureFolder)) {
        New-Item -ItemType Directory -Path $SignatureFolder -Force | Out-Null
        Write-Host "[OK] Created signature folder: $SignatureFolder" -ForegroundColor Green
    }

    # Write HTML signature (UTF-8 with BOM for Outlook to detect encoding)
    $htmPath = Join-Path $SignatureFolder "$SignatureName.htm"
    $utf8WithBom = New-Object System.Text.UTF8Encoding $true
    [System.IO.File]::WriteAllText($htmPath, $HtmlContent, $utf8WithBom)
    Write-Host "[OK] Wrote HTML signature: $htmPath" -ForegroundColor Green

    # Write plain text signature (UTF-8 with BOM)
    $txtPath = Join-Path $SignatureFolder "$SignatureName.txt"
    [System.IO.File]::WriteAllText($txtPath, $TxtContent, $utf8WithBom)
    Write-Host "[OK] Wrote TXT signature: $txtPath" -ForegroundColor Green

    return @{
        HtmPath = $htmPath
        TxtPath = $txtPath
    }
}

function Set-DefaultSignature {
    <#
    .SYNOPSIS
        Set signature as default in Outlook via registry.
    #>
    param(
        [string]$SignatureName
    )

    # Find Outlook profile registry key
    $outlookVersions = @("16.0", "15.0", "14.0")  # Office 2016+, 2013, 2010
    $profilesBase = "HKCU:\Software\Microsoft\Office"

    foreach ($version in $outlookVersions) {
        $profilesPath = "$profilesBase\$version\Outlook\Profiles"
        
        if (Test-Path $profilesPath) {
            $profiles = Get-ChildItem $profilesPath -ErrorAction SilentlyContinue
            
            foreach ($profile in $profiles) {
                # The signature settings are in a subkey with a specific GUID
                $accountsPath = Join-Path $profile.PSPath "9375CFF0413111d3B88A00104B2A6676"
                
                if (Test-Path $accountsPath) {
                    $accounts = Get-ChildItem $accountsPath -ErrorAction SilentlyContinue
                    
                    foreach ($account in $accounts) {
                        try {
                            # Set New Signature
                            Set-ItemProperty -Path $account.PSPath -Name "New Signature" -Value $SignatureName -Type String -Force
                            # Set Reply/Forward Signature
                            Set-ItemProperty -Path $account.PSPath -Name "Reply-Forward Signature" -Value $SignatureName -Type String -Force
                            
                            Write-Host "[OK] Set default signature for profile: $($profile.PSChildName)" -ForegroundColor Green
                        }
                        catch {
                            Write-Host "[WARN] Could not set default for $($account.PSPath): $($_.Exception.Message)" -ForegroundColor Yellow
                        }
                    }
                }
            }
        }
    }
}

# ============================================================================
# Main
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Deploy Outlook Signature (POC)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuration:" -ForegroundColor White
Write-Host "  User: $UserEmail"
Write-Host "  Template: $TemplatePath"
Write-Host "  Signature Name: $SignatureName"
Write-Host "  Signature Folder: $SignatureFolder"
Write-Host "  Dry Run: $DryRun"
Write-Host "  Preview Only: $PreviewOnly"
Write-Host "  Set As Default: $SetAsDefault"
Write-Host ""

# Step 1: Authenticate
Write-Host "[1/5] Authenticating to Microsoft Graph..." -ForegroundColor Yellow
$accessToken = Get-GraphAccessToken -TenantId $TenantId -ClientId $ClientId -ClientSecret $ClientSecret
Write-Host "[OK] Authenticated successfully" -ForegroundColor Green

# Step 2: Fetch user profile
Write-Host "[2/5] Fetching user profile for $UserEmail..." -ForegroundColor Yellow
$userProfile = Get-UserProfile -AccessToken $accessToken -UserEmail $UserEmail
Write-Host "[OK] Profile fetched:" -ForegroundColor Green
Write-Host "     Name: $($userProfile.displayName)"
Write-Host "     Title: $($userProfile.jobTitle)"
Write-Host "     Mobile: $($userProfile.mobilePhone)"
Write-Host "     Department: $($userProfile.department)"

# Step 3: Get office info
Write-Host "[3/5] Resolving office info..." -ForegroundColor Yellow
$officeInfo = Get-OfficeInfo -UserProfile $userProfile
Write-Host "[OK] Office: $($officeInfo.Name)" -ForegroundColor Green

# Step 4: Generate signature
Write-Host "[4/5] Generating signature from template..." -ForegroundColor Yellow
$htmlSignature = New-SignatureHtml -TemplatePath $TemplatePath -UserProfile $userProfile -OfficeInfo $officeInfo
$txtSignature = New-SignatureTxt -UserProfile $userProfile -OfficeInfo $officeInfo
Write-Host "[OK] Signature generated ($($htmlSignature.Length) chars HTML)" -ForegroundColor Green

# Preview mode - save to temp and open in browser
if ($PreviewOnly) {
    $previewPath = Join-Path $env:TEMP "signature_preview.html"
    $htmlSignature | Out-File -FilePath $previewPath -Encoding UTF8 -Force
    Write-Host ""
    Write-Host "[PREVIEW] Opening signature in browser..." -ForegroundColor Cyan
    Start-Process $previewPath
    Write-Host "[PREVIEW] File saved to: $previewPath" -ForegroundColor Cyan
    exit 0
}

# Dry run mode - just show what would happen
if ($DryRun) {
    Write-Host ""
    Write-Host "[DRY RUN] Would deploy to:" -ForegroundColor Yellow
    Write-Host "  HTML: $SignatureFolder\$SignatureName.htm"
    Write-Host "  TXT:  $SignatureFolder\$SignatureName.txt"
    if ($SetAsDefault) {
        Write-Host "  Would set as default signature"
    }
    Write-Host ""
    Write-Host "[DRY RUN] Generated HTML:" -ForegroundColor Yellow
    Write-Host $htmlSignature
    exit 0
}

# Step 5: Deploy signature
Write-Host "[5/5] Deploying signature to Outlook folder..." -ForegroundColor Yellow
$paths = Deploy-Signature -SignatureFolder $SignatureFolder -SignatureName $SignatureName -HtmlContent $htmlSignature -TxtContent $txtSignature

# Set as default if requested
if ($SetAsDefault) {
    Write-Host ""
    Write-Host "[BONUS] Setting as default signature..." -ForegroundColor Yellow
    Set-DefaultSignature -SignatureName $SignatureName
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Signature deployed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Restart Outlook to see the new signature"
Write-Host "  2. Compose a new email - signature should appear automatically"
Write-Host ""
