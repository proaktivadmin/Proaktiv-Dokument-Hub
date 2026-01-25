#!/usr/bin/env python3
"""
Export employee photos from proaktiv.no into a local folder structure.

This script does NOT upload or modify WebDAV. It only creates local folders
and downloads image files so you can upload them manually.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import mimetypes
import shutil
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

# Import dotenv early to load environment before other imports
try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from app.config import settings
from scripts.sync_proaktiv_directory import (
    DEFAULT_START_URLS,
    classify_url,
    extract_links,
    fetch_html,
    normalize_url,
    parse_city_employees,
    parse_employee_page,
    parse_kjedeledelse_page,
    parse_office_page,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "webdav-upload"
DEFAULT_COLLECTION_ROOT = "photos/employees"
DEFAULT_PUBLIC_BASE_URL = "https://proaktiv.no/d"

INVALID_FILENAME_CHARS = '<>:"/\\|?*'


@dataclass
class EmployeeRecord:
    first_name: str
    last_name: str
    full_name: str
    title: str | None
    email: str | None
    homepage_profile_url: str | None
    profile_image_url: str | None
    office_url: str | None
    office_name: str | None
    office_slug: str | None
    source_pages: set[str] = field(default_factory=set)
    image_filename: str | None = None
    local_path: str | None = None
    collection_path: str | None = None
    public_url: str | None = None
    download_status: str | None = None
    download_bytes: int | None = None


def normalize_asset_url(url: str) -> str:
    parsed = urlparse(url)
    encoded_path = quote(unquote(parsed.path), safe="/")
    return parsed._replace(path=encoded_path).geturl()


def sanitize_filename(name: str) -> str:
    cleaned = "".join("_" if char in INVALID_FILENAME_CHARS else char for char in name)
    cleaned = cleaned.strip().strip(".")
    return cleaned or "image"


def derive_employee_slug(profile_url: str | None) -> str | None:
    if not profile_url:
        return None
    parsed = urlparse(profile_url)
    parts = unquote(parsed.path).strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "eiendomsmegler":
        return parts[2]
    return None


def derive_office_slug(profile_url: str | None, office_url: str | None) -> str:
    for url in (profile_url, office_url):
        if not url:
            continue
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        if path == "/om-oss/kjedeledelse":
            return "kjedeledelse"
        parts = unquote(path).strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "eiendomsmegler":
            return parts[1] or "ukjent"
    return "ukjent"


def derive_filename_from_email(email: str | None) -> str | None:
    """Derive filename from employee email.

    Target format: {email}.jpg
    Example: froyland@proaktiv.no -> froyland@proaktiv.no.jpg
    """
    if not email:
        return None
    # Sanitize email for filesystem (@ and . are allowed in filenames on most systems)
    sanitized = sanitize_filename(email.lower().strip())
    if not sanitized:
        return None
    return f"{sanitized}.jpg"


def derive_filename(profile_image_url: str | None, employee_slug: str | None) -> str | None:
    """Legacy filename derivation - kept for backwards compatibility."""
    if profile_image_url:
        filename = unquote(Path(urlparse(profile_image_url).path).name)
        if filename:
            return sanitize_filename(filename)
    if employee_slug:
        return sanitize_filename(f"{employee_slug}.jpg")
    return None


def ensure_extension(filename: str, content_type: str | None) -> str:
    suffix = Path(filename).suffix
    if suffix:
        return filename
    guessed = mimetypes.guess_extension(content_type or "") or ".jpg"
    return f"{filename}{guessed}"


def record_key(record: EmployeeRecord) -> str:
    if record.homepage_profile_url:
        return record.homepage_profile_url
    if record.email:
        return record.email.lower()
    return f"{record.full_name}::{record.office_slug or ''}".lower()


def upsert_record(
    records: dict[str, EmployeeRecord],
    payload: Any,
    *,
    source_url: str,
) -> EmployeeRecord:
    first_name = payload.first_name or ""
    last_name = payload.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    record = EmployeeRecord(
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        title=getattr(payload, "title", None),
        email=getattr(payload, "email", None),
        homepage_profile_url=getattr(payload, "homepage_profile_url", None),
        profile_image_url=getattr(payload, "profile_image_url", None),
        office_url=getattr(payload, "office_url", None),
        office_name=getattr(payload, "office_name", None),
        office_slug=None,
    )

    key = record_key(record)
    existing = records.get(key)
    if existing:
        existing.title = existing.title or record.title
        existing.email = existing.email or record.email
        existing.homepage_profile_url = existing.homepage_profile_url or record.homepage_profile_url
        existing.profile_image_url = existing.profile_image_url or record.profile_image_url
        existing.office_url = existing.office_url or record.office_url
        existing.office_name = existing.office_name or record.office_name
        existing.first_name = existing.first_name or record.first_name
        existing.last_name = existing.last_name or record.last_name
        existing.full_name = existing.full_name or record.full_name
        existing.source_pages.add(source_url)
        existing.office_slug = existing.office_slug or derive_office_slug(
            existing.homepage_profile_url, existing.office_url
        )
        return existing

    record.source_pages.add(source_url)
    record.office_slug = derive_office_slug(record.homepage_profile_url, record.office_url)
    records[key] = record
    return record


async def crawl_directory(
    *,
    start_urls: list[str],
    delay_ms: int,
    max_pages: int,
    max_runtime_minutes: int,
    max_office_pages: int,
    max_employee_pages: int,
    use_firecrawl: bool,
    deep_employees: bool,
) -> dict[str, EmployeeRecord]:
    queue = [normalize_url(url) for url in start_urls]
    visited: set[str] = set()
    records: dict[str, EmployeeRecord] = {}
    processed_offices = 0
    processed_employees = 0
    total_processed = 0
    start_time = time.monotonic()
    delay_seconds = max(0, delay_ms / 1000)

    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0"},
        follow_redirects=True,
        timeout=30,
    ) as client:
        while queue and total_processed < max_pages:
            if (time.monotonic() - start_time) > (max_runtime_minutes * 60):
                logger.info("Max runtime reached, stopping crawl.")
                break

            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            if processed_offices >= max_office_pages and processed_employees >= max_employee_pages:
                break

            if delay_seconds:
                await asyncio.sleep(delay_seconds)

            try:
                html = await fetch_html(
                    client, url, use_firecrawl=use_firecrawl, timeout_ms=settings.FIRECRAWL_TIMEOUT_MS
                )
            except Exception as exc:
                logger.warning("Failed to fetch %s: %s", url, exc)
                continue

            total_processed += 1
            soup = BeautifulSoup(html, "lxml")
            page_type = classify_url(url)

            for link in extract_links(soup, url):
                if deep_employees and classify_url(link) != "employee":
                    continue
                if link not in visited and link not in queue:
                    queue.append(link)

            if page_type == "kjedledelse" and processed_offices < max_office_pages:
                _, employee_payloads = parse_kjedeledelse_page(soup, url)
                processed_offices += 1
                for payload in employee_payloads:
                    if processed_employees >= max_employee_pages:
                        break
                    upsert_record(records, payload, source_url=url)
                    processed_employees += 1

            if page_type == "office" and processed_offices < max_office_pages:
                _, employee_payloads = parse_office_page(soup, url)
                processed_offices += 1
                for payload in employee_payloads:
                    if payload.homepage_profile_url and payload.homepage_profile_url not in visited:
                        if payload.homepage_profile_url not in queue:
                            queue.append(payload.homepage_profile_url)
                    if deep_employees:
                        continue
                    if processed_employees >= max_employee_pages:
                        break
                    upsert_record(records, payload, source_url=url)
                    processed_employees += 1

            if page_type == "employee" and processed_employees < max_employee_pages:
                payload, _ = parse_employee_page(soup, url)
                upsert_record(records, payload, source_url=url)
                processed_employees += 1

            if page_type == "city":
                employee_payloads = parse_city_employees(soup, url)
                for payload in employee_payloads:
                    if processed_employees >= max_employee_pages:
                        break
                    if payload.homepage_profile_url and payload.homepage_profile_url not in visited:
                        if payload.homepage_profile_url not in queue:
                            queue.append(payload.homepage_profile_url)
                    if deep_employees:
                        continue
                    upsert_record(records, payload, source_url=url)
                    processed_employees += 1

    logger.info(
        "Crawl complete. processed_pages=%s offices=%s employees=%s",
        total_processed,
        processed_offices,
        processed_employees,
    )
    return records


async def export_photos(
    *,
    output_dir: Path,
    collection_root: str,
    public_base_url: str,
    download_delay_ms: int,
    dry_run: bool,
    force: bool,
    records: dict[str, EmployeeRecord],
) -> dict[str, Any]:
    """Export employee photos to local folder structure.

    Target structure: {output_dir}/{collection_root}/{email}.jpg
    Example: ~/ProaktivPhotos/webdav-upload/photos/employees/froyland@proaktiv.no.jpg

    This matches the WebDAV target: proaktiv.no/d/photos/employees/{email}.jpg
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    collection_root = collection_root.strip("/").strip()
    public_base_url = public_base_url.rstrip("/")
    download_delay = max(0, download_delay_ms / 1000)

    download_cache: dict[str, Path] = {}
    missing_images: list[EmployeeRecord] = []
    skipped_external: list[EmployeeRecord] = []

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        for record in records.values():
            # Skip employees without proaktiv.no email (external users)
            if record.email and not record.email.lower().endswith("@proaktiv.no"):
                record.download_status = "skipped_external_email"
                skipped_external.append(record)
                continue

            # Use email-based filename (new architecture)
            filename = derive_filename_from_email(record.email)
            if not filename:
                record.download_status = "missing_email"
                missing_images.append(record)
                continue

            record.image_filename = filename
            # Flat structure: photos/employees/{email}.jpg (no office subfolders)
            collection_path = f"{collection_root}/{filename}"
            local_path = output_dir / collection_root / filename
            record.collection_path = collection_path
            record.local_path = str(local_path)
            record.public_url = f"{public_base_url}/{collection_path}"

            if not record.profile_image_url:
                record.download_status = "missing_image_url"
                missing_images.append(record)
                continue

            normalized_url = normalize_asset_url(record.profile_image_url)
            if normalized_url in download_cache:
                source_path = download_cache[normalized_url]
                if dry_run:
                    record.download_status = "dry-run-copy"
                else:
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    if source_path != local_path:
                        shutil.copy2(source_path, local_path)
                    record.download_status = "copied"
                    record.download_bytes = local_path.stat().st_size
                continue

            if local_path.exists() and not force:
                record.download_status = "skipped_exists"
                record.download_bytes = local_path.stat().st_size
                download_cache[normalized_url] = local_path
                continue

            if dry_run:
                record.download_status = "dry-run"
                continue

            try:
                if download_delay:
                    await asyncio.sleep(download_delay)
                response = await client.get(normalized_url)
                response.raise_for_status()
                # Keep .jpg extension regardless of actual content type for consistency
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(response.content)
                record.download_status = "downloaded"
                record.download_bytes = len(response.content)
                download_cache[normalized_url] = local_path
            except Exception as exc:
                record.download_status = f"failed: {exc}"
                missing_images.append(record)

    return {
        "missing_images_count": len(missing_images),
        "skipped_external_count": len(skipped_external),
        "downloaded": sum(1 for record in records.values() if record.download_status == "downloaded"),
        "copied": sum(1 for record in records.values() if record.download_status == "copied"),
        "skipped": sum(1 for record in records.values() if record.download_status == "skipped_exists"),
    }


