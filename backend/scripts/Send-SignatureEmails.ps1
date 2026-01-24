<#
.SYNOPSIS
    Bulk send signature emails to employees.

.DESCRIPTION
    Loads Entra credentials from backend/.env, obtains a Graph access token,
    fetches active employees from the API, and sends a signature link email.

.PARAMETER ApiBaseUrl
    Base URL of the backend API (e.g. https://proaktiv-admin.up.railway.app).

.PARAMETER FrontendUrl
    Base URL of the frontend app (used to build signature links).

.PARAMETER SenderEmail
    Sender email address used for Graph /sendMail.

.PARAMETER FilterEmails
    Optional list of emails for targeted testing.

.PARAMETER DryRun
    If set, do not send emails (shows what would happen).

.PARAMETER Force
    Skip confirmation prompt.
#>

[CmdletBinding()]
param(
    [string]$ApiBaseUrl = "https://proaktiv-admin.up.railway.app",
    [string]$FrontendUrl = "https://proaktiv-dokument-hub.vercel.app",
    [string]$SenderEmail = "it@proaktiv.no",
    [string[]]$FilterEmails,
    [switch]$DryRun,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:StartTime = Get-Date
$script:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:BackendDir = Split-Path -Parent $script:ScriptDir

# ============================================================================
# Helpers
# ============================================================================

function Write-Color {
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        [ValidateSet("White", "Green", "Yellow", "Red", "Cyan", "Gray")]
        [string]$Color = "White"
    )

    Write-Host $Message -ForegroundColor $Color
}

function Import-DotEnv {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return $false
    }

    Get-Content $Path | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $value = $value -replace '^["'']|["'']$', ''
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }

    return $true
}

function Get-GraphAccessToken {
    param(
        [Parameter(Mandatory)]
        [string]$TenantId,
        [Parameter(Mandatory)]
        [string]$ClientId,
        [Parameter(Mandatory)]
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
        throw "Failed to get Graph access token: $($_.Exception.Message)"
    }
}

function Get-EmployeesFromApi {
    param(
        [Parameter(Mandatory)]
        [string]$ApiBaseUrl
    )

    $baseUrl = $ApiBaseUrl.TrimEnd("/")
    $limit = 500
    $skip = 0
    $allEmployees = @()
    $total = $null

    do {
        $url = "$baseUrl/api/employees?status=active&employee_type=internal&limit=$limit&skip=$skip"

        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -Headers @{ Accept = "application/json" }
        }
        catch {
            $statusCode = $null
            if ($_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            if ($statusCode -eq 401) {
                throw "API returned 401 (unauthorized). Ensure authentication is disabled or run with a valid session."
            }
            throw "Failed to fetch employees: $($_.Exception.Message)"
        }

        $items = @()
        if ($response -and $response.items) {
            $items = @($response.items)
        }
        elseif ($response -is [System.Collections.IEnumerable]) {
            $items = @($response)
        }

        $allEmployees += $items
        if ($response -and $response.total) {
            $total = [int]$response.total
        }
        else {
            $total = $allEmployees.Count
        }

        $skip += $limit
    } while ($items.Count -gt 0 -and $allEmployees.Count -lt $total)

    return ,$allEmployees
}

function Get-NotificationTemplate {
    $templatePath = Join-Path $script:ScriptDir "templates\signature-notification-email.html"
    if (Test-Path $templatePath) {
        return Get-Content $templatePath -Raw -Encoding UTF8
    }

    return @"
<p>Hei {{FirstName}},</p>
<p>Signaturen din er klar.</p>
<p><a href="{{SignatureUrl}}">{{SignatureUrl}}</a></p>
<p>Hilsen<br>IT-avdelingen</p>
"@
}

function Build-NotificationHtml {
    param(
        [Parameter(Mandatory)]
        [string]$Template,
        [Parameter(Mandatory)]
        [string]$FirstName,
        [Parameter(Mandatory)]
        [string]$SignatureUrl
    )

    $safeName = [System.Net.WebUtility]::HtmlEncode($FirstName)
    $safeUrl = [System.Net.WebUtility]::HtmlEncode($SignatureUrl)

    $html = $Template.Replace("{{FirstName}}", $safeName)
    return $html.Replace("{{SignatureUrl}}", $safeUrl)
}

