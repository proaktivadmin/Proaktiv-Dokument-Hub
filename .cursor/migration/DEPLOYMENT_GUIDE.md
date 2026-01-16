# Deployment Guide: Railway + Vercel

**Date:** 2026-01-16
**Status:** Ready for Deployment

This guide walks you through deploying the migrated application to Railway (backend) and Vercel (frontend).

---

## Prerequisites

- [x] Railway account (linked to GitHub)
- [x] Vercel account (linked to GitHub)
- [x] GitHub repository: `Proaktiv-Dokument-Hub`
- [x] Migration changes committed to branch

---

## Part 1: Railway Backend Setup

### Step 1: Create New Project
1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose `Proaktiv-Dokument-Hub` repository
5. When asked for branch, select `V2-development` (or your current branch)

### Step 2: Configure Root Directory
1. In project settings, set **Root Directory** to: `backend`
2. Railway will auto-detect the Dockerfile

### Step 3: Add PostgreSQL Database
1. Click **"+ New"** in your project
2. Select **"Database"** → **"PostgreSQL"**
3. Railway automatically creates `DATABASE_URL` variable

### Step 4: Set Environment Variables
Click on your backend service, go to **Variables** tab:

| Variable | Value |
|----------|-------|
| `APP_ENV` | `production` |
| `SECRET_KEY` | Click "Generate" for a random 32-char string |
| `ALLOWED_ORIGINS` | `["https://YOUR-APP.vercel.app"]` (update after Vercel setup) |
| `PLATFORM` | `railway` |
| `LOG_LEVEL` | `INFO` |

**Note:** Leave `DATABASE_URL` alone - Railway manages this automatically.

### Step 5: Wait for Deployment
Railway will:
1. Build the Docker image
2. Run database migrations (via startup script)
3. Start the FastAPI server

**Expected Time:** 2-5 minutes

### Step 6: Get Backend URL
1. Go to your backend service
2. Click **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://dokumenthub-production.up.railway.app`)

### Step 7: Verify Backend
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/api/health
```

Expected:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

---

## Part 2: Vercel Frontend Setup

### Step 1: Create New Project
1. Go to https://vercel.com/new
2. Click **"Import"**
3. Select `Proaktiv-Dokument-Hub` repository
4. Set **Root Directory** to: `frontend`

### Step 2: Configure Build Settings
Vercel should auto-detect Next.js. Verify:
- **Framework Preset:** Next.js
- **Build Command:** `npm run build` (default)
- **Output Directory:** (leave empty, Next.js auto-configures)

### Step 3: Set Environment Variables
In the **Environment Variables** section:

| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://YOUR-RAILWAY-URL.up.railway.app` |

### Step 4: Deploy
Click **"Deploy"**

**Expected Time:** 1-3 minutes

### Step 5: Get Frontend URL
Vercel provides a URL like: `https://proaktiv-dokument-hub.vercel.app`

---

## Part 3: Update CORS

### Step 1: Update Railway Backend
Go back to Railway and update the `ALLOWED_ORIGINS` variable:

```
["https://proaktiv-dokument-hub.vercel.app"]
```

Or if you have a custom domain:
```
["https://proaktiv-dokument-hub.vercel.app","https://dokumenthub.proaktiv.no"]
```

### Step 2: Redeploy Backend
Railway will automatically redeploy when you save the variable.

---

## Part 4: Import Templates

The templates are currently in the `library/` folder but not in the database.

### Option A: Via curl (if library folder is in container)
```bash
curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/api/admin/import-templates
```

### Option B: Manual seeding
If the library folder isn't available in the container, you'll need to:
1. Connect to the PostgreSQL database
2. Run a seed script locally that inserts template content

**Check import status:**
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/api/admin/template-content-stats
```

Expected:
```json
{
  "total_templates": 43,
  "with_content": 43,
  "without_content": 0,
  "percentage_complete": 100.0
}
```

---

## Part 5: Verification

### Health Check
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/api/health
```

### Template List
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/api/templates
```

### Dashboard Stats
```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/api/dashboard/stats
```

### Frontend
Open in browser: `https://proaktiv-dokument-hub.vercel.app`

- [ ] Dashboard loads
- [ ] Template list displays
- [ ] Template preview renders
- [ ] No console errors

---

## Troubleshooting

### "Connection refused" or "CORS error"
- Check `ALLOWED_ORIGINS` includes your Vercel URL
- Verify `BACKEND_URL` in Vercel points to Railway

### "Internal Server Error" (500)
- Check Railway logs for Python errors
- Verify `DATABASE_URL` is correctly linked

### Templates not showing
- Run the import: `POST /api/admin/import-templates`
- Check database has tables: Railway → PostgreSQL → Connect → Query

### Build fails on Railway
- Check `backend/Dockerfile` exists
- Verify `requirements.txt` has all dependencies

### Build fails on Vercel
- Check `frontend/package.json` has all dependencies
- Verify `BACKEND_URL` is set

---

## URLs Summary

| Service | URL |
|---------|-----|
| Railway Backend | `https://YOUR-APP.up.railway.app` |
| Railway PostgreSQL | (internal, via DATABASE_URL) |
| Vercel Frontend | `https://YOUR-APP.vercel.app` |
| API Docs | `https://YOUR-RAILWAY-URL.up.railway.app/docs` |

---

## Cost Estimate

### Railway
- **Hobby Plan:** Free tier includes:
  - $5 credit/month
  - Enough for 1 backend + 1 PostgreSQL (low traffic)
- **Typical usage:** ~$5-10/month after free tier

### Vercel
- **Hobby Plan:** Free for personal projects
  - Unlimited deploys
  - 100GB bandwidth/month
- **Typical usage:** $0/month

**Total:** $0-10/month (vs Azure ~$30-50/month)

---

## Next Steps

After deployment is complete:
1. Run `/migration-qa` to verify everything works
2. Test all critical paths
3. Approve merge to main

---

## Rollback Plan

If something goes wrong:
1. Azure deployment is still running
2. Switch DNS/usage back to Azure URLs
3. No data loss - both systems share same data model
