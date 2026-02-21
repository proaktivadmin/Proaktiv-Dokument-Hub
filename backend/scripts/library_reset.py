"""
Library Reset Script — one-time script to classify and archive legacy templates.

Usage:
  python -m scripts.library_reset              # dry-run (default)
  python -m scripts.library_reset --confirm    # apply changes

This script:
  1. Tags "Vitec Next" templates → origin=vitec_system, workflow_status=published
  2. Tags "Kundemal" templates → origin=custom, keeps workflow_status or sets draft
  3. Remaining templates → is_archived_legacy=True, workflow_status=archived
"""

import argparse
import asyncio
import hashlib
import logging
import sys
from pathlib import Path

# Ensure backend is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, sessionmaker

from app.models.template import Template

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def run_reset(confirm: bool) -> None:
    import os

    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set")
        sys.exit(1)

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Load all templates with their tags
        result = await db.execute(
            select(Template).options(selectinload(Template.tags))
        )
        templates = result.scalars().all()

        stats = {
            "vitec_published": 0,
            "custom_kept": 0,
            "archived_legacy": 0,
            "total": len(templates),
        }

        for tmpl in templates:
            tag_names = {tag.name.strip().lower() for tag in tmpl.tags}
            has_vitec = any("vitec" in n for n in tag_names)
            has_kundemal = any("kundemal" in n for n in tag_names)
            has_content = bool(tmpl.content and tmpl.content.strip())

            if has_vitec and has_content:
                # Vitec Next system templates → publish and hash
                source_hash = compute_hash(tmpl.content) if tmpl.content else None
                if confirm:
                    tmpl.origin = "vitec_system"
                    tmpl.workflow_status = "published"
                    tmpl.vitec_source_hash = source_hash
                stats["vitec_published"] += 1
                logger.info(
                    "  [VITEC] %s (id=%s) → published, origin=vitec_system",
                    tmpl.title,
                    tmpl.id,
                )

            elif has_kundemal:
                # Custom templates → keep current status or set to draft
                new_status = tmpl.workflow_status if tmpl.workflow_status != "archived" else "draft"
                if not has_content:
                    new_status = "draft"
                if confirm:
                    tmpl.origin = "custom"
                    tmpl.workflow_status = new_status
                stats["custom_kept"] += 1
                logger.info(
                    "  [CUSTOM] %s (id=%s) → %s, origin=custom",
                    tmpl.title,
                    tmpl.id,
                    new_status,
                )

            else:
                # Remaining (untagged or other tags) → archive as legacy
                inferred_origin = "vitec_system" if has_content else "custom"
                if confirm:
                    tmpl.is_archived_legacy = True
                    tmpl.workflow_status = "archived"
                    tmpl.origin = inferred_origin
                stats["archived_legacy"] += 1
                logger.info(
                    "  [LEGACY] %s (id=%s) → archived, origin=%s",
                    tmpl.title,
                    tmpl.id,
                    inferred_origin,
                )

        if confirm:
            await db.commit()
            logger.info("")
            logger.info("=== CHANGES APPLIED ===")
        else:
            logger.info("")
            logger.info("=== DRY RUN (no changes made) ===")
            logger.info("Run with --confirm to apply changes.")

        logger.info("")
        logger.info("Summary:")
        logger.info("  Total templates:           %d", stats["total"])
        logger.info("  Vitec Next → published:    %d", stats["vitec_published"])
        logger.info("  Kundemal → custom:         %d", stats["custom_kept"])
        logger.info("  Legacy → archived:         %d", stats["archived_legacy"])

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Library reset script")
    parser.add_argument("--confirm", action="store_true", help="Actually apply changes (default is dry-run)")
    args = parser.parse_args()

    if not args.confirm:
        logger.info("Running in DRY-RUN mode (pass --confirm to apply)")

    asyncio.run(run_reset(confirm=args.confirm))


if __name__ == "__main__":
    main()
