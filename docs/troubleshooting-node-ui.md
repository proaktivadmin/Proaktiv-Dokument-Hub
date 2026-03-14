# Node.js and UI Troubleshooting

Common Node.js errors and UI issues when running the Proaktiv Dokument Hub frontend.

---

## Quick Fixes

| Symptom | Likely cause | Fix |
|--------|--------------|-----|
| `ECONNRESET` / "Kan ikke koble til serveren" | Backend not running | Homelab: `.\scripts\deploy-homelab.ps1` or SSH and `docker compose up -d` |
| `502 Bad Gateway` on reports | Vitec Hub API failure | See [reports-502-debugging.md](./reports-502-debugging.md) |
| `Module not found: @radix-ui/react-switch` | Missing dependency | `cd frontend && npm install @radix-ui/react-switch` |
| Theme flash / wrong colors on load | ThemeProvider hydration | Expected; resolves after mount. Use `?dark=1` or `?dark=0` to force. |
| `[object Object]` in console | Old WebVitals logging | Fixed in current codebase; ensure you're on latest. |

---

## ECONNRESET and API Connection Errors

**Symptom:** Console shows `ECONNRESET`, `ERR_NETWORK`, or "Nettverksfeil: Kan ikke koble til serveren".

**Cause:** The frontend proxies `/api/*` to the backend. If the backend is not running, requests fail.

**Fix:**

1. **Homelab (primary):** Docker runs on Proxmox LXC only. Deploy:
   ```powershell
   .\scripts\deploy-homelab.ps1
   ```
   Or SSH and run: `docker compose up -d` inside LXC 203.

2. **Homelab — backend down:** Ensure the backend container is running:
   ```bash
   docker compose ps
   docker compose up -d backend
   ```

3. **Production (Vercel + Railway):** Backend runs on Railway. If you see ECONNRESET in production, check Railway logs and service health.

---

## Node.js / Next.js Errors

### Proxy (Middleware) Deprecation

Next.js 16 renamed `middleware.ts` to `proxy.ts`. The project uses `frontend/src/proxy.ts` with `export function proxy()`. If you see deprecation warnings, ensure no `middleware.ts` exists and the proxy export is correct.

### Turbopack Lockfile Warning

If you see a lockfile warning during dev, `next.config.js` sets `turbopack.root` to silence it. No action needed.

### Hydration Mismatch

`useSearchParams()` in ThemeProvider can cause hydration warnings. The layout wraps ThemeProvider in `<Suspense>`, which mitigates this. If you add new `useSearchParams` usage, wrap the component in Suspense.

---

## UI Issues

### Dark Mode Toggle Not Persisting

Theme is driven by `?dark=1` / `?dark=0` in the URL. The toggle updates the URL; if you navigate without the param, it falls back to Oslo time (18:00–07:00 = dark). To force light/dark, keep the query param in the URL.

### Cards / Layout Look Wrong

Ensure design tokens are used (see `.planning/codebase/DESIGN-SYSTEM.md`). Avoid hardcoded colors; use `bg-card`, `text-foreground`, `border-border`, etc.

### Console Spam from API Errors

The API layer logs errors with `[API Error]` prefix. These are expected when:
- Backend is down (ECONNRESET)
- Vitec Hub returns 502 (see reports-502-debugging.md)
- Auth session expired (redirect to /login)

To reduce noise in development, you can temporarily comment out `console.error` in `frontend/src/lib/api.ts` — but keep error handling logic intact.

---

## Verification

After applying fixes:

```bash
# Frontend (on this PC — no Docker needed)
cd frontend
npm run build
npm run lint

# Full stack — homelab only
.\scripts\deploy-homelab.ps1
curl http://192.168.77.127:8000/api/health
# Open http://192.168.77.127:3000
```

## Docker: Homelab Only (Production Parity)

Docker runs on the **homelab** (Proxmox LXC at 192.168.77.127), not on this PC. Deploy with `.\scripts\deploy-homelab.ps1`. The frontend runs a **production build** (same as Vercel). For hot reload, SSH in and run:

```bash
docker compose --profile dev up frontend-dev
# Frontend at http://192.168.77.127:3001
```

---

## Related Docs

- [reports-502-debugging.md](./reports-502-debugging.md) — Reports page 502 errors
- [database-access-workflow.md](./database-access-workflow.md) — DB access
- [proxmox-deployment.md](./proxmox-deployment.md) — Homelab deploy