function Send-GraphMail {
    param(
        [Parameter(Mandatory)]
        [string]$AccessToken,
        [Parameter(Mandatory)]
        [string]$SenderEmail,
        [Parameter(Mandatory)]
        [string]$RecipientEmail,
        [Parameter(Mandatory)]
        [string]$Subject,
        [Parameter(Mandatory)]
        [string]$HtmlBody
    )

    $headers = @{
        Authorization = "Bearer $AccessToken"
        "Content-Type" = "application/json"
    }

    $payload = @{
        message = @{
            subject = $Subject
            body = @{
                contentType = "HTML"
                content = $HtmlBody
            }
            toRecipients = @(
                @{ emailAddress = @{ address = $RecipientEmail } }
            )
        }
        saveToSentItems = $false
    }

    $url = "https://graph.microsoft.com/v1.0/users/$SenderEmail/sendMail"
    $json = $payload | ConvertTo-Json -Depth 8

    try {
        Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $json | Out-Null
        return @{ Success = $true; Error = $null }
    }
    catch {
        $message = $_.Exception.Message
        return @{ Success = $false; Error = $message }
    }
}

# ============================================================================
# Main
# ============================================================================

try {
    Write-Host ""
    Write-Color "================================================================================" "Cyan"
    Write-Color "                  BULK SIGNATURE EMAIL SENDER" "Cyan"
    Write-Color "================================================================================" "Cyan"
    Write-Host ""

    $envFile = Join-Path $script:BackendDir ".env"
    if (Import-DotEnv -Path $envFile) {
        Write-Color "[OK] Loaded .env file" "Green"
    }
    else {
        Write-Color "[WARN] .env file not found (continuing with existing env vars)" "Yellow"
    }

    $tenantId = $env:ENTRA_TENANT_ID
    $clientId = $env:ENTRA_CLIENT_ID
    $clientSecret = $env:ENTRA_CLIENT_SECRET

    if (-not $tenantId -or -not $clientId -or -not $clientSecret) {
        throw "Missing ENTRA_TENANT_ID, ENTRA_CLIENT_ID, or ENTRA_CLIENT_SECRET in environment"
    }

    $apiBase = $ApiBaseUrl.TrimEnd("/")
    $frontendBase = $FrontendUrl.TrimEnd("/")

    Write-Host ""
    Write-Color "Configuration:" "White"
    Write-Host "  ApiBaseUrl:  $apiBase"
    Write-Host "  FrontendUrl: $frontendBase"
    Write-Host "  SenderEmail: $SenderEmail"
    Write-Host "  DryRun:      $DryRun"
    if ($FilterEmails -and $FilterEmails.Count -gt 0) {
        Write-Host "  FilterEmails: $($FilterEmails -join ', ')"
    }
    Write-Host ""

    Write-Color "[1/3] Authenticating to Microsoft Graph..." "Yellow"
    $accessToken = Get-GraphAccessToken -TenantId $tenantId -ClientId $clientId -ClientSecret $clientSecret
    Write-Color "[OK] Authenticated successfully" "Green"

    Write-Color "[2/3] Fetching employees from API..." "Yellow"
    $employees = @(Get-EmployeesFromApi -ApiBaseUrl $apiBase)
    Write-Color "[OK] Retrieved $($employees.Count) employees" "Green"

    # Filter: active + has email (API already filters active, but keep safety)
    $eligibleEmployees = @($employees | Where-Object { $_.status -eq "active" -and $_.email })
    $missingEmailCount = $employees.Count - $eligibleEmployees.Count

    # Filter by email list if provided
    if ($FilterEmails -and $FilterEmails.Count -gt 0) {
        $filterSet = @{}
        foreach ($email in $FilterEmails) {
            if ($email) {
                $filterSet[$email.ToLower()] = $true
            }
        }
        $filteredEmployees = @($eligibleEmployees | Where-Object { $filterSet.ContainsKey($_.email.ToLower()) })
        $filteredOutCount = $eligibleEmployees.Count - $filteredEmployees.Count
        $eligibleEmployees = $filteredEmployees
    }
    else {
        $filteredOutCount = 0
    }

    if ($eligibleEmployees.Count -eq 0) {
        Write-Color "[WARN] No employees to process after filtering" "Yellow"
        exit 0
    }

    Write-Host ""
    Write-Color "Eligible employees: $($eligibleEmployees.Count)" "White"
    if ($missingEmailCount -gt 0) {
        Write-Color "Skipped (missing email): $missingEmailCount" "Yellow"
    }
    if ($filteredOutCount -gt 0) {
        Write-Color "Skipped (filter list): $filteredOutCount" "Yellow"
    }

    # Confirmation prompt
    if (-not $Force) {
        Write-Host ""
        $confirm = Read-Host "Send signature emails to $($eligibleEmployees.Count) employees? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Color "Cancelled by user" "Yellow"
            exit 0
        }
    }

    Write-Host ""
    Write-Color "[3/3] Processing emails..." "Yellow"

    $template = Get-NotificationTemplate
    $results = @()
    $sentCount = 0
    $dryRunCount = 0
    $errorCount = 0
    $skippedCount = 0

    for ($i = 0; $i -lt $eligibleEmployees.Count; $i++) {
        $employee = $eligibleEmployees[$i]
        $index = $i + 1
        $percent = [int](($index / $eligibleEmployees.Count) * 100)

        Write-Progress -Activity "Sending signature emails" -Status "$index of $($eligibleEmployees.Count): $($employee.email)" -PercentComplete $percent

        if (-not $employee.email) {
            $skippedCount++
            Write-Color "[SKIP] Missing email for employee $($employee.id)" "Yellow"
            continue
        }

        $signatureUrl = "$frontendBase/signature/$($employee.id)"
        $firstName = if ($employee.first_name) { $employee.first_name } elseif ($employee.full_name) { $employee.full_name } else { "der" }
        $htmlBody = Build-NotificationHtml -Template $template -FirstName $firstName -SignatureUrl $signatureUrl
        $subject = "Din e-postsignatur er klar"

        if ($DryRun) {
            $dryRunCount++
            Write-Color "[DRY RUN] Would send to $($employee.email)" "Yellow"
            $results += @{ Email = $employee.email; Status = "dry-run"; Error = $null }
            continue
        }

        $sendResult = Send-GraphMail -AccessToken $accessToken -SenderEmail $SenderEmail -RecipientEmail $employee.email -Subject $subject -HtmlBody $htmlBody
        if ($sendResult.Success) {
            $sentCount++
            Write-Color "[SENT] $($employee.email)" "Green"
            $results += @{ Email = $employee.email; Status = "sent"; Error = $null }
        }
        else {
            $errorCount++
            Write-Color "[ERROR] $($employee.email): $($sendResult.Error)" "Red"
            $results += @{ Email = $employee.email; Status = "error"; Error = $sendResult.Error }
        }

        # Rate limiting between sends
        if ($index -lt $eligibleEmployees.Count) {
            Start-Sleep -Milliseconds 500
        }
    }

    Write-Progress -Activity "Sending signature emails" -Completed

    $endTime = Get-Date
    $duration = $endTime - $script:StartTime
    $durationStr = "{0:mm\:ss}" -f $duration

    Write-Host ""
    Write-Color "================================================================================" "Cyan"
    Write-Color "SUMMARY" "Cyan"
    Write-Color "================================================================================" "Cyan"
    Write-Host "Duration:        $durationStr"
    Write-Host "Total fetched:   $($employees.Count)"
    Write-Host "Eligible:        $($eligibleEmployees.Count)"
    Write-Host "Sent:            $sentCount"
    Write-Host "Dry run:         $dryRunCount"
    Write-Host "Skipped:         $skippedCount"
    Write-Host "Errors:          $errorCount"
    Write-Color "================================================================================" "Cyan"

    if ($errorCount -gt 0) {
        exit 1
    }
    else {
        exit 0
    }
}
catch {
    Write-Host ""
    Write-Color "[FATAL] $($_.Exception.Message)" "Red"
    exit 1
}
