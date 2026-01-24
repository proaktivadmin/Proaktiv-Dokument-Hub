#Requires -Modules ExchangeOnlineManagement

<#
.SYNOPSIS
    Manage Proaktiv email signature transport rules in Exchange Online.
.DESCRIPTION
    Creates, updates, or removes transport rules that append email signatures
    to outgoing messages sent to external recipients. Read-only by default.
.EXAMPLE
    .\Set-TransportRuleSignature.ps1
    Show status in read-only mode (default).
.EXAMPLE
    .\Set-TransportRuleSignature.ps1 -Create -DryRun
    Preview creation without making changes.
.EXAMPLE
    .\Set-TransportRuleSignature.ps1 -Update -Force
    Update the transport rule without confirmation.
#>

[CmdletBinding()]
param(
    [switch]$Create,      # Create new transport rule
    [switch]$Update,      # Update existing rule
    [switch]$Remove,      # Remove rule
    [switch]$DryRun,      # Preview only (default behavior)
    [ValidateNotNullOrEmpty()]
    [string]$RuleName = "Proaktiv External Signature",
    [ValidateNotNullOrEmpty()]
    [string]$TemplatePath = ".\templates\transport-signature.html",
    [ValidateNotNullOrEmpty()]
    [string]$Organization = "proaktiv.onmicrosoft.com",
    [string]$UserPrincipalName,
    [switch]$DisableWam,
    [switch]$UseRPSSession,
    [switch]$Force        # Skip confirmation prompts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:StartTime = Get-Date
$script:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:BackendDir = Split-Path -Parent $script:ScriptDir
$script:LogFile = $null

function Write-Log {
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [ValidateSet("INFO", "WARN", "ERROR")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    $color = switch ($Level) {
        "INFO"  { "White" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
    }

    Write-Host $logEntry -ForegroundColor $color

    if ($script:LogFile) {
        $isoTimestamp = Get-Date -Format "o"
        "$isoTimestamp | $($Level.PadRight(5)) | $Message" | Add-Content -Path $script:LogFile
    }
}

function Initialize-Log {
    $logDir = Join-Path $script:BackendDir "logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $dateStamp = Get-Date -Format "yyyyMMdd"
    $script:LogFile = Join-Path $logDir "transport-rule-$dateStamp.log"
}

function Resolve-TemplatePath {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    $resolved = if ([System.IO.Path]::IsPathRooted($Path)) {
        $Path
    }
    else {
        Join-Path $script:ScriptDir $Path
    }

    if (-not (Test-Path $resolved)) {
        throw "Template file not found: $resolved"
    }

    return (Resolve-Path $resolved).Path
}

function Confirm-Action {
    param(
        [Parameter(Mandatory)]
        [string]$Prompt
    )

    if ($Force) {
        return $true
    }

    $response = Read-Host "$Prompt (y/N)"
    return $response -match "^(y|yes)$"
}

function Get-ExistingRule {
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    try {
        return Get-TransportRule -Identity $Name -ErrorAction SilentlyContinue
    }
    catch {
        throw "Failed to query transport rule '$Name': $($_.Exception.Message)"
    }
}

function Invoke-Main {
    $actionFlags = @($Create, $Update, $Remove) | Where-Object { $_ }
    $actionCount = @($actionFlags).Count
    if ($actionCount -gt 1) {
        throw "Only one of -Create, -Update, or -Remove can be specified."
    }

    $requestedAction = if ($Create) { "Create" } elseif ($Update) { "Update" } elseif ($Remove) { "Remove" } else { "Status" }
    $effectiveDryRun = $DryRun -or ($requestedAction -eq "Status")

    Initialize-Log

    Write-Log "Script started"
    Write-Log "Action: $requestedAction"
    Write-Log "Dry run: $effectiveDryRun"
    Write-Log "Rule name: $RuleName"
    Write-Log "Organization: $Organization"

    $signatureHtml = $null
    $resolvedTemplate = $null
    if ($requestedAction -in @("Create", "Update")) {
        $resolvedTemplate = Resolve-TemplatePath -Path $TemplatePath
        $signatureHtml = Get-Content $resolvedTemplate -Raw -Encoding UTF8
        if (-not $signatureHtml) {
            throw "Template file is empty: $resolvedTemplate"
        }
        Write-Log "Template loaded: $resolvedTemplate ($($signatureHtml.Length) chars)"
    }
    elseif ($requestedAction -eq "Remove") {
        Write-Log "Skipping template validation for Remove action" -Level "INFO"
    }
    else {
        Write-Log "No action specified; running status-only read-only mode" -Level "WARN"
    }

    $connectParams = @{
        Organization = $Organization
        ShowBanner   = $false
    }

    if ($DisableWam) {
        $connectParams.DisableWAM = $true
    }
    if ($UseRPSSession) {
        $connectParams.UseRPSSession = $true
    }

    $connectCommand = Get-Command Connect-ExchangeOnline -ErrorAction Stop
    $supportsDevice = $connectCommand.Parameters.ContainsKey("Device")

    if ($supportsDevice) {
        Write-Log "Connecting to Exchange Online (device code flow)..."
        $connectParams.Device = $true
    }
    elseif ($UserPrincipalName) {
        Write-Log "Connecting to Exchange Online (interactive login)..."
        $connectParams.UserPrincipalName = $UserPrincipalName
    }
    else {
        throw "Connect-ExchangeOnline does not support -Device. Provide -UserPrincipalName for interactive login."
    }

    Connect-ExchangeOnline @connectParams
    Write-Log "Exchange Online connected"

    if (-not (Get-Command -Name "Get-TransportRule" -ErrorAction SilentlyContinue)) {
        if (-not $UseRPSSession) {
            throw "Transport rule cmdlets are unavailable in REST mode. Re-run with -UseRPSSession."
        }
        throw "Transport rule cmdlets are unavailable after connection. Verify WinRM basic auth is enabled."
    }

    $existingRule = Get-ExistingRule -Name $RuleName
    if ($existingRule) {
        Write-Log "Existing rule found: $RuleName"
    }
    else {
        Write-Log "No existing rule found: $RuleName" -Level "WARN"
    }

    switch ($requestedAction) {
        "Status" {
            if ($existingRule) {
                Write-Log "Status: rule exists and is $($existingRule.State)" -Level "INFO"
            }
            else {
                Write-Log "Status: rule does not exist" -Level "WARN"
            }
            return 0
        }
        "Create" {
            if ($existingRule) {
                throw "Transport rule already exists: $RuleName"
            }
            if ($effectiveDryRun) {
                Write-Log "[DRY RUN] Would create transport rule with template: $resolvedTemplate" -Level "WARN"
                return 0
            }
            if (-not (Confirm-Action -Prompt "Create transport rule '$RuleName'?")) {
                Write-Log "Cancelled by user" -Level "WARN"
                return 0
            }

            New-TransportRule -Name $RuleName `
                -SentToScope NotInOrganization `
                -ApplyHtmlDisclaimerLocation Append `
                -ApplyHtmlDisclaimerText $signatureHtml `
                -ApplyHtmlDisclaimerFallbackAction Wrap

            Write-Log "Transport rule created: $RuleName"
            return 0
        }
        "Update" {
            if (-not $existingRule) {
                throw "Transport rule not found: $RuleName"
            }
            if ($effectiveDryRun) {
                Write-Log "[DRY RUN] Would update transport rule with template: $resolvedTemplate" -Level "WARN"
                return 0
            }
            if (-not (Confirm-Action -Prompt "Update transport rule '$RuleName'?")) {
                Write-Log "Cancelled by user" -Level "WARN"
                return 0
            }

            Set-TransportRule -Identity $RuleName `
                -ApplyHtmlDisclaimerText $signatureHtml

            Write-Log "Transport rule updated: $RuleName"
            return 0
        }
        "Remove" {
            if (-not $existingRule) {
                Write-Log "Nothing to remove; rule not found" -Level "WARN"
                return 0
            }
            if ($effectiveDryRun) {
                Write-Log "[DRY RUN] Would remove transport rule: $RuleName" -Level "WARN"
                return 0
            }
            if (-not (Confirm-Action -Prompt "Remove transport rule '$RuleName'?")) {
                Write-Log "Cancelled by user" -Level "WARN"
                return 0
            }

            Remove-TransportRule -Identity $RuleName -Confirm:$false
            Write-Log "Transport rule removed: $RuleName"
            return 0
        }
    }

    return 0
}

$exitCode = 0
try {
    $exitCode = Invoke-Main
}
catch {
    $message = $_.Exception.Message
    Write-Log "Fatal error: $message" -Level "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Level "ERROR"

    if ($message -match "authentication|unauthorized|login|connect") {
        $exitCode = 2
    }
    elseif ($message -match "Template file not found|Template file is empty|parameter|specified") {
        $exitCode = 3
    }
    elseif ($message -match "already exists|not found") {
        $exitCode = 4
    }
    else {
        $exitCode = 1
    }
}
finally {
    try {
        Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
    }
    catch {
        # Ignore disconnect errors
    }
}

exit $exitCode
