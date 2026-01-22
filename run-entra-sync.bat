@echo off
REM ============================================================================
REM Entra ID Employee Sync - Windows Launcher
REM 
REM Syncs employee data from PostgreSQL to Microsoft Entra ID and Exchange Online.
REM Run with -DryRun first to preview changes!
REM
REM Prerequisites:
REM   - PowerShell 7+ (pwsh)
REM   - Python 3.12+
REM   - Microsoft.Graph PowerShell modules
REM   - ExchangeOnlineManagement module
REM
REM Environment Variables (set these before running):
REM   - ENTRA_TENANT_ID: Azure AD tenant ID
REM   - ENTRA_CLIENT_ID: App registration client ID
REM   - ENTRA_CLIENT_SECRET: App registration secret (or use certificate)
REM   - ENTRA_ORGANIZATION: Microsoft 365 organization (e.g., proaktiv.onmicrosoft.com)
REM   - DATABASE_URL: PostgreSQL connection string (optional, uses backend/.env if not set)
REM
REM Usage:
REM   run-entra-sync.bat                     - Interactive mode (prompts for parameters)
REM   run-entra-sync.bat --dry-run           - Dry run with env vars
REM   run-entra-sync.bat --filter ola@x.com  - Single user test
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo                    PROAKTIV - ENTRA ID EMPLOYEE SYNC
echo ================================================================================
echo.

REM Check for pwsh (PowerShell 7+)
where pwsh >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PowerShell 7+ ^(pwsh^) not found.
    echo         Install from: https://aka.ms/powershell
    echo.
    pause
    exit /b 1
)

REM Parse command line arguments
set DRY_RUN=
set FILTER_EMAIL=
set SKIP_PROFILE=
set SKIP_PHOTO=
set SKIP_SIGNATURE=

:parse_args
if "%~1"=="" goto :done_parsing
if /i "%~1"=="--dry-run" (
    set DRY_RUN=-DryRun
    shift
    goto :parse_args
)
if /i "%~1"=="--filter" (
    set FILTER_EMAIL=-FilterEmail "%~2"
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--skip-profile" (
    set SKIP_PROFILE=-SkipProfile
    shift
    goto :parse_args
)
if /i "%~1"=="--skip-photo" (
    set SKIP_PHOTO=-SkipPhoto
    shift
    goto :parse_args
)
if /i "%~1"=="--skip-signature" (
    set SKIP_SIGNATURE=-SkipSignature
    shift
    goto :parse_args
)
shift
goto :parse_args

:done_parsing

REM Check required environment variables
if "%ENTRA_TENANT_ID%"=="" (
    echo [WARN] ENTRA_TENANT_ID not set. Will prompt for input.
)
if "%ENTRA_CLIENT_ID%"=="" (
    echo [WARN] ENTRA_CLIENT_ID not set. Will prompt for input.
)
if "%ENTRA_ORGANIZATION%"=="" (
    echo [WARN] ENTRA_ORGANIZATION not set. Will prompt for input.
)

echo.
echo Running Entra ID sync script...
echo.

REM Build PowerShell command
set PS_ARGS=
if defined ENTRA_TENANT_ID set PS_ARGS=!PS_ARGS! -TenantId "%ENTRA_TENANT_ID%"
if defined ENTRA_CLIENT_ID set PS_ARGS=!PS_ARGS! -ClientId "%ENTRA_CLIENT_ID%"
if defined ENTRA_ORGANIZATION set PS_ARGS=!PS_ARGS! -Organization "%ENTRA_ORGANIZATION%"
if defined ENTRA_CERT_THUMBPRINT set PS_ARGS=!PS_ARGS! -CertificateThumbprint "%ENTRA_CERT_THUMBPRINT%"
set PS_ARGS=!PS_ARGS! %DRY_RUN% %FILTER_EMAIL% %SKIP_PROFILE% %SKIP_PHOTO% %SKIP_SIGNATURE%

REM Execute PowerShell script
pwsh -ExecutionPolicy Bypass -File "%~dp0backend\scripts\Sync-EntraIdEmployees.ps1" !PS_ARGS!

set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE%==0 (
    echo [SUCCESS] Sync completed successfully.
) else if %EXIT_CODE%==1 (
    echo [WARNING] Sync completed with some skipped/failed users.
) else if %EXIT_CODE%==2 (
    echo [ERROR] Authentication failure. Check credentials.
) else if %EXIT_CODE%==3 (
    echo [ERROR] Database connection failure. Check DATABASE_URL.
) else if %EXIT_CODE%==4 (
    echo [ERROR] Invalid parameters. Check command line arguments.
) else if %EXIT_CODE%==5 (
    echo [ERROR] Missing dependencies. Install required PowerShell modules.
) else (
    echo [ERROR] Unknown error ^(exit code: %EXIT_CODE%^).
)

echo.
pause
exit /b %EXIT_CODE%
