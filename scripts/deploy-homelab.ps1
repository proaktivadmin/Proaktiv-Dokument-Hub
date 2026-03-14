# Deploy latest code to Proxmox homelab
# Docker runs on homelab only — no Docker required on this PC.
# SSH to Proxmox host (192.168.77.10), run pct exec in LXC 203.
# App URL after deploy: http://192.168.77.127:3000

param(
    [string]$Branch = "main",
    [switch]$NoBuild  # Skip frontend build (faster, use only for backend-only changes)
)

$PROXMOX_HOST = "192.168.77.10"
$LXC_ID = "203"
$REPO_DIR = "/root/Proaktiv-Dokument-Hub"
$APP_URL = "http://192.168.77.127:3000"

# Full deploy: fetch, force-checkout (discard local changes), reset to remote, build, up
$buildStep = if ($NoBuild) { "docker compose up -d" } else { "docker compose build frontend && docker compose up -d" }
$innerCmd = "cd $REPO_DIR && git fetch origin && git checkout -f $Branch && git reset --hard origin/$Branch && $buildStep"
$sshCmd = "pct exec $LXC_ID -- bash -c '$innerCmd'"

Write-Host "Deploying branch '$Branch' to homelab (Proxmox $PROXMOX_HOST, LXC $LXC_ID)..." -ForegroundColor Cyan
if ($NoBuild) { Write-Host "Skipping frontend build (-NoBuild)" -ForegroundColor Yellow }

ssh "root@$PROXMOX_HOST" $sshCmd
if ($LASTEXITCODE -eq 0) {
    Write-Host "Done. Frontend: $APP_URL" -ForegroundColor Green
} else {
    Write-Host "SSH failed. Ensure key-based auth: ssh root@$PROXMOX_HOST" -ForegroundColor Red
    exit 1
}
