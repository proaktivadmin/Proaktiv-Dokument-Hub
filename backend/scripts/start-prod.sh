#!/bin/bash
set -e

echo "🚀 Starting Proaktiv Dokument Hub Backend..."

cd /app

# Run Alembic migrations
echo "📦 Running database migrations..."
alembic upgrade head
echo "✅ Migrations complete!"

# Start the application
echo "🌐 Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
