#!/usr/bin/env python3
"""
Export office banner images from proaktiv.no into a local folder structure.

This script crawls office pages and downloads their banner images.
Target structure: photos/offices/{office_slug}.jpg

Office page structure on proaktiv.no:
- City/Area pages: /eiendomsmegler/{city} (e.g., /drammen-lier)
- Office pages: /eiendomsmegler/{city}/{office-name} (e.g., /drammen-lier/proaktiv-drammen-lier-holmestrand)

Some cities like Trondheim, Bergen, Sarpsborg have multiple offices under one city page.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from app.config import settings
from scripts.sync_proaktiv_directory import (
    extract_links,
    fetch_html,
    normalize_url,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "webdav-upload"
DEFAULT_COLLECTION_ROOT = "photos/offices"
DEFAULT_PUBLIC_BASE_URL = "https://proaktiv.no/d"

# Office area pages - these are the city/region landing pages
OFFICE_AREA_URLS = [
    "https://proaktiv.no/eiendomsmegler/oslo",
    "https://proaktiv.no/eiendomsmegler/drammen-lier",
    "https://proaktiv.no/eiendomsmegler/lillestrøm",
    "https://proaktiv.no/eiendomsmegler/lørenskog",
    "https://proaktiv.no/eiendomsmegler/bergen",
    "https://proaktiv.no/eiendomsmegler/voss",
    "https://proaktiv.no/eiendomsmegler/stavanger",
    "https://proaktiv.no/eiendomsmegler/sandnes",
    "https://proaktiv.no/eiendomsmegler/sola",
    "https://proaktiv.no/eiendomsmegler/trondheim",
    "https://proaktiv.no/eiendomsmegler/ålesund",
    "https://proaktiv.no/eiendomsmegler/skien",
    "https://proaktiv.no/eiendomsmegler/haugesund",
    "https://proaktiv.no/eiendomsmegler/sarpsborg",
    "https://proaktiv.no/eiendomsmegler/jæren",
    "https://proaktiv.no/eiendomsmegler/kristiansand",
]

INVALID_FILENAME_CHARS = '<>:"/\\|?*'


@dataclass
class OfficeRecord:
    name: str
    homepage_url: str | None
    city_slug: str | None
    office_slug: str | None
    banner_image_url: str | None
    email: str | None
    phone: str | None
    address: str | None
    source_pages: set[str] = field(default_factory=set)
    image_filename: str | None = None
    local_path: str | None = None
    collection_path: str | None = None
    public_url: str | None = None
    download_status: str | None = None
    download_bytes: int | None = None


def sanitize_filename(name: str) -> str:
    cleaned = "".join("_" if char in INVALID_FILENAME_CHARS else char for char in name)
    cleaned = cleaned.strip().strip(".")
    return cleaned or "image"


def derive_office_slug(url: str | None) -> str | None:
    """Extract office slug from URL like /eiendomsmegler/drammen-lier/proaktiv-drammen-lier-holmestrand."""
    if not url:
        return None
    parsed = urlparse(url)
    parts = unquote(parsed.path).strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "eiendomsmegler":
        return parts[2]  # e.g., "proaktiv-drammen-lier-holmestrand"
    if len(parts) >= 2 and parts[0] == "eiendomsmegler":
        return parts[1]  # e.g., "drammen-lier" for city-level pages
    return None


def derive_city_slug(url: str | None) -> str | None:
    """Extract city slug from URL."""
    if not url:
        return None
    parsed = urlparse(url)
    parts = unquote(parsed.path).strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "eiendomsmegler":
        return parts[1]
    return None


def normalize_asset_url(url: str) -> str:
    parsed = urlparse(url)
    encoded_path = quote(unquote(parsed.path), safe="/")
    return parsed._replace(path=encoded_path).geturl()


def is_office_page(url: str) -> bool:
    """Check if URL is an office profile page (exactly 3 path segments, starts with 'proaktiv-').

    Office pages: /eiendomsmegler/{city}/proaktiv-{office-name}
    Employee pages: /eiendomsmegler/{city}/{office-name}/{employee-slug}
    """
    parsed = urlparse(url)
    parts = unquote(parsed.path).strip("/").split("/")
    # /eiendomsmegler/{city}/{office-name} = 3 parts
    # Office slugs typically start with "proaktiv-"
    if len(parts) == 3 and parts[0] == "eiendomsmegler":
        office_slug = parts[2].lower()
        # Office pages have slugs starting with "proaktiv-"
        return office_slug.startswith("proaktiv-")
    return False


def is_city_page(url: str) -> bool:
    """Check if URL is a city/area page (2 path segments)."""
    parsed = urlparse(url)
    parts = unquote(parsed.path).strip("/").split("/")
    # /eiendomsmegler/{city} = 2 parts
    return len(parts) == 2 and parts[0] == "eiendomsmegler"


def extract_banner_image_url(soup: BeautifulSoup) -> str | None:
    """Extract banner image from og:image meta tag."""
    og_image = soup.find("meta", property="og:image")
    if og_image:
        content = og_image.get("content", "")
        if content and not any(skip in content.lower() for skip in ("logo", "favicon", "icon", "placeholder")):
            # Strip query params for cleaner URL
            parsed = urlparse(content)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return None


def extract_office_name(soup: BeautifulSoup) -> str | None:
    """Extract office name from page."""
    # Try og:title first
    og_title = soup.find("meta", property="og:title")
    if og_title:
        title = og_title.get("content", "")
        if title:
            # Clean up title (remove " | Proaktiv Eiendomsmegling" suffix if present)
            if "|" in title:
                title = title.split("|")[0].strip()
            return title

    # Fallback to h1
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return None


def extract_office_contact(soup: BeautifulSoup) -> dict[str, str | None]:
    """Extract contact info from office page."""
    result = {"email": None, "phone": None, "address": None}

    # Look for email
    email_link = soup.find("a", href=lambda x: x and x.startswith("mailto:"))
    if email_link:
        result["email"] = email_link.get("href", "").replace("mailto:", "").split("?")[0]

    # Look for phone
    tel_link = soup.find("a", href=lambda x: x and x.startswith("tel:"))
    if tel_link:
        result["phone"] = tel_link.get("href", "").replace("tel:", "").replace(" ", "")

    return result


async def crawl_offices(
    *,
    start_urls: list[str],
    delay_ms: int,
    max_pages: int,
    use_firecrawl: bool,
) -> dict[str, OfficeRecord]:
    """Crawl office pages and extract banner images."""
    queue = [normalize_url(url) for url in start_urls]
    visited: set[str] = set()
    records: dict[str, OfficeRecord] = {}
    processed = 0
    delay_seconds = max(0, delay_ms / 1000)

    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0"},
        follow_redirects=True,
        timeout=30,
    ) as client:
        while queue and processed < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            if delay_seconds:
                await asyncio.sleep(delay_seconds)

            try:
                html = await fetch_html(
                    client, url, use_firecrawl=use_firecrawl, timeout_ms=settings.FIRECRAWL_TIMEOUT_MS
                )
            except Exception as exc:
                logger.warning("Failed to fetch %s: %s", url, exc)
                continue

            processed += 1
            soup = BeautifulSoup(html, "lxml")

            # Extract links to office pages
            for link in extract_links(soup, url):
                if link not in visited and link not in queue:
                    if is_office_page(link) or is_city_page(link):
                        queue.append(link)

            # Only process office pages (not city pages) for banners
            if is_office_page(url):
                name = extract_office_name(soup)
                banner_url = extract_banner_image_url(soup)
                contact = extract_office_contact(soup)
                office_slug = derive_office_slug(url)
                city_slug = derive_city_slug(url)

                if name and office_slug:
                    key = url
                    if key not in records:
                        records[key] = OfficeRecord(
                            name=name,
                            homepage_url=url,
                            city_slug=city_slug,
                            office_slug=office_slug,
                            banner_image_url=banner_url,
                            email=contact.get("email"),
                            phone=contact.get("phone"),
                            address=contact.get("address"),
                        )
                    records[key].source_pages.add(url)
                    logger.info("Found office: %s -> %s", name, banner_url or "NO BANNER")

    logger.info("Crawl complete. processed_pages=%s offices=%s", processed, len(records))
    return records


async def export_banners(
    *,
    output_dir: Path,
    collection_root: str,
    public_base_url: str,
    download_delay_ms: int,
    dry_run: bool,
    force: bool,
    records: dict[str, OfficeRecord],
) -> dict[str, Any]:
    """Export office banner images to local folder structure."""
    output_dir.mkdir(parents=True, exist_ok=True)
    collection_root = collection_root.strip("/").strip()
    public_base_url = public_base_url.rstrip("/")
    download_delay = max(0, download_delay_ms / 1000)

    missing_images: list[OfficeRecord] = []

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        for record in records.values():
            # Use office slug for filename
            if not record.office_slug:
                record.download_status = "missing_slug"
                missing_images.append(record)
                continue

            filename = f"{sanitize_filename(record.office_slug)}.jpg"
            record.image_filename = filename
            collection_path = f"{collection_root}/{filename}"
            local_path = output_dir / collection_root / filename
            record.collection_path = collection_path
            record.local_path = str(local_path)
            record.public_url = f"{public_base_url}/{collection_path}"

            if not record.banner_image_url:
                record.download_status = "missing_image_url"
                missing_images.append(record)
                continue

            normalized_url = normalize_asset_url(record.banner_image_url)

            if local_path.exists() and not force:
                record.download_status = "skipped_exists"
                record.download_bytes = local_path.stat().st_size
                continue

            if dry_run:
                record.download_status = "dry-run"
                continue

            try:
                if download_delay:
                    await asyncio.sleep(download_delay)
                response = await client.get(normalized_url)
                response.raise_for_status()
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(response.content)
                record.download_status = "downloaded"
                record.download_bytes = len(response.content)
            except Exception as exc:
                record.download_status = f"failed: {exc}"
                missing_images.append(record)

    return {
        "missing_images_count": len(missing_images),
        "downloaded": sum(1 for r in records.values() if r.download_status == "downloaded"),
        "skipped": sum(1 for r in records.values() if r.download_status == "skipped_exists"),
    }


def write_outputs(
    *,
    output_dir: Path,
    collection_root: str,
    public_base_url: str,
    records: dict[str, OfficeRecord],
    summary: dict[str, Any],
) -> None:
    """Write manifest and CSV files."""
    manifest = {
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "collection_root": collection_root,
        "public_base_url": public_base_url,
        "offices": [],
    }

    for record in sorted(records.values(), key=lambda r: r.name or ""):
        manifest["offices"].append(
            {
                "name": record.name,
                "homepage_url": record.homepage_url,
                "city_slug": record.city_slug,
                "office_slug": record.office_slug,
                "banner_image_url": record.banner_image_url,
                "email": record.email,
                "phone": record.phone,
                "image_filename": record.image_filename,
                "collection_path": record.collection_path,
                "public_url": record.public_url,
                "local_path": record.local_path,
                "download_status": record.download_status,
                "download_bytes": record.download_bytes,
                "source_pages": sorted(record.source_pages),
            }
        )

    manifest_path = output_dir / "office_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    csv_path = output_dir / "office_banner_map.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "homepage_url",
                "office_slug",
                "banner_image_url",
                "image_filename",
                "collection_path",
                "public_url",
                "download_status",
            ],
        )
        writer.writeheader()
        for record in manifest["offices"]:
            writer.writerow({key: record.get(key) for key in writer.fieldnames})

    missing_path = output_dir / "missing_office_banners.txt"
    with open(missing_path, "w", encoding="utf-8") as f:
        for record in manifest["offices"]:
            if record.get("download_status") in ("missing_image_url", "missing_slug"):
                f.write(f"{record.get('name')} | {record.get('homepage_url')}\n")

    summary_path = output_dir / "office_summary.json"
    summary["total_records"] = len(records)
    summary["output_dir"] = str(output_dir)
    summary["collection_root"] = collection_root
    summary["public_base_url"] = public_base_url
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info("Wrote manifest: %s", manifest_path)
    logger.info("Wrote CSV map: %s", csv_path)
    logger.info("Wrote missing list: %s", missing_path)
    logger.info("Wrote summary: %s", summary_path)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Export office banner images from proaktiv.no")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--collection-root",
        default=DEFAULT_COLLECTION_ROOT,
        help=f"Collection root path (default: {DEFAULT_COLLECTION_ROOT})",
    )
    parser.add_argument(
        "--public-base-url",
        default=DEFAULT_PUBLIC_BASE_URL,
        help=f"Public base URL (default: {DEFAULT_PUBLIC_BASE_URL})",
    )
    parser.add_argument(
        "--delay-ms",
        type=int,
        default=2000,
        help="Delay between requests in ms (default: 2000)",
    )
    parser.add_argument(
        "--download-delay-ms",
        type=int,
        default=500,
        help="Delay between downloads in ms (default: 500)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Max pages to crawl (default: 100)",
    )
    parser.add_argument(
        "--use-firecrawl",
        action="store_true",
        help="Use Firecrawl for fetching HTML",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't download images, just crawl and report",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download existing images",
    )

    args = parser.parse_args()

    logger.info("Starting office banner crawl with %d start URLs", len(OFFICE_AREA_URLS))

    records = await crawl_offices(
        start_urls=OFFICE_AREA_URLS,
        delay_ms=args.delay_ms,
        max_pages=args.max_pages,
        use_firecrawl=args.use_firecrawl,
    )

    summary = await export_banners(
        output_dir=args.output_dir,
        collection_root=args.collection_root,
        public_base_url=args.public_base_url,
        download_delay_ms=args.download_delay_ms,
        dry_run=args.dry_run,
        force=args.force,
        records=records,
    )

    write_outputs(
        output_dir=args.output_dir,
        collection_root=args.collection_root,
        public_base_url=args.public_base_url,
        records=records,
        summary=summary,
    )


if __name__ == "__main__":
    asyncio.run(main())
