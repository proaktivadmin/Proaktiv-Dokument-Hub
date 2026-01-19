# Vitec Next Admin Hub (Proaktiv Dokument Hub)

A modern document template management system for Norwegian real estate brokers, integrated with Vitec Next.

![Version](https://img.shields.io/badge/version-3.x-blue)
![Stack](https://img.shields.io/badge/stack-Next.js%20%2B%20FastAPI-green)
![Status](https://img.shields.io/badge/status-production-success)
![Platform](https://img.shields.io/badge/platform-Railway-purple)

---

## ✨ What’s New (2026-01-18)

### Template workflow parity with Vitec Next
- **Origin marker** (Vitec Next vs Kundemal) and list grouping
- **Attachments** (paperclip count + names) in list/cards/detail
- **Kategorisering fields** available in the Settings UI (type/receiver/phases/etc.)
- **Pagination fixes** in list view

### Import tooling for Vitec Next templates
- `backend/scripts/import_vitec_next_export.py`
- `docs/vitec-next-export-format.md`
- `docs/vitec-next-mcp-scrape-and-import.md`

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Document-First View** | Preview templates as rendered documents, not code |
| **Shelf Layout** | Templates organized in visual card shelves by channel |
| **Smart Sanitizer** | Strip inline CSS and normalize HTML for Vitec compatibility |
| **Merge Field Library** | 142+ flettekoder with one-click copy |
| **Code Patterns** | Pre-built Vitec logic snippets (if/else, loops) |
| **Template Settings** | Configure margins, headers/footers, and Vitec “Kategorisering” fields |
| **Variable Simulator** | Test documents with sample data before deployment |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│    FastAPI      │────▶│   PostgreSQL    │
│   (Frontend)    │     │    (Backend)    │     │   (Database)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                            Railway
```

### Tech Stack
- **Frontend:** Next.js 14 (App Router), React, Tailwind CSS, Shadcn/UI
- **Backend:** FastAPI, Pydantic, SQLAlchemy (async)
- **Database:** PostgreSQL with JSONB fields
- **Hosting:** Railway (all services)
- **Editor:** Monaco Editor for code viewing/editing

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Start Development Environment

```bash
# Clone the repository
git clone https://github.com/Adrian12341234-code/Proaktiv-Dokument-Hub.git
cd Proaktiv-Dokument-Hub

# Start all services
docker compose up -d

# Access the application
open http://localhost:3000
```

### Health Checks

```bash
# Backend API
curl http://localhost:8000/api/health

# Frontend
curl http://localhost:3000
```

### Production URLs

- **Frontend:** https://blissful-quietude-production.up.railway.app
- **Backend API:** https://proaktiv-dokument-hub-production.up.railway.app

---

## 📁 Project Structure

```
proaktiv-dokument-hub/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # Pages (templates, flettekoder, sanitizer)
│   │   ├── components/      # React components
│   │   │   ├── shelf/       # Template card and shelf components
│   │   │   ├── templates/   # Document viewer, settings, simulator
│   │   │   ├── flettekoder/ # Merge field library components
│   │   │   └── editor/      # Monaco code editor
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # API client and utilities
│   │   └── types/           # TypeScript interfaces
│   └── public/              # Static assets (vitec-theme.css)
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── services/        # Business logic (async)
│   │   ├── routers/         # API endpoints
│   │   └── schemas/         # Pydantic models
│   └── alembic/             # Database migrations
│
└── .cursor/                  # Agent context and specs
    ├── active_context.md    # Current project status
    ├── specs/               # Architecture specifications
    └── agents/              # Agent prompts
```

---

## 🔧 Core Concepts

### Flettekoder (Merge Fields)
Templates use a custom merge field syntax compatible with Vitec Next:

```html
<!-- Simple field -->
<p>Kjøper: [[kjøper.navn]]</p>

<!-- Required field (asterisk) -->
<p>Pris: [[*eiendom.pris]]</p>

<!-- Conditional content -->
<div vitec-if="eiendom.fellesgjeld > 0">
  Fellesgjeld: [[eiendom.fellesgjeld]]
</div>

<!-- Loop -->
<ul vitec-foreach="selger in selgere">
  <li>[[selger.navn]]</li>
</ul>
```

### Template Channels
- **PDF** - Print-ready documents
- **Email** - HTML emails with inline styles
- **SMS** - Plain text messages
- **PDF + Email** - Dual-purpose templates

---

## 🚀 Deployment

The app deploys automatically to Railway when you push to the `main` branch.

### Railway Services
1. **proaktiv-dokument-hub** - Backend (FastAPI)
2. **blissful-quietude** - Frontend (Next.js)
3. **PostgreSQL** - Database

### Environment Variables
Backend requires:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret
- `APP_ENV` - Environment (production)
- `VITEC_INSTALLATION_ID` - Vitec Hub installation ID (e.g., MSPROATEST)
- `VITEC_HUB_BASE_URL` - Hub base URL (QA: https://proatest.qa.vitecnext.no)
- `VITEC_HUB_PRODUCT_LOGIN` - Product login username
- `VITEC_HUB_ACCESS_KEY` - Product access key

Frontend requires:
- `BACKEND_URL` - Backend API URL

### Vitec Hub QA Sync (Manual)
```bash
# Verify product login access (QA)
curl -u "$VITEC_HUB_PRODUCT_LOGIN:$VITEC_HUB_ACCESS_KEY" \
  https://proatest.qa.vitecnext.no/Account/Methods

# Sync offices (departments)
curl -X POST http://localhost:8000/api/offices/sync

# Sync employees
curl -X POST http://localhost:8000/api/employees/sync
```

---

## 📝 Documentation

- [CLAUDE.md](CLAUDE.md) - Project conventions for AI agents
- [.cursor/active_context.md](.cursor/active_context.md) - Current project status
- [docs/vitec-next-mcp-scrape-and-import.md](docs/vitec-next-mcp-scrape-and-import.md) - Vitec export + import workflow

---

## 🤝 Contributing

1. Read `CLAUDE.md` for project conventions
2. Check `.cursor/active_context.md` for current status
3. Follow the agent pipeline for major features
4. Push to `main` for production deployment

---

## 📄 License

Proprietary - Proaktiv Eiendomsmegling AS
