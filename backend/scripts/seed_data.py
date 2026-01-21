"""
Seed Data Script

Populates the database with initial categories and tags.
Run with: python -m scripts.seed_data
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.services.category_service import CategoryService
from app.services.tag_service import TagService

# Initial tags based on legacy system
INITIAL_TAGS = [
    {"name": "Kontrakt", "color": "#EF4444"},
    {"name": "Bolig", "color": "#10B981"},
    {"name": "AML", "color": "#8B5CF6"},
    {"name": "Salg", "color": "#F59E0B"},
    {"name": "Kjøper", "color": "#3B82F6"},
    {"name": "Selger", "color": "#EC4899"},
    {"name": "Forkjøpsrett", "color": "#14B8A6"},
    {"name": "Tinglysing", "color": "#6366F1"},
]

# Initial categories based on legacy library folder structure
INITIAL_CATEGORIES = [
    {"name": "Akseptbrev", "icon": "FileCheck", "description": "Akseptbrev og bekreftelser"},
    {"name": "AML", "icon": "Shield", "description": "Anti-hvitvaskingsdokumenter og risikovurderinger"},
    {"name": "Bortefester", "icon": "Home", "description": "Dokumenter for bortefester"},
    {"name": "Følgebrev", "icon": "Mail", "description": "Følgebrev og tinglysningsdokumenter"},
    {"name": "Forkjøpsrett", "icon": "Scale", "description": "Forkjøpsrett og borettslag"},
    {"name": "Forretningsfører", "icon": "Building", "description": "Kommunikasjon med forretningsfører"},
    {"name": "Informasjonsbrev", "icon": "Info", "description": "Informasjonsbrev til kjøper og selger"},
    {"name": "Kontrakt", "icon": "FileText", "description": "Kontrakter og avtaler"},
    {"name": "Salgsmelding", "icon": "Megaphone", "description": "Salgsmeldinger"},
    {"name": "SMS", "icon": "MessageSquare", "description": "SMS-maler"},
    {"name": "Topptekst", "icon": "Type", "description": "Topptekster og bunntekster"},
]


async def seed_tags(db: AsyncSession) -> int:
    """Seed initial tags."""
    count = 0
    for tag_data in INITIAL_TAGS:
        try:
            await TagService.create(db, **tag_data)
            count += 1
            print(f"  ✓ Created tag: {tag_data['name']}")
        except ValueError:
            print(f"  - Tag exists: {tag_data['name']}")
    return count


async def seed_categories(db: AsyncSession) -> int:
    """Seed initial categories."""
    count = 0
    for i, cat_data in enumerate(INITIAL_CATEGORIES):
        try:
            await CategoryService.create(db, sort_order=i + 1, **cat_data)
            count += 1
            print(f"  ✓ Created category: {cat_data['name']}")
        except ValueError:
            print(f"  - Category exists: {cat_data['name']}")
    return count


async def main():
    """Run seed data script."""
    print("🌱 Seeding database with initial data...\n")

    async with async_session_factory() as db:
        print("📌 Creating tags...")
        tags_created = await seed_tags(db)

        print("\n📁 Creating categories...")
        cats_created = await seed_categories(db)

        print(f"\n✅ Done! Created {tags_created} tags and {cats_created} categories.")


if __name__ == "__main__":
    asyncio.run(main())
