# Proaktiv Dokument Hub V2.6

A modern document template management system for Norwegian real estate brokers, integrated with Vitec Next.

![Version](https://img.shields.io/badge/version-2.6-blue)
![Stack](https://img.shields.io/badge/stack-Next.js%20%2B%20FastAPI-green)
![Status](https://img.shields.io/badge/status-production-success)

---

## ✨ What's New in V2.6

### Live Document Preview Thumbnails
Template cards now display **live previews** of document content, making it easy to visually identify templates at a glance.

### A4 Page Break Visualization
Toggle to see exactly where page breaks will occur on A4 paper - red dashed lines mark the 257mm content boundaries.

### Simulator Test Data Persistence
Default test values for merge fields are now **saved to your browser**, with options to save your own defaults, reset to system defaults, or clear all values.

### Visual Code Generator
Build Vitec code snippets (if/else, loops, inline conditions) without writing code - just click and copy.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Document-First View** | Preview templates as rendered documents, not code |
| **Shelf Layout** | Templates organized in visual card shelves by channel |
| **Smart Sanitizer** | Strip inline CSS and normalize HTML for Vitec compatibility |
| **Merge Field Library** | 142+ flettekoder with one-click copy |
| **Code Patterns** | Pre-built Vitec logic snippets (if/else, loops) |
| **Template Settings** | Configure margins, headers, footers, and themes |
| **Variable Simulator** | Test documents with sample data before deployment |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│    FastAPI      │────▶│   PostgreSQL    │
│   (Frontend)    │     │    (Backend)    │     │   (Database)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Azure Blob     │
                        │  Storage        │
                        └─────────────────┘
```

### Tech Stack
- **Frontend:** Next.js 14 (App Router), React, Tailwind CSS, Shadcn/UI
- **Backend:** FastAPI, Pydantic, SQLAlchemy (async)
- **Database:** PostgreSQL with JSONB fields
- **Storage:** Azure Blob Storage for templates
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
git clone https://github.com/your-org/proaktiv-dokument-hub.git
cd proaktiv-dokument-hub

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
├── .cursor/                  # Agent context and specs
│   ├── active_context.md    # Current project status
│   ├── specs/               # Architecture specifications
│   └── agents/              # Agent prompts
│
└── documentation/           # Project documentation
    ├── AI_HANDOFF.md        # Agent handoff protocol
    ├── BRAND_GUIDE.md       # Design guidelines
    └── API_REFERENCE.md     # API documentation
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

## 📊 Current Status

| Metric | Value |
|--------|-------|
| Templates | 43 |
| Merge Fields | 142 |
| Code Patterns | 10 |
| Categories | 12 |

---

## 🔐 Security

- Azure Easy Auth for production authentication
- Mocked authentication for local development
- All API endpoints protected in production

---

## 📝 Documentation

- [AI Handoff Protocol](documentation/AI_HANDOFF.md) - For AI agents
- [Brand Guide](documentation/BRAND_GUIDE.md) - Design standards
- [API Reference](documentation/API_REFERENCE.md) - Backend endpoints

---

## 🤝 Contributing

1. Read `CLAUDE.md` for project conventions
2. Check `.cursor/active_context.md` for current status
3. Follow the agent pipeline for major features
4. Update documentation with code changes

---

## 📄 License

Proprietary - Proaktiv Eiendomsmegling AS

---

*Built with ❤️ for Norwegian real estate professionals*
