# Proxmox Homelab Deployment Guide

Deploy Proaktiv Dokument Hub to your Proxmox server at `192.168.77.10`.

## Current Deployment (2026-03-14)

- **LXC 203** (`dokument-hub`) on Proxmox `192.168.77.10`
- **App URL:** http://192.168.77.127:3000
- **Backend API:** http://192.168.77.127:8000
- **Database:** Local Postgres in Docker (fresh, no production data)

---

## Quick Deploy (Manual — Proxmox Console)

When SSH is not configured, deploy via the Proxmox web console:

1. Open **Proxmox**: https://192.168.77.10:8006
2. **LXC 203** (dokument-hub) → **Console**
3. Log in (root or your user)
4. Run:

```bash
cd /root/Proaktiv-Dokument-Hub && git fetch origin && git checkout feat/dark-mode-toggle && git pull origin feat/dark-mode-toggle && docker compose restart frontend
```

5. Open http://192.168.77.127:3000

---

## Option A: Ubuntu VM + Docker (Recommended)

### 1. Create VM on Proxmox

1. Log into Proxmox: https://192.168.77.10:8006
2. **Create VM** → Ubuntu 24.04 LTS
   - **Resources:** 2–4 vCPU, 4–8 GB RAM, 32 GB disk
   - **Network:** Bridge (e.g. `vmbr0`), DHCP or static IP
   - **Cloud-init:** Optional, for SSH keys

### 2. Install Docker on the VM

```bash
# SSH into the VM
ssh user@<VM_IP>

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group to apply
```

### 3. Deploy the Application

```bash
# Clone the repo (or rsync/scp from your dev machine)
git clone https://github.com/proaktivadmin/Proaktiv-Dokument-Hub.git
cd Proaktiv-Dokument-Hub

# Copy and configure env
cp backend/.env.docker.example backend/.env.docker
# Edit backend/.env.docker with your values (DATABASE_URL, VITEC_HUB_*, etc.)
nano backend/.env.docker

# For homelab: use local Postgres instead of Railway
# In backend/.env.docker, set:
# DATABASE_URL=postgresql://postgres:postgres@db:5432/dokument_hub

# Build and run
docker compose build --no-cache
docker compose up -d
```

### 4. Networking

**Option A1: Direct port exposure**

- Frontend: `http://<VM_IP>:3000`
- Backend API: `http://<VM_IP>:8000`
- Ensure firewall allows 3000, 8000, 5432 (if needed)

**Option A2: Reverse proxy (recommended)**

- Install Nginx or Traefik on the VM or a separate container
- Use a hostname (e.g. `dokument-hub.home`) and TLS
- Proxy `/api/*` to backend:8000, `/` to frontend:3000

---

## Option B: Proxmox LXC + Docker

Docker in LXC needs a privileged container and kernel features.

### 1. Create LXC

- **Template:** Ubuntu 24.04
- **Privileged:** Yes (required for Docker)
- **Features:** `nesting=1`, `keyctl=1`

### 2. Install Docker

```bash
# Inside LXC
apt update && apt install -y curl
curl -fsSL https://get.docker.com | sh
```

### 3. Deploy

Same as Option A, step 3.

---

## Environment Variables for Homelab

| Variable | Homelab value |
|----------|---------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@db:5432/dokument_hub` |
| `FRONTEND_URL` | `http://<VM_IP>:3000` or your domain |
| `ALLOWED_ORIGINS` | Include your homelab URL |
| `APP_ENV` | `development` or `production` |

Keep `VITEC_HUB_*`, `ENTRA_*`, etc. from your existing `.env.docker` if you need them.

---

## Quick Deploy Script

Save as `deploy-proxmox.sh` and run on the Proxmox VM:

```bash
#!/bin/bash
set -e
REPO_URL="${REPO_URL:-https://github.com/proaktivadmin/Proaktiv-Dokument-Hub.git}"
DIR="${DIR:-Proaktiv-Dokument-Hub}"

if [ ! -d "$DIR" ]; then
  git clone "$REPO_URL" "$DIR"
  cd "$DIR"
else
  cd "$DIR"
  git pull
fi

# Ensure .env.docker exists
[ -f backend/.env.docker ] || cp backend/.env.docker.example backend/.env.docker

docker compose build --no-cache
docker compose up -d

echo "Frontend: http://$(hostname -I | awk '{print $1}'):3000"
```

---

## Access from Your PC

- **Same LAN:** `http://<VM_IP>:3000`
- **Different subnet:** Configure port forwarding or VPN to reach `192.168.77.x`

---

## Notes

- Production uses Railway for backend + Postgres. For homelab-only, use the local `db` service.
- `.env.docker` is gitignored; copy it manually or via a secure transfer.
- For HTTPS, use a reverse proxy (Caddy, Nginx, Traefik) with Let's Encrypt.
