#!/usr/bin/env python3
"""
Download Employee Photos Script

Fetches high-resolution employee photos from Vitec Hub API (primary)
with proaktiv.no fallback, storing them locally.

Usage:
    python backend/scripts/download_employee_photos.py
    python backend/scripts/download_employee_photos.py --dry-run
    python backend/scripts/download_employee_photos.py --employee-id <uuid>
    python backend/scripts/download_employee_photos.py --skip-vitec

    # Use Railway database:
    $env:DATABASE_URL = "postgresql://postgres:PASSWORD@shuttle.proxy.rlwy.net:51557/railway"
    python backend/scripts/download_employee_photos.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import dotenv early to load environment before other imports
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.services.vitec_hub_service import VitecHubService


def get_async_database_url(url: str) -> str:
    """Convert database URL to async format."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


def create_session_factory(db_url: str) -> async_sessionmaker[AsyncSession]:
    """Create a session factory for the given database URL."""
    async_url = get_async_database_url(db_url)

    # Handle SSL for Railway/hosted Postgres
    connect_args: dict = {}
    if "asyncpg" in async_url and ("railway" in async_url.lower() or "rlwy" in async_url.lower()):
        connect_args["ssl"] = True
        # Remove sslmode from URL if present
        if "sslmode=" in async_url:
            import re

            async_url = re.sub(r"[?&]sslmode=[^&]*", "", async_url)

    engine = create_async_engine(
        async_url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args,
    )

    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Default output directory
DEFAULT_OUTPUT_DIR = Path(os.path.expanduser("~")) / "Documents" / "ProaktivPhotos"


