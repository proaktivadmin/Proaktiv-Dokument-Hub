# Proaktiv Skills Library

This directory contains specialized "Skills" - reusable prompt modules and scripts for specific domains.

## Current Stack (2026-01-22)

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Next.js | 16.1.4 |
| React | React | 19.2.3 |
| Styling | Tailwind CSS | 4.1.18 |
| TypeScript | TypeScript | 5.9.3 |
| Backend | FastAPI | 0.109.0 |
| ORM | SQLAlchemy | 2.0.46 |
| Testing (FE) | Vitest | 4.0.17 |
| Testing (BE) | Pytest | 8.0.0+ |
| CI/CD | GitHub Actions | - |

## How to Use
Agents are instructed to check this directory when encountering complex tasks in specific domains.
- **Usage:** Read the relevant skill file (e.g., `skills/pdf_parsing.md`) to get specific strategies and code patterns.

## Creating New Skills
1. Create a `SKILL_NAME.md` file.
2. Include:
    - **Trigger:** When to use this skill.
    - **Strategy:** The preferred approach/library.
    - **Snippets:** Reusable code blocks.

## Useful Commands

```bash
# Check CI status
gh run list --repo proaktivadmin/Proaktiv-Dokument-Hub --limit 3

# Run local tests
cd frontend && npm run test:run
cd backend && pytest

# Start local dev
docker compose up -d
```
