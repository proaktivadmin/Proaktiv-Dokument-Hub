# Start Development Environment (Homelab)

Docker runs on the **homelab** (Proxmox LXC), not on this PC. Use the deploy script or SSH:

1. Deploy to homelab: `.\scripts\deploy-homelab.ps1`
2. Or SSH and run manually:
   ```powershell
   ssh root@192.168.77.10 "pct exec 203 -- bash -c 'cd /root/Proaktiv-Dokument-Hub && docker compose up -d'"
   ```
3. Test backend health: `curl http://192.168.77.127:8000/api/health`
4. Verify frontend: http://192.168.77.127:3000
5. Report status of all services

**Note:** The frontend runs a **production build** (identical to Vercel) for parity testing. For hot reload, use `--profile dev` and `frontend-dev` (port 3001).

If any service fails, show logs: `ssh root@192.168.77.10 "pct exec 203 -- docker compose logs [service]"`
