@echo off
setlocal

REM Convenience launcher for the Proaktiv directory scraper (PowerShell).
REM Usage examples:
REM   run-proaktiv-scraper.bat -Preset all -Migrate -Overwrite
REM   run-proaktiv-scraper.bat -TargetDb railway -Migrate -Preset all -Overwrite
REM
REM NOTE: For Railway runs, set env var RAILWAY_DATABASE_URL (recommended) before running.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0backend\scripts\run_proaktiv_directory_sync.ps1" %*

endlocal
