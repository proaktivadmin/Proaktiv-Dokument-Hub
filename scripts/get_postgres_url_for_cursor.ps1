# Get Railway Postgres URL for Cursor MCP
# Run this when the Postgres password changes to get the updated connection string.
# Copy the output and update Cursor's mcp.json postgres args.
#
# Usage:
#   railway service   # Select "Proaktiv-Dokument-Hub" (backend - has resolved DATABASE_URL)
#   .\scripts\get_postgres_url_for_cursor.ps1

$url = railway run powershell -Command "Write-Output `$env:DATABASE_URL"
if ($url) {
    Write-Host ""
    Write-Host "Copy this URL and update Cursor's mcp.json:" -ForegroundColor Green
    Write-Host "  File: $env:USERPROFILE\.cursor\mcp.json" -ForegroundColor Gray
    Write-Host "  Replace the postgres connection string in the 'args' array." -ForegroundColor Gray
    Write-Host ""
    Write-Host $url
    Write-Host ""
} else {
    Write-Host "Could not get DATABASE_URL. Ensure Railway CLI is linked and run:" -ForegroundColor Yellow
    Write-Host "  railway service   # Select Postgres"
    Write-Host "  railway variables"
}
