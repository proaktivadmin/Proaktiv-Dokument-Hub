#!/usr/bin/env python3
"""
Upload downloaded employee photos to proaktiv.no WebDAV.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import mimetypes
import sys
from pathlib import Path
from typing import Any

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import dotenv early to load environment before other imports
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from app.services.webdav_service import WebDAVService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_PHOTOS_DIR = Path.home() / "Documents" / "ProaktivPhotos"
DEFAULT_REMOTE_DIR = "/photos/employees"
DEFAULT_PUBLIC_BASE_URL = "https://proaktiv.no/d/photos/employees/"


def _normalize_remote_dir(remote_dir: str) -> str:
    clean = remote_dir.strip()
    if not clean.startswith("/"):
        clean = f"/{clean}"
    return clean.rstrip("/")


def _build_hosted_url(public_base_url: str, filename: str) -> str:
    return f"{public_base_url.rstrip('/')}/{filename}"


async def _ensure_remote_dir(webdav: WebDAVService, remote_dir: str, dry_run: bool) -> None:
    clean_dir = _normalize_remote_dir(remote_dir)
    parts = [part for part in clean_dir.split("/") if part]
    current = ""
    for part in parts:
        current = f"{current}/{part}"
        if await webdav.exists(current):
            continue
        if dry_run:
            logger.info("[DRY RUN] Would create directory: %s", current)
            continue
        await webdav.create_directory(current)
        logger.info("Created directory: %s", current)


async def upload_photos(
    photos_dir: Path,
    remote_dir: str,
    public_base_url: str,
    dry_run: bool,
    force: bool,
) -> None:
    manifest_path = photos_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path, encoding="utf-8") as f:
        manifest: dict[str, Any] = json.load(f)

    photos: dict[str, Any] = manifest.get("photos", {})
    if not photos:
        logger.warning("Manifest contains no photos to upload.")
        return

    webdav = WebDAVService()
    if not webdav.is_configured:
        raise RuntimeError("WebDAV is not configured. Set WEBDAV_* environment variables.")

    await _ensure_remote_dir(webdav, remote_dir, dry_run)

    uploaded = 0
    skipped_existing = 0
    missing_files = 0

    for employee_id, data in photos.items():
        filename = data.get("filename")
        if not filename:
            logger.warning("Missing filename for employee %s", employee_id)
            continue

        local_file = photos_dir / "photos" / filename
        if not local_file.exists():
            logger.warning("Missing local file: %s", local_file)
            missing_files += 1
            continue

        hosted_url = data.get("hosted_url")
        if hosted_url and not force:
            skipped_existing += 1
            continue

        remote_file = f"{_normalize_remote_dir(remote_dir)}/{filename}"
        content_type, _ = mimetypes.guess_type(filename)

        if dry_run:
            logger.info("[DRY RUN] Would upload %s -> %s", local_file, remote_file)
        else:
            content = local_file.read_bytes()
            await webdav.upload_file(remote_file, content, content_type)
            logger.info("Uploaded %s -> %s", local_file.name, remote_file)

        data["hosted_url"] = _build_hosted_url(public_base_url, filename)
        uploaded += 1

    if dry_run:
        logger.info("[DRY RUN] Skipping manifest update.")
        return

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info("Updated manifest with hosted URLs: %s", manifest_path)
    logger.info(
        "Upload summary - uploaded: %s, skipped: %s, missing: %s",
        uploaded,
        skipped_existing,
        missing_files,
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Upload employee photos to WebDAV.")
    parser.add_argument(
        "--photos-dir",
        type=Path,
        default=DEFAULT_PHOTOS_DIR,
        help=f"Photos directory (default: {DEFAULT_PHOTOS_DIR})",
    )
    parser.add_argument(
        "--remote-dir",
        type=str,
        default=DEFAULT_REMOTE_DIR,
        help=f"Remote WebDAV directory (default: {DEFAULT_REMOTE_DIR})",
    )
    parser.add_argument(
        "--public-base-url",
        type=str,
        default=DEFAULT_PUBLIC_BASE_URL,
        help=f"Public base URL for hosted photos (default: {DEFAULT_PUBLIC_BASE_URL})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without uploading",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-upload even if hosted_url already exists in manifest",
    )

    args = parser.parse_args()

    await upload_photos(
        photos_dir=args.photos_dir,
        remote_dir=args.remote_dir,
        public_base_url=args.public_base_url,
        dry_run=args.dry_run,
        force=args.force,
    )


if __name__ == "__main__":
    asyncio.run(main())
