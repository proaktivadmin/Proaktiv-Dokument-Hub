#!/usr/bin/env python3
"""
Import Vitec Next templates (exported as JSON) into Proaktiv Dokument Hub.

This script is designed to pair with a Chrome/MCP-based scraping workflow that
exports all Vitec Next document templates into a single JSON file.

Usage (local):
  python backend/scripts/import_vitec_next_export.py --input data/vitec-next-export.json --match-title --update-existing

Usage (docker backend container):
  python /app/scripts/import_vitec_next_export.py --input /app/data/vitec-next-export.json --match-title --update-existing
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

# -----------------------------------------------------------------------------
# Import path bootstrap (works in local + /app container)
# -----------------------------------------------------------------------------

THIS_FILE = Path(__file__).resolve()
BACKEND_DIR = THIS_FILE.parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    # When running in Docker, legacy scripts used: sys.path.insert(0, "/app")
    # but we support both.
    from app.database import async_session_factory
    from app.models.category import Category
    from app.models.tag import Tag
    from app.models.template import Template
    from app.services.sanitizer_service import get_sanitizer_service
    from app.services.template_analyzer_service import TemplateAnalyzerService
    from app.services.template_content_service import TemplateContentService
    from app.services.template_service import TemplateService
    from app.services.template_settings_service import TemplateSettingsService
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Failed to import backend modules. Run from repo root, or inside /app in the backend container."
    ) from e


logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _normalize_title(value: str) -> str:
    return " ".join((value or "").strip().split()).lower()


ORIGIN_TAG_VITEC = "Vitec Next"
ORIGIN_TAG_KUNDEMAL = "Kundemal"
ATTACHMENT_NAME_KEYS = (
    "name",
    "fileName",
    "filename",
    "title",
    "documentName",
    "attachmentName",
    "templateName",
)
ATTACHMENT_ID_KEYS = (
    "id",
    "attachmentId",
    "documentId",
    "templateId",
    "attachmentTemplateId",
)


def _is_vitec_origin_tag(value: str) -> bool:
    lowered = (value or "").strip().lower()
    return "vitec" in lowered or lowered == "systemmal"


def _is_kundemal_origin_tag(value: str) -> bool:
    lowered = (value or "").strip().lower()
    return "kundemal" in lowered


def _extract_is_system(item: dict[str, Any], metadata: dict[str, Any]) -> bool | None:
    sources = [
        metadata.get("vitec_details"),
        metadata.get("vitec_raw"),
        metadata,
    ]
    for source in sources:
        if not isinstance(source, dict):
            continue
        is_system = source.get("isSystem")
        if isinstance(is_system, bool):
            return is_system
        system_type = source.get("systemTemplateType")
        if isinstance(system_type, int) and system_type > 0:
            return True

    template_type = (item.get("template_type") or "").strip().lower()
    if template_type == "system":
        return True
    if template_type:
        return False

    return None


def _resolve_origin_tag(
    tag_names: list[str],
    item: dict[str, Any],
    metadata: dict[str, Any],
) -> tuple[str | None, str | None]:
    for tag in tag_names:
        if _is_kundemal_origin_tag(tag):
            return tag, "tags"
    for tag in tag_names:
        if _is_vitec_origin_tag(tag):
            return tag, "tags"

    sources = [
        metadata.get("vitec_details"),
        metadata.get("vitec_raw"),
        metadata,
        item,
    ]
    for source in sources:
        if not isinstance(source, dict):
            continue
        for key in ("isVitecTemplate", "isVitec"):
            value = source.get(key)
            if isinstance(value, bool):
                return (ORIGIN_TAG_VITEC if value else ORIGIN_TAG_KUNDEMAL), "metadata"

    is_system = _extract_is_system(item, metadata)
    if is_system is True:
        return ORIGIN_TAG_VITEC, "metadata"
    if is_system is False:
        return ORIGIN_TAG_KUNDEMAL, "metadata"

    return None, None


def _apply_origin_tag(tag_names: list[str], origin_tag: str | None) -> list[str]:
    if not origin_tag:
        return _norm_str_list(tag_names)

    origin_is_vitec = _is_vitec_origin_tag(origin_tag)
    origin_is_kundemal = _is_kundemal_origin_tag(origin_tag)

    cleaned: list[str] = []
    for tag in _norm_str_list(tag_names):
        if origin_is_vitec and _is_kundemal_origin_tag(tag):
            continue
        if origin_is_kundemal and _is_vitec_origin_tag(tag):
            continue
        cleaned.append(tag)

    if not any(tag.lower() == origin_tag.lower() for tag in cleaned):
        cleaned.append(origin_tag)

    return _norm_str_list(cleaned)


def _normalize_attachment_name(value: Any) -> str | None:
    if value is None:
        return None
    name = str(value).strip()
    return name or None


def _looks_like_attachment_key(key: str) -> bool:
    lowered = key.lower()
    return "attachment" in lowered or "vedlegg" in lowered


def _normalize_attachment_entry(entry: Any, source: str) -> dict[str, Any] | None:
    if isinstance(entry, str):
        name = _normalize_attachment_name(entry)
        if not name:
            return None
        return {"name": name, "source": source}
    if not isinstance(entry, dict):
        return None

    name = None
    for key in ATTACHMENT_NAME_KEYS:
        if key in entry and entry[key]:
            name = _normalize_attachment_name(entry[key])
            if name:
                break

    if not name:
        return None

    attachment: dict[str, Any] = {"name": name, "source": source}
    for key in ATTACHMENT_ID_KEYS:
        if key in entry and entry[key] is not None:
            attachment["id"] = str(entry[key])
            break

    return attachment


def _extract_attachment_entries(entries: Any, source: str) -> list[dict[str, Any]]:
    if entries is None:
        return []
    if not isinstance(entries, list):
        entries = [entries]
    extracted: list[dict[str, Any]] = []
    for entry in entries:
        normalized = _normalize_attachment_entry(entry, source)
        if normalized:
            extracted.append(normalized)
    return extracted


def _find_attachment_candidates(
    source: dict[str, Any],
    *,
    source_name: str,
    depth: int = 0,
    max_depth: int = 2,
) -> list[tuple[str, Any]]:
    if depth > max_depth:
        return []

    candidates: list[tuple[str, Any]] = []
    for key, value in source.items():
        if _looks_like_attachment_key(key):
            candidates.append((f"{source_name}.{key}", value))
        if isinstance(value, dict):
            candidates.extend(
                _find_attachment_candidates(
                    value,
                    source_name=f"{source_name}.{key}",
                    depth=depth + 1,
                    max_depth=max_depth,
                )
            )
    return candidates


def _dedupe_attachments(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for entry in entries:
        name = _normalize_attachment_name(entry.get("name"))
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append({**entry, "name": name})
    return deduped


def _extract_vitec_attachments(
    item: dict[str, Any],
    metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    if isinstance(metadata.get("vitec_attachments"), list):
        return _dedupe_attachments(metadata.get("vitec_attachments", []))

    attachments: list[dict[str, Any]] = []

    if isinstance(item.get("attachments"), list):
        attachments.extend(_extract_attachment_entries(item.get("attachments"), "item.attachments"))

    sources: list[tuple[str, Any]] = [
        ("metadata.vitec_details", metadata.get("vitec_details")),
        ("metadata.vitec_raw", metadata.get("vitec_raw")),
        ("metadata", metadata),
    ]
    for source_name, source in sources:
        if not isinstance(source, dict):
            continue
        for key_path, value in _find_attachment_candidates(source, source_name=source_name):
            attachments.extend(_extract_attachment_entries(value, key_path))

    return _dedupe_attachments(attachments)


def _as_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _norm_str_list(values: Any) -> list[str]:
    if not values:
        return []
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for v in values:
        if v is None:
            continue
        s = str(v).strip()
        if not s:
            continue
        out.append(s)
    # preserve order but dedupe
    seen: set[str] = set()
    uniq: list[str] = []
    for s in out:
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(s)
    return uniq


async def _get_or_create_tag(session, name: str, *, color: str = "#3B82F6") -> Tag:
    # Case-insensitive lookup (best effort)
    res = await session.execute(select(Tag).where(Tag.name.ilike(name)))
    tag = res.scalar_one_or_none()
    if tag:
        return tag

    tag = Tag(name=name, color=color)
    session.add(tag)
    try:
        async with session.begin_nested():
            await session.flush()
        await session.refresh(tag)
        return tag
    except IntegrityError:
        # Someone else created it (or casing mismatch) - fetch it
        res2 = await session.execute(select(Tag).where(Tag.name.ilike(name)))
        tag2 = res2.scalar_one_or_none()
        if tag2:
            return tag2
        raise


async def _get_category_by_vitec_id(session, vitec_id: int) -> Category | None:
    res = await session.execute(select(Category).where(Category.vitec_id == vitec_id))
    return res.scalar_one_or_none()


async def _get_or_create_category(session, *, name: str | None, vitec_id: int | None) -> Category | None:
    if vitec_id is not None:
        existing = await _get_category_by_vitec_id(session, vitec_id)
        if existing:
            return existing

    if name:
        res = await session.execute(select(Category).where(Category.name == name))
        existing_by_name = res.scalar_one_or_none()
        if existing_by_name:
            # Backfill vitec_id if we have it
            if vitec_id is not None and existing_by_name.vitec_id is None:
                existing_by_name.vitec_id = vitec_id
                await session.flush()
            return existing_by_name

    if not name and vitec_id is None:
        return None

    # Create (best effort). If the seed script ran, this usually won't be needed.
    category = Category(
        name=name or f"Vitec {vitec_id}",
        vitec_id=vitec_id,
        icon=None,
        description="Imported/created by Vitec Next importer",
        sort_order=vitec_id or 0,
    )
    session.add(category)
    try:
        async with session.begin_nested():
            await session.flush()
        await session.refresh(category)
        return category
    except IntegrityError:
        # Fetch by name or vitec_id after conflict
        if vitec_id is not None:
            existing = await _get_category_by_vitec_id(session, vitec_id)
            if existing:
                return existing
        if name:
            res2 = await session.execute(select(Category).where(Category.name == name))
            existing_by_name = res2.scalar_one_or_none()
            if existing_by_name:
                return existing_by_name
        raise


async def _get_template_by_file_name(session, file_name: str) -> Template | None:
    res = await session.execute(select(Template).where(Template.file_name == file_name))
    return res.scalar_one_or_none()


@dataclass(frozen=True)
class TitleCandidate:
    id: Any
    title: str
    channel: str | None
    created_at: datetime | None


def _created_at_key(candidate: "TitleCandidate") -> datetime:
    created_at = candidate.created_at
    if created_at is None:
        return datetime.min.replace(tzinfo=UTC)
    if created_at.tzinfo is None:
        return created_at.replace(tzinfo=UTC)
    return created_at


async def _build_title_index(session) -> dict[str, list[TitleCandidate]]:
    res = await session.execute(select(Template.id, Template.title, Template.channel, Template.created_at))
    rows = res.all()
    index: dict[str, list[TitleCandidate]] = {}
    for template_id, title, channel, created_at in rows:
        key = _normalize_title(str(title or ""))
        if not key:
            continue
        index.setdefault(key, []).append(
            TitleCandidate(
                id=template_id,
                title=str(title or ""),
                channel=str(channel or "") if channel is not None else None,
                created_at=created_at,
            )
        )
    return index


def _choose_title_match(
    candidates: list[TitleCandidate],
    channel: str | None,
) -> tuple[TitleCandidate | None, str | None]:
    if not candidates:
        return None, None

    match_reason = "title"
    filtered = candidates
    if channel:
        channel_matches = [candidate for candidate in candidates if (candidate.channel or "").strip() == channel]
        if len(channel_matches) == 1:
            return channel_matches[0], "title+channel"
        if len(channel_matches) > 1:
            filtered = channel_matches
            match_reason = "title+channel"

    if len(filtered) == 1:
        return filtered[0], match_reason

    # Multiple matches: prefer the oldest template to keep history in versions.
    return sorted(filtered, key=_created_at_key)[0], f"{match_reason}+oldest"


@dataclass(frozen=True)
class ImportStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0

    def add(self, *, created=0, updated=0, skipped=0, failed=0) -> "ImportStats":
        return ImportStats(
            created=self.created + created,
            updated=self.updated + updated,
            skipped=self.skipped + skipped,
            failed=self.failed + failed,
        )


# -----------------------------------------------------------------------------
# Main import
# -----------------------------------------------------------------------------


async def import_vitec_export(
    *,
    input_path: Path,
    dry_run: bool,
    update_existing: bool,
    auto_sanitize: bool,
    match_title: bool,
    created_by: str,
) -> ImportStats:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    templates = raw.get("templates")
    if not isinstance(templates, list):
        raise ValueError("Invalid export: missing 'templates' array")

    export_version = str(raw.get("export_version", "unknown"))
    export_ts = raw.get("exported_at") or _utc_now_iso()

    sanitizer = get_sanitizer_service()

    stats = ImportStats()

    async with async_session_factory() as session:
        title_index: dict[str, list[TitleCandidate]] | None = None
        if match_title:
            title_index = await _build_title_index(session)

        for idx, item in enumerate(templates, 1):
            try:
                vitec_template_id = item.get("vitec_template_id")
                if vitec_template_id is None:
                    raise ValueError("Missing vitec_template_id")
                vitec_template_id_str = str(vitec_template_id).strip()

                title = (item.get("title") or "").strip()
                if not title:
                    title = f"Vitec template {vitec_template_id_str}"

                status = (item.get("status") or "published").strip()
                if status not in {"draft", "published", "archived"}:
                    status = "published"

                channel = (item.get("channel") or "pdf_email").strip()

                # Stable identity in Hub: derive a deterministic file_name unless provided
                file_name = (item.get("file_name") or "").strip()
                if not file_name:
                    safe_channel = channel.replace("/", "-").replace(" ", "_")
                    file_name = f"vitec_next_{vitec_template_id_str}_{safe_channel}.html"

                description = item.get("description")
                if not isinstance(description, str) or not description.strip():
                    description = f"Imported from Vitec Next (vitec_template_id={vitec_template_id_str})"

                content = item.get("content")
                if not isinstance(content, str):
                    content = ""
                content = content.strip()

                if not content:
                    logger.warning(f"[{idx}/{len(templates)}] Skipping empty content: {file_name} ({title})")
                    stats = stats.add(skipped=1)
                    continue

                processed_content = sanitizer.sanitize(content) if auto_sanitize else content
                file_size_bytes = len(processed_content.encode("utf-8"))

                # Common metadata that we always store/merge
                incoming_metadata = item.get("metadata")
                if not isinstance(incoming_metadata, dict):
                    incoming_metadata = {}
                attachments = _extract_vitec_attachments(item, incoming_metadata)
                if attachments:
                    incoming_metadata["vitec_attachments"] = attachments

                # Tags
                tag_names = _norm_str_list(item.get("tags"))
                origin_tag, origin_source = _resolve_origin_tag(tag_names, item, incoming_metadata)
                tag_names = _apply_origin_tag(tag_names, origin_tag)
                tag_ids: list[Any] = []
                for tag_name in tag_names:
                    tag = await _get_or_create_tag(session, tag_name)
                    tag_ids.append(tag.id)

                # Categories (supports legacy 'category' object too)
                categories_payload = item.get("categories")
                if not isinstance(categories_payload, list):
                    cat_single = item.get("category")
                    categories_payload = [cat_single] if isinstance(cat_single, dict) else []

                category_ids: list[Any] = []
                for cat in categories_payload:
                    if not isinstance(cat, dict):
                        continue
                    cat_vitec_id = cat.get("vitec_id")
                    try:
                        cat_vitec_id_int = int(cat_vitec_id) if cat_vitec_id is not None else None
                    except Exception:
                        cat_vitec_id_int = None

                    cat_name = cat.get("name")
                    cat_name_str = str(cat_name).strip() if cat_name is not None else None
                    category = await _get_or_create_category(
                        session,
                        name=cat_name_str if cat_name_str else None,
                        vitec_id=cat_vitec_id_int,
                    )
                    if category:
                        category_ids.append(category.id)

                existing = await _get_template_by_file_name(session, file_name)
                match_source: str | None = "file_name" if existing else None

                if existing is None and match_title and title_index is not None:
                    title_key = _normalize_title(title)
                    candidates = title_index.get(title_key, [])
                    chosen, match_source = _choose_title_match(candidates, channel)
                    if chosen:
                        if len(candidates) > 1:
                            logger.warning(
                                "Multiple templates matched title '%s'; using %s id=%s",
                                title,
                                match_source,
                                chosen.id,
                            )
                        existing = await TemplateService.get_by_id(session, chosen.id)
                        if existing is None:
                            match_source = None

                vitec_import_meta = {
                    "source": "vitec-next",
                    "vitec_template_id": vitec_template_id_str,
                    "export_version": export_version,
                    "exported_at": export_ts,
                    "imported_at": _utc_now_iso(),
                    "matched_by": match_source or "new",
                }
                if origin_tag:
                    vitec_import_meta["origin_tag"] = origin_tag
                    vitec_import_meta["origin_tag_source"] = origin_source
                if attachments:
                    vitec_import_meta["attachment_count"] = len(attachments)
                if existing is not None:
                    vitec_import_meta["matched_template_id"] = str(existing.id)

                if existing is None:
                    if dry_run:
                        logger.info(f"[DRY RUN] Would create: {file_name} ({title})")
                        stats = stats.add(created=1)
                        continue

                    template = await TemplateService.create(
                        session,
                        title=title,
                        description=description,
                        file_name=file_name,
                        file_type="html",
                        file_size_bytes=file_size_bytes,
                        azure_blob_url=f"vitec-next://template/{vitec_template_id_str}",
                        created_by=created_by,
                        status=status,
                        tag_ids=tag_ids or None,
                        category_ids=category_ids or None,
                        content=processed_content,
                    )

                    # Store metadata + compute merge fields once (without version bump)
                    merge_fields = TemplateAnalyzerService.extract_merge_fields(processed_content)
                    await TemplateService.update(
                        session,
                        template,
                        updated_by=created_by,
                        vitec_merge_fields=merge_fields,
                        metadata_json={
                            **incoming_metadata,
                            "vitec_import": vitec_import_meta,
                        },
                    )

                    # Apply settings fields
                    await _apply_settings_from_export(
                        session,
                        template_id=template.id,
                        updated_by=created_by,
                        item=item,
                        channel=channel,
                    )

                    logger.info(f"Created: {file_name} ({title})")
                    stats = stats.add(created=1)

                    if match_title and title_index is not None:
                        title_key = _normalize_title(template.title)
                        if title_key:
                            title_index.setdefault(title_key, []).append(
                                TitleCandidate(
                                    id=template.id,
                                    title=template.title,
                                    channel=template.channel,
                                    created_at=template.created_at,
                                )
                            )
                    continue

                # Existing template found
                if not update_existing:
                    logger.info(f"Skipped (exists): {file_name} ({existing.title})")
                    stats = stats.add(skipped=1)
                    continue

                if dry_run:
                    logger.info(f"[DRY RUN] Would update: {file_name} ({title})")
                    stats = stats.add(updated=1)
                    continue

                # Update metadata + tags/categories + basic fields
                existing_meta = existing.metadata_json or {}
                merged_meta = {
                    **existing_meta,
                    **incoming_metadata,
                    "vitec_import": {
                        **(existing_meta.get("vitec_import") or {}),
                        **vitec_import_meta,
                    },
                }

                await TemplateService.update(
                    session,
                    existing,
                    updated_by=created_by,
                    title=title,
                    description=description,
                    status=status,
                    file_size_bytes=file_size_bytes,
                    metadata_json=merged_meta,
                    tag_ids=tag_ids or [],
                    category_ids=category_ids or [],
                )

                # Update HTML content with versioning + merge field extraction
                await TemplateContentService.save_content(
                    session,
                    existing.id,
                    content=processed_content,
                    updated_by=created_by,
                    change_notes="Imported from Vitec Next export",
                    auto_sanitize=False,  # already applied above if requested
                )

                await _apply_settings_from_export(
                    session,
                    template_id=existing.id,
                    updated_by=created_by,
                    item=item,
                    channel=channel,
                )

                logger.info(f"Updated: {file_name} ({title})")
                stats = stats.add(updated=1)

            except Exception as e:
                logger.exception(f"Failed importing template index={idx}: {e}")
                stats = stats.add(failed=1)

        if dry_run:
            await session.rollback()
        else:
            await session.commit()

    return stats


async def _apply_settings_from_export(
    session,
    *,
    template_id: Any,
    updated_by: str,
    item: dict[str, Any],
    channel: str,
) -> None:
    margins = item.get("margins_cm")
    if not isinstance(margins, dict):
        margins = {}

    await TemplateSettingsService.update_settings(
        session,
        template_id,
        updated_by=updated_by,
        channel=channel,
        template_type=item.get("template_type"),
        receiver_type=item.get("receiver_type"),
        receiver=item.get("receiver"),
        extra_receivers=_norm_str_list(item.get("extra_receivers")),
        phases=_norm_str_list(item.get("phases")),
        assignment_types=_norm_str_list(item.get("assignment_types")),
        ownership_types=_norm_str_list(item.get("ownership_types")),
        departments=_norm_str_list(item.get("departments")),
        email_subject=item.get("email_subject"),
        margin_top=_as_decimal(margins.get("top")),
        margin_bottom=_as_decimal(margins.get("bottom")),
        margin_left=_as_decimal(margins.get("left")),
        margin_right=_as_decimal(margins.get("right")),
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Import Vitec Next templates from a JSON export")
    parser.add_argument("--input", required=True, type=str, help="Path to Vitec Next export JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing to DB")
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update templates when file_name already exists (otherwise skip)",
    )
    parser.add_argument(
        "--match-title",
        action="store_true",
        help="When file_name is not found, match existing templates by title (case-insensitive)",
    )
    parser.add_argument(
        "--auto-sanitize",
        action="store_true",
        help="Sanitize HTML during import (keeps Vitec Stilark compliance)",
    )
    parser.add_argument(
        "--created-by",
        type=str,
        default=os.environ.get("VITEC_IMPORT_USER", "vitec-import@system"),
        help="Email/name stored in created_by/updated_by fields",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    stats = await import_vitec_export(
        input_path=input_path,
        dry_run=args.dry_run,
        update_existing=args.update_existing,
        auto_sanitize=args.auto_sanitize,
        match_title=args.match_title,
        created_by=args.created_by,
    )

    logger.info(
        "Done. created=%s updated=%s skipped=%s failed=%s",
        stats.created,
        stats.updated,
        stats.skipped,
        stats.failed,
    )


if __name__ == "__main__":
    asyncio.run(main())
