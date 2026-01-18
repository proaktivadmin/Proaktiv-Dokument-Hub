"""
Seed script for Vitec categories with vitec_id.

Populates the categories table with Vitec Next document categories sourced
from the reference file: .cursor/vitec-reference.md

Run with: python -m scripts.seed_vitec_categories
Optional: python -m scripts.seed_vitec_categories --source path/to/vitec-reference.md
"""

import argparse
import asyncio
import sys
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

REFERENCE_DEFAULT = Path(__file__).resolve().parents[2] / ".cursor" / "vitec-reference.md"

CATEGORY_LINE_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*)\|\s*$")


def load_categories_from_reference(path: Path) -> List[Tuple[int, str, Optional[str]]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Reference file not found: {path}. Provide --source to the Vitec reference markdown."
        )

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    categories: List[Tuple[int, str, Optional[str]]] = []
    in_table = False

    for line in lines:
        if line.strip().startswith("## Dokumentkategorier"):
            in_table = True
            continue
        if in_table and line.strip().startswith("## "):
            break
        if not in_table:
            continue
        if not line.strip().startswith("|"):
            continue
        if line.strip().startswith("|----"):
            continue

        match = CATEGORY_LINE_RE.match(line.strip())
        if not match:
            continue

        vitec_id = int(match.group(1))
        name = match.group(2).strip()
        folders = match.group(3).strip()
        description = f"Dokumentmapper: {folders}" if folders else None
        categories.append((vitec_id, name, description))

    if not categories:
        raise ValueError("No categories parsed from reference file.")

    return categories


async def seed_vitec_categories(source: Path):
    """Seed Vitec categories using Vitec reference markdown."""
    from app.models.category import Category
    
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        categories = load_categories_from_reference(source)
        count = 0
        for vitec_id, name, description in categories:
            result = await session.execute(select(Category).where(Category.vitec_id == vitec_id))
            category = result.scalar_one_or_none()

            if not category:
                result = await session.execute(select(Category).where(Category.name == name))
                category = result.scalar_one_or_none()

            if category:
                category.name = name
                category.vitec_id = vitec_id
                category.icon = None
                category.description = description
                category.sort_order = vitec_id
            else:
                category = Category(
                    name=name,
                    vitec_id=vitec_id,
                    icon=None,
                    description=description,
                    sort_order=vitec_id,
                )
                session.add(category)

            count += 1
        
        await session.commit()
        print(f"Seeded {count} Vitec categories")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Vitec categories from reference markdown.")
    parser.add_argument(
        "--source",
        type=str,
        default=str(REFERENCE_DEFAULT),
        help="Path to vitec-reference.md (defaults to .cursor/vitec-reference.md)",
    )
    args = parser.parse_args()
    asyncio.run(seed_vitec_categories(Path(args.source)))