def write_outputs(
    *,
    output_dir: Path,
    collection_root: str,
    public_base_url: str,
    records: dict[str, EmployeeRecord],
    summary: dict[str, Any],
) -> None:
    manifest = {
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "collection_root": collection_root,
        "public_base_url": public_base_url,
        "employees": [],
    }

    for record in sorted(records.values(), key=lambda r: (r.office_slug or "", r.full_name)):
        manifest["employees"].append(
            {
                "full_name": record.full_name,
                "title": record.title,
                "email": record.email,
                "homepage_profile_url": record.homepage_profile_url,
                "profile_image_url": record.profile_image_url,
                "office_name": record.office_name,
                "office_url": record.office_url,
                "office_slug": record.office_slug,
                "image_filename": record.image_filename,
                "collection_path": record.collection_path,
                "public_url": record.public_url,
                "local_path": record.local_path,
                "download_status": record.download_status,
                "download_bytes": record.download_bytes,
                "source_pages": sorted(record.source_pages),
            }
        )

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    csv_path = output_dir / "employee_photo_map.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "full_name",
                "email",
                "homepage_profile_url",
                "profile_image_url",
                "office_slug",
                "image_filename",
                "collection_path",
                "public_url",
                "download_status",
                "download_bytes",
            ],
        )
        writer.writeheader()
        for record in manifest["employees"]:
            writer.writerow({key: record.get(key) for key in writer.fieldnames})

    missing_path = output_dir / "missing_images.txt"
    with open(missing_path, "w", encoding="utf-8") as f:
        for record in manifest["employees"]:
            if record.get("download_status") in ("missing_image_url", "missing_filename"):
                f.write(f"{record.get('full_name')} | {record.get('homepage_profile_url')}\n")

    summary_path = output_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info("Wrote manifest: %s", manifest_path)
    logger.info("Wrote CSV map: %s", csv_path)
    logger.info("Wrote missing list: %s", missing_path)
    logger.info("Wrote summary: %s", summary_path)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export employee photos into a local folder structure (no WebDAV writes)."
    )
    parser.add_argument("--start", action="append", default=None, help="Start URL (repeatable)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument(
        "--collection-root",
        type=str,
        default=DEFAULT_COLLECTION_ROOT,
        help="Top-level collection folder (e.g. eiendomsmegler)",
    )
    parser.add_argument(
        "--public-base-url",
        type=str,
        default=DEFAULT_PUBLIC_BASE_URL,
        help="Base public URL for building final links",
    )
    parser.add_argument("--delay-ms", type=int, default=1500, help="Delay between page requests (ms)")
    parser.add_argument("--download-delay-ms", type=int, default=200, help="Delay between image downloads (ms)")
    parser.add_argument("--max-pages", type=int, default=180, help="Max pages to process")
    parser.add_argument("--max-runtime-minutes", type=int, default=60, help="Max runtime minutes")
    parser.add_argument("--max-office-pages", type=int, default=80, help="Max office pages")
    parser.add_argument("--max-employee-pages", type=int, default=400, help="Max employee pages")
    parser.add_argument("--use-firecrawl", action="store_true", help="Use Firecrawl for fetching HTML")
    parser.add_argument("--deep-employees", action="store_true", help="Parse employee profile pages")
    parser.add_argument("--dry-run", action="store_true", help="Do not download images")
    parser.add_argument("--force", action="store_true", help="Re-download even if file exists")
    args = parser.parse_args()

    start_urls = [normalize_url(url) for url in (args.start or DEFAULT_START_URLS)]
    logger.info("Starting crawl with %s start URLs", len(start_urls))

    records = await crawl_directory(
        start_urls=start_urls,
        delay_ms=args.delay_ms,
        max_pages=args.max_pages,
        max_runtime_minutes=args.max_runtime_minutes,
        max_office_pages=args.max_office_pages,
        max_employee_pages=args.max_employee_pages,
        use_firecrawl=args.use_firecrawl,
        deep_employees=args.deep_employees,
    )

    summary = await export_photos(
        output_dir=args.output_dir,
        collection_root=args.collection_root,
        public_base_url=args.public_base_url,
        download_delay_ms=args.download_delay_ms,
        dry_run=args.dry_run,
        force=args.force,
        records=records,
    )
    summary["total_records"] = len(records)
    summary["output_dir"] = str(args.output_dir)
    summary["collection_root"] = args.collection_root
    summary["public_base_url"] = args.public_base_url

    write_outputs(
        output_dir=args.output_dir,
        collection_root=args.collection_root,
        public_base_url=args.public_base_url,
        records=records,
        summary=summary,
    )


if __name__ == "__main__":
    asyncio.run(main())
