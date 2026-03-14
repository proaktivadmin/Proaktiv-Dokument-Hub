# Deploy latest code to Proxmox homelab at 192.168.77.127
# Run from project root. Requires SSH access to homelab.

param(
    [string]$Branch = "feat/dark-mode-toggle"
)

$HOMELAB_HOST = "192.168.77.127"
$REPO_DIR = "/root/Proaktiv-Dokument-Hub"
$sshCmd = "cd $REPO_DIR && git fetch origin && git checkout $Branch && git pull origin $Branch && docker compose restart frontend"

Write-Host "Deploying branch '$Branch' to $HOMELAB_HOST..." -ForegroundColor Cyan
Write-Host "If SSH fails, run this manually on the homelab:" -ForegroundColor Yellow
Write-Host "  $sshCmd" -ForegroundColor Gray
Write-Host ""

ssh "root@$HOMELAB_HOST" $sshCmd
if ($LASTEXITCODE -eq 0) {
    Write-Host "Done. Frontend: http://${HOMELAB_HOST}:3000" -ForegroundColor Green
} else {
    Write-Host "SSH failed (password/key required). Run manually on homelab:" -ForegroundColor Red
    Write-Host "  ssh root@$HOMELAB_HOST" -ForegroundColor Gray
    Write-Host "  $sshCmd" -ForegroundColor Gray
    exit 1
}
