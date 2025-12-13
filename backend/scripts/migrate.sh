#!/bin/bash
# Database migration helper script
set -e

cd /app

case "$1" in
  upgrade)
    echo "⬆️  Running upgrade to ${2:-head}..."
    alembic upgrade ${2:-head}
    ;;
  downgrade)
    echo "⬇️  Running downgrade to ${2:--1}..."
    alembic downgrade ${2:--1}
    ;;
  revision)
    echo "📝 Creating new revision..."
    alembic revision --autogenerate -m "${2:-Auto migration}"
    ;;
  history)
    echo "📜 Migration history:"
    alembic history
    ;;
  current)
    echo "📍 Current revision:"
    alembic current
    ;;
  *)
    echo "Usage: $0 {upgrade|downgrade|revision|history|current} [args]"
    echo ""
    echo "Commands:"
    echo "  upgrade [revision]   - Upgrade to a revision (default: head)"
    echo "  downgrade [revision] - Downgrade to a revision (default: -1)"
    echo "  revision [message]   - Create new auto-generated revision"
    echo "  history              - Show migration history"
    echo "  current              - Show current revision"
    exit 1
    ;;
esac

echo "✅ Done!"

