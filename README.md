# Vitec Next Admin Hub (Proaktiv Dokument Hub)

A modern document template management system for Norwegian real estate brokers, integrated with Vitec Next.

![Version](https://img.shields.io/badge/version-3.6-blue)
![Stack](https://img.shields.io/badge/stack-Next.js%2016%20%2B%20FastAPI-green)
![Status](https://img.shields.io/badge/status-production-success)
![Platform](https://img.shields.io/badge/platform-Vercel%20%2B%20Railway-purple)

---

## ✨ What's New (2026-01-28)

### V3.7 Territory Seeding & Dashboard Fixes

- **Territory Seeding**: Imported 1732 assignments from CSV data with 5122 postal codes synced from Bring API.
- **Enhanced Sources**: Added support for new territory sources (`tjenestetorget`, `eiendomsmegler`, `meglersmart`).
- **Dashboard Stability**: Resolved 500 errors on the `/territories` dashboard by correctly initializing source statistics.
- **Office Synchronization**: Added missing offices (Lillestrøm, Ålesund, Lørenskog) to match production data.
- **Integration Testing**: New test suite for territory endpoints.

### V3.6 Design System Enhancement

- **Design token system** - Centralized shadows, transitions, colors
- **Premium UI polish** - Brand-aligned components with micro-interactions
- **Consistent patterns** - Card hover, selection glow, avatar scaling
- **Typography hierarchy** - Serif headings for premium feel
- **Design guide** - `.planning/codebase/DESIGN-SYSTEM.md`

### V3.5 Navigation & Logo Library

- **Reorganized navigation** - Ressurser (files/docs) and Selskap (HR/org) dropdowns
- **Logo Library** - Proaktiv logos with preview, copy URL, and download
- **Avatar resizing** - Server-side image cropping for proper profile pictures
- **Sub-offices** - Parent-child office hierarchy with display on cards

### V3.4 Portal Skins Preview

- **Vitec portal skins** - Budportal and Visningsportal with Proaktiv branding
- **Fullscreen preview** - Accurate representation of live portals

### V3.2 Stack Upgrade + CI/CD

- **Next.js 16** + React 19 + Tailwind CSS 4 + TypeScript 5.9
- **GitHub Actions** - ESLint, TypeScript, Vitest, Ruff, Pyright, Pytest
- **Sentry** - Error tracking for frontend and backend

---

## 🎯 Key Features

| Feature                 | Description                                                           |
| ----------------------- | --------------------------------------------------------------------- |
| **Document-First View** | Preview templates as rendered documents, not code                     |
| **Shelf Layout**        | Templates organized in visual card shelves by channel                 |
| **Smart Sanitizer**     | Strip inline CSS and normalize HTML for Vitec compatibility           |
| **Merge Field Library** | 142+ flettekoder with one-click copy                                  |
| **Code Patterns**       | Pre-built Vitec logic snippets (if/else, loops)                       |
| **Template Settings**   | Configure margins, headers/footers, and Vitec "Kategorisering" fields |
| **Variable Simulator**  | Test documents with sample data before deployment                     |
| **Logo Library**        | Proaktiv logos with preview, copy URL, and download                   |
| **Portal Skins**        | Preview Vitec Budportal and Visningsportal with custom branding       |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js 16    │────▶│    FastAPI      │────▶│   PostgreSQL    │
│   (Vercel)      │     │   (Railway)     │     │   (Railway)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Tech Stack

- **Frontend:** Next.js 16 (App Router), React 19, Tailwind CSS 4, Shadcn/UI
- **Backend:** FastAPI, Pydantic, SQLAlchemy (async)
- **Database:** PostgreSQL with JSONB fields
- **Hosting:** Vercel (frontend) + Railway (backend + database)
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry
- **Design:** Custom design token system (see `.planning/codebase/DESIGN-SYSTEM.md`)

---

## 🚀 Quick Start

### Prerequisites

- **Homelab:** Docker & Docker Compose on Proxmox LXC (192.168.77.127)
- **This PC:** Node.js 18+ and Python 3.11+ for lint/tests (Docker not required)

### Start Development Environment (Homelab)

```powershell
# Clone the repository
git clone https://github.com/proaktivadmin/Proaktiv-Dokument-Hub.git
cd Proaktiv-Dokument-Hub

# Deploy to homelab (SSH to Proxmox, builds and starts)
.\scripts\deploy-homelab.ps1

# Access the application
# http://192.168.77.127:3000
```

### Health Checks

```bash
# Backend API (homelab)
curl http://192.168.77.127:8000/api/health

# Frontend (homelab)
curl http://192.168.77.127:3000
```

### Production URLs

- **Frontend (Vercel):** https://proaktiv-dokument-hub.vercel.app
- **Backend (Railway):** https://proaktiv-admin.up.railway.app

---

## 📁 Project Structure

```
proaktiv-dokument-hub/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # Pages (templates, assets, offices, employees)
│   │   ├── components/      # React components
│   │   │   ├── assets/      # Asset gallery, LogoLibrary
│   │   │   ├── shelf/       # Template card and shelf components
│   │   │   ├── templates/   # Document viewer, settings, simulator
│   │   │   ├── offices/     # Office cards and management
│   │   │   ├── employees/   # Employee cards and Entra sync
│   │   │   └── portal/      # Portal mockup components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # API client and utilities
│   │   └── types/           # TypeScript interfaces
│   └── public/              # Static assets

├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── services/        # Business logic (async)
│   │   │   ├── image_service.py    # Avatar resizing
│   │   │   └── ...
│   │   ├── routers/         # API endpoints
│   │   └── schemas/         # Pydantic models
│   ├── alembic/             # Database migrations
│   └── scripts/             # Utility scripts (sync, import)

├── skins/                    # Vitec portal skin packages
│   ├── proaktiv-bud/        # Budportal skin
│   └── proaktiv-visning/    # Visningsportal skin

└── .planning/                # Project planning
    ├── STATE.md             # Current status
    ├── ROADMAP.md           # Phase breakdown
    └── phases/              # Phase plans
```

---

## 🔧 Navigation Structure

### Ressurser (Files & Documents)

- **Maler** - Document templates
- **Kategorier** - Template categories
- **Mediefiler** - Assets, logos (includes Proaktiv Logoer tab)
- **WebDAV Lagring** - WebDAV file browser

### Selskap (HR & Organization)

- **Kontorer** - Offices/departments
- **Ansatte** - Employees
- **Markedsområder** - Market territories
- **Mottakere** - Recipients

### Verktøy (Tools)

- **Sanitizer** - HTML cleanup
- **Synkronisering** - Vitec sync
- **Portal Skins** - Portal preview

---

## 🚀 Deployment

The app deploys automatically when you push to the `main` branch:

- Frontend → Vercel
- Backend → Railway

### Environment Variables

**Backend (Railway):**

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret
- `APP_PASSWORD_HASH` - bcrypt hash for auth
- `VITEC_HUB_*` - Vitec API credentials
- `SENTRY_DSN` - Error tracking

**Frontend (Vercel):**

- `BACKEND_URL` - Railway backend URL (for rewrites)
- `NEXT_PUBLIC_SENTRY_DSN` - Error tracking

---

## 📝 Documentation

- [CLAUDE.md](CLAUDE.md) - Project conventions for AI agents
- [.planning/STATE.md](.planning/STATE.md) - Current project status
- [.planning/codebase/DESIGN-SYSTEM.md](.planning/codebase/DESIGN-SYSTEM.md) - Frontend design guidelines
- [docs/](docs/) - Additional documentation

---

## 🤝 Contributing

1. Read `CLAUDE.md` for project conventions
2. Check `.planning/STATE.md` for current status
3. **For UI work**: Follow `.planning/codebase/DESIGN-SYSTEM.md`
4. Follow the agent pipeline for major features
5. Push to `main` for production deployment

---

## 📄 License

Proprietary - Proaktiv Eiendomsmegling AS