class PhotoDownloader:
    """Downloads employee photos from Vitec Hub or proaktiv.no."""

    def __init__(
        self,
        output_dir: Path,
        db_url: str,
        dry_run: bool = False,
        force: bool = False,
        skip_vitec: bool = False,
    ):
        self.output_dir = output_dir
        self.photos_dir = output_dir / "photos"
        self.manifest_path = output_dir / "manifest.json"
        self.log_path = output_dir / "download.log"
        self.dry_run = dry_run
        self.force = force
        self.skip_vitec = skip_vitec
        self.db_url = db_url
        self.session_factory = create_session_factory(db_url)
        self.vitec_service = VitecHubService()
        self.installation_id = settings.VITEC_INSTALLATION_ID
        self.manifest: dict[str, Any] = {"downloaded_at": None, "photos": {}}
        self.stats = {
            "total": 0,
            "downloaded": 0,
            "skipped_exists": 0,
            "skipped_no_source": 0,
            "failed": 0,
            "vitec_success": 0,
            "proaktiv_success": 0,
        }

    def setup_directories(self) -> None:
        """Create output directories if they don't exist."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create directory: {self.output_dir}")
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")

        # Set up file logging
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(file_handler)

    def load_manifest(self) -> None:
        """Load existing manifest if present."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, encoding="utf-8") as f:
                    self.manifest = json.load(f)
                logger.info(f"Loaded manifest with {len(self.manifest.get('photos', {}))} entries")
            except json.JSONDecodeError:
                logger.warning("Could not parse existing manifest, starting fresh")
                self.manifest = {"downloaded_at": None, "photos": {}}

    def save_manifest(self) -> None:
        """Save manifest to disk."""
        if self.dry_run:
            return

        self.manifest["downloaded_at"] = datetime.now(UTC).isoformat()
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved manifest to {self.manifest_path}")

    async def fetch_from_vitec(self, vitec_employee_id: str) -> bytes | None:
        """Fetch photo from Vitec Hub API."""
        if not self.installation_id:
            logger.debug("VITEC_INSTALLATION_ID not configured")
            return None

        if not self.vitec_service.is_configured:
            logger.debug("Vitec Hub credentials not configured")
            return None

        try:
            image_bytes = await self.vitec_service.get_employee_picture(self.installation_id, vitec_employee_id)
            if image_bytes:
                logger.debug(f"Got {len(image_bytes)} bytes from Vitec for {vitec_employee_id}")
            return image_bytes
        except Exception as e:
            logger.warning(f"Vitec fetch failed for {vitec_employee_id}: {e}")
            return None

    async def fetch_from_url(self, url: str) -> bytes | None:
        """Fetch photo from a URL (e.g., proaktiv.no)."""
        if not url:
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    if "image" in content_type:
                        logger.debug(f"Got {len(response.content)} bytes from URL")
                        return response.content
                    else:
                        logger.debug(f"URL returned non-image content-type: {content_type}")
                else:
                    logger.debug(f"URL returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"URL fetch failed for {url}: {e}")

        return None

    def get_image_info(self, image_bytes: bytes) -> dict[str, Any]:
        """Extract image metadata."""
        info = {"size_bytes": len(image_bytes)}

        try:
            from PIL import Image

            with Image.open(BytesIO(image_bytes)) as img:
                info["dimensions"] = f"{img.width}x{img.height}"
                info["format"] = img.format or "UNKNOWN"
        except ImportError:
            logger.debug("Pillow not installed, skipping image dimension extraction")
            info["dimensions"] = "unknown"
            info["format"] = "unknown"
        except Exception as e:
            logger.debug(f"Could not extract image info: {e}")
            info["dimensions"] = "unknown"
            info["format"] = "unknown"

        return info

    def save_photo(
        self,
        employee_id: str,
        image_bytes: bytes,
        source: str,
        employee_name: str,
        employee_email: str,
        office_name: str,
    ) -> str:
        """Save photo to disk and update manifest."""
        # Determine file extension from image content
        ext = "jpg"
        if image_bytes[:4] == b"\x89PNG":
            ext = "png"
        elif image_bytes[:2] == b"GI":
            ext = "gif"
        elif image_bytes[:4] == b"RIFF":
            ext = "webp"

        filename = f"{employee_id}.{ext}"
        filepath = self.photos_dir / filename

        if self.dry_run:
            logger.info(f"[DRY RUN] Would save: {filename}")
            return filename

        # Write image file
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        # Get image info
        image_info = self.get_image_info(image_bytes)

        # Update manifest
        self.manifest["photos"][employee_id] = {
            "filename": filename,
            "source": source,
            "employee_name": employee_name,
            "employee_email": employee_email or "",
            "office": office_name,
            "size_bytes": image_info["size_bytes"],
            "dimensions": image_info["dimensions"],
            "format": image_info.get("format", "unknown"),
            "downloaded_at": datetime.now(UTC).isoformat(),
        }

        logger.info(
            f"Saved: {filename} ({image_info['dimensions']}, {image_info['size_bytes']:,} bytes, source: {source})"
        )
        return filename

    async def download_employee_photo_from_data(self, data: dict[str, Any]) -> bool:
        """Download photo for a single employee from dict data."""
        employee_id = data["id"]
        employee_name = data["full_name"]
        employee_email = data.get("email")
        office_name = data.get("office_name", "Unknown")
        vitec_employee_id = data.get("vitec_employee_id")
        profile_image_url = data.get("profile_image_url")

        # Check if already downloaded (unless force)
        if not self.force:
            existing_entry = self.manifest.get("photos", {}).get(employee_id)
            if existing_entry:
                existing_file = self.photos_dir / existing_entry["filename"]
                if existing_file.exists():
                    logger.debug(f"Skipping {employee_name} - already downloaded")
                    self.stats["skipped_exists"] += 1
                    return True

        image_bytes: bytes | None = None
        source: str = ""

        # Try Vitec Hub first (unless skipped)
        if not self.skip_vitec and vitec_employee_id:
            image_bytes = await self.fetch_from_vitec(vitec_employee_id)
            if image_bytes:
                source = "vitec"
                self.stats["vitec_success"] += 1

        # Fall back to proaktiv.no URL
        if not image_bytes and profile_image_url:
            # Skip Vitec proxy URLs - those don't work outside the API
            if not profile_image_url.startswith("/api/vitec"):
                image_bytes = await self.fetch_from_url(profile_image_url)
                if image_bytes:
                    source = "proaktiv"
                    self.stats["proaktiv_success"] += 1

        if not image_bytes:
            logger.warning(f"No photo available for {employee_name}")
            self.stats["skipped_no_source"] += 1
            return False

        # Save the photo
        try:
            self.save_photo(
                employee_id,
                image_bytes,
                source,
                employee_name,
                employee_email or "",
                office_name,
            )
            self.stats["downloaded"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to save photo for {employee_name}: {e}")
            self.stats["failed"] += 1
            return False

    async def download_all(self, employee_id: str | None = None) -> None:
        """Download photos for all employees (or a specific one)."""
        self.setup_directories()
        self.load_manifest()

        async with self.session_factory() as session:
            # Build query - use raw SQL to avoid ORM model issues
            from sqlalchemy import text

            sql = """
                SELECT
                    e.id, e.first_name, e.last_name, e.email,
                    e.vitec_employee_id, e.profile_image_url,
                    o.name as office_name
                FROM employees e
                LEFT JOIN offices o ON e.office_id = o.id
                WHERE e.status = 'active' AND e.employee_type = 'internal'
            """
            if employee_id:
                sql += f" AND e.id = '{employee_id}'"

            result = await session.execute(text(sql))
            rows = result.fetchall()

            if not rows:
                logger.warning("No employees found matching criteria")
                return

            self.stats["total"] = len(rows)
            logger.info(f"Processing {len(rows)} employees...")

            for row in rows:
                # Convert row to dict for easier access
                employee_data = {
                    "id": str(row[0]),
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "vitec_employee_id": row[4],
                    "profile_image_url": row[5],
                    "office_name": row[6] or "Unknown",
                }
                employee_data["full_name"] = f"{employee_data['first_name']} {employee_data['last_name'] or ''}".strip()

                await self.download_employee_photo_from_data(employee_data)
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)

        # Save manifest
        self.save_manifest()

        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print download summary."""
        logger.info("-" * 50)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("-" * 50)
        logger.info(f"Total employees:       {self.stats['total']}")
        logger.info(f"Downloaded:            {self.stats['downloaded']}")
        logger.info(f"  - From Vitec:        {self.stats['vitec_success']}")
        logger.info(f"  - From proaktiv.no:  {self.stats['proaktiv_success']}")
        logger.info(f"Skipped (exists):      {self.stats['skipped_exists']}")
        logger.info(f"Skipped (no source):   {self.stats['skipped_no_source']}")
        logger.info(f"Failed:                {self.stats['failed']}")
        logger.info("-" * 50)
        if not self.dry_run:
            logger.info(f"Photos saved to: {self.photos_dir}")
            logger.info(f"Manifest: {self.manifest_path}")


async def main():
    parser = argparse.ArgumentParser(description="Download employee photos from Vitec Hub or proaktiv.no")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Database URL (default: uses DATABASE_URL env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if photo already exists",
    )
    parser.add_argument(
        "--employee-id",
        type=str,
        help="Download photo for a specific employee UUID",
    )
    parser.add_argument(
        "--skip-vitec",
        action="store_true",
        help="Skip Vitec Hub API, only use proaktiv.no URLs",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get database URL
    db_url = args.db_url or os.environ.get("DATABASE_URL") or settings.DATABASE_URL
    if not db_url:
        logger.error("No database URL provided. Use --db-url or set DATABASE_URL env var.")
        sys.exit(1)

    # Mask password in log output
    masked_url = db_url
    if "@" in db_url:
        parts = db_url.split("@")
        prefix = parts[0]
        if ":" in prefix:
            user_start = prefix.rfind("//") + 2
            colon = prefix.find(":", user_start)
            if colon != -1:
                masked_url = prefix[: colon + 1] + "***@" + parts[1]
    logger.info(f"Database: {masked_url}")

    if args.dry_run:
        logger.info("=" * 50)
        logger.info("DRY RUN MODE - No files will be written")
        logger.info("=" * 50)

    downloader = PhotoDownloader(
        output_dir=args.output_dir,
        db_url=db_url,
        dry_run=args.dry_run,
        force=args.force,
        skip_vitec=args.skip_vitec,
    )

    await downloader.download_all(employee_id=args.employee_id)


if __name__ == "__main__":
    asyncio.run(main())
