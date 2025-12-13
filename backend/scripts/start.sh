#!/bin/bash
set -e

echo "🚀 Starting Proaktiv Dokument Hub Backend..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done
echo "✅ Database is ready!"

# Run migrations
echo "📦 Running database migrations..."
cd /app
alembic upgrade head
echo "✅ Migrations complete!"

# Start the application
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"

