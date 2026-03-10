#!/usr/bin/env python3
"""
Merge a Vitec content patch into the existing vitec-next-export.json.

The patch file (vitec-next-content-patch.json) is a mapping of
template_id -> { content, details, margins, udf_fields }.

This script merges the fetched content and details back into the
original export, producing a complete vitec-next-export.json.

Usage:
    python scripts/tools/merge_content_patch.py
    python scripts/tools/merge_content_patch.py \
        --export ~/Downloads/vitec-next-export.json \
        --patch ~/Downloads/vitec-next-content-patch.json \
        --output data/vitec-next-export.json
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT = Path.home() / "Downloads" / "vitec-next-export.json"
DEFAULT_PATCH = Path.home() / "Downloads" / "vitec-next-content-patch.json"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "vitec-next-export.json"

CHANNEL_MAP = {0: "pdf_email", 1: "email", 2: "sms", 3: "pdf"}
RECEIVER_TYPE_MAP = {0: "Systemstandard", 1: "Kommunale", 2: "Egne/kundetilpasset"}


def merge(export_data: dict, patch_data: dict) -> dict:
    templates = export_data.get("templates", [])
    patched_count = 0
    empty_count = 0
    error_count = 0

    for template in templates:
        tid = template.get("vitec_template_id")
        if tid not in patch_data:
            continue

        patch = patch_data[tid]

        if patch.get("error"):
            error_count += 1
            continue

        content = patch.get("content", "")
        template["content"] = content

        if not content.strip():
            empty_count += 1
        else:
            patched_count += 1

        details = patch.get("details", {})
        margins = patch.get("margins", {})
        udf_fields = patch.get("udf_fields", [])

        meta = template.get("metadata", {})
        meta["vitec_details"] = details
        meta["content_meta"] = {"margins": margins, "udf_fields": udf_fields}
        template["metadata"] = meta

        if margins:
            template["margins_cm"] = {
                "top": margins.get("top", template.get("margins_cm", {}).get("top")),
                "bottom": margins.get("bottom", template.get("margins_cm", {}).get("bottom")),
                "left": margins.get("left", template.get("margins_cm", {}).get("left")),
                "right": margins.get("right", template.get("margins_cm", {}).get("right")),
            }

        if details:
            _enrich_from_details(template, details)

    export_data["exported_at"] = datetime.now(UTC).isoformat()
    export_data["source"]["note"] = (
        f"merged content patch: {patched_count} with content, "
        f"{empty_count} empty, {error_count} errors"
    )

    return export_data


def _enrich_from_details(template: dict, details: dict) -> None:
    """Fill in fields from vitec_details that the list endpoint doesn't provide."""
    vitec_raw = template.get("metadata", {}).get("vitec_raw", {})

    attachments = (
        details.get("attachments")
        or details.get("attachmentTemplates")
        or details.get("attachmentTemplateList")
        or details.get("documentTemplateAttachments")
        or []
    )
    if attachments:
        template["attachments"] = attachments

    receiver_type_raw = RECEIVER_TYPE_MAP.get(
        details.get("receiverType", vitec_raw.get("receiverType"))
    )
    if receiver_type_raw and receiver_type_raw != "Kommunale":
        template["receiver_type"] = receiver_type_raw

    for field in ("phases", "assignmentTypes", "ownershipTypes", "departments"):
        export_key = field.replace("T", "_t").replace("O", "_o")
        if field == "assignmentTypes":
            export_key = "assignment_types"
        elif field == "ownershipTypes":
            export_key = "ownership_types"
        else:
            export_key = field

        vals = details.get(field)
        if isinstance(vals, list) and vals:
            template[export_key] = vals


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge content patch into Vitec export")
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT, help="Original export JSON")
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH, help="Content patch JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output merged JSON")
    args = parser.parse_args()

    if not args.export.exists():
        raise SystemExit(f"Export file not found: {args.export}")
    if not args.patch.exists():
        raise SystemExit(f"Patch file not found: {args.patch}")

    export_data = json.loads(args.export.read_text(encoding="utf-8"))
    patch_data = json.loads(args.patch.read_text(encoding="utf-8"))

    total_templates = len(export_data.get("templates", []))
    total_patches = len(patch_data)
    print(f"Export: {total_templates} templates")
    print(f"Patch: {total_patches} entries")

    merged = merge(export_data, patch_data)

    with_content = sum(1 for t in merged["templates"] if (t.get("content") or "").strip())
    without_content = total_templates - with_content

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nMerged: {args.output}")
    print(f"  With content: {with_content}")
    print(f"  Without content: {without_content}")


if __name__ == "__main__":
    main()
