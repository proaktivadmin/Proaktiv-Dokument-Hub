from __future__ import annotations

import ast
import datetime as dt
import html
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


PARSER_VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[3]
SOURCE_DOC = ROOT / "docs" / "Alle-flettekoder-25.9.md"
SEED_SCRIPT = ROOT / "backend" / "scripts" / "seed_merge_fields.py"
OUTPUT_FILE = ROOT / "mcp" / "vitec-next" / "data" / "flettekoder.json"

FIELD_PATTERN = re.compile(r"\[\[(\*)?([^\[\]]+?)\]\]")
CONDITION_PATTERN = re.compile(r"vitec-if\s*=\s*(?:\"([^\"]+)\"|'([^']+)')")
LOOP_PATTERN = re.compile(r"vitec-foreach\s*=\s*(?:\"([^\"]+)\"|'([^']+)')")
SEED_LIST_PATTERN = re.compile(
    r"VITEC_MERGE_FIELDS\s*=\s*\[(.*?)\]\s*async def",
    re.DOTALL,
)
SEED_DICT_PATTERN = re.compile(r"\{.*?\}", re.DOTALL)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def normalize_path(path: str) -> str:
    return clean_text(path).lower()


def extract_seed_index() -> dict[str, dict[str, Any]]:
    seed_text = SEED_SCRIPT.read_text(encoding="utf-8")
    list_match = SEED_LIST_PATTERN.search(seed_text)
    if not list_match:
        raise RuntimeError("Could not locate VITEC_MERGE_FIELDS in seed_merge_fields.py")

    index: dict[str, dict[str, Any]] = {}
    for dict_blob in SEED_DICT_PATTERN.findall(list_match.group(1)):
        try:
            data = ast.literal_eval(dict_blob)
        except (SyntaxError, ValueError):
            continue
        if not isinstance(data, dict) or "path" not in data:
            continue
        index[normalize_path(str(data["path"]))] = data
    return index


def parse_flettekoder(seed_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_text = SOURCE_DOC.read_text(encoding="utf-8")
    soup = BeautifulSoup(source_text, "html.parser")
    unescaped_source = html.unescape(source_text)

    sections: dict[str, list[dict[str, Any]]] = {}
    section_order: list[str] = []
    field_index: dict[tuple[str, str, str], dict[str, Any]] = {}
    current_section: str | None = None
    enriched_count = 0

    for row in soup.find_all("tr"):
        section_header = row.find("h3")
        if section_header:
            current_section = clean_text(section_header.get_text(" ", strip=True))
            if current_section not in sections:
                sections[current_section] = []
                section_order.append(current_section)
            continue

        if not current_section:
            continue

        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        label = clean_text(cells[0].get_text(" ", strip=True))
        if not label:
            continue

        value_html = html.unescape(" ".join(str(cell) for cell in cells[1:]))
        value_text = clean_text(" ".join(cell.get_text(" ", strip=True) for cell in cells[1:]))
        matches = [
            {
                "required": bool(star),
                "path": clean_text(path),
            }
            for star, path in FIELD_PATTERN.findall(value_html)
        ]
        if not matches:
            continue

        version = clean_text(row.get("data-version", "")) or None
        for match in matches:
            path = match["path"]
            required = bool(match["required"])
            dedupe_key = (current_section, label, normalize_path(path))

            existing_field = field_index.get(dedupe_key)
            if existing_field:
                existing_field["required"] = existing_field["required"] or required
                continue

            field: dict[str, Any] = {
                "path": path,
                "label": label,
                "raw_example": value_text,
                "version": version,
                "required": required,
            }

            seed_data = seed_index.get(normalize_path(path))
            if seed_data:
                enriched_count += 1
                field["enrichment"] = {
                    "category": seed_data.get("category"),
                    "label": seed_data.get("label"),
                    "description": seed_data.get("description"),
                    "example_value": seed_data.get("example_value"),
                    "data_type": seed_data.get("data_type"),
                    "is_iterable": seed_data.get("is_iterable"),
                    "parent_model": seed_data.get("parent_model"),
                }

            sections[current_section].append(field)
            field_index[dedupe_key] = field

    ordered_sections = [
        {
            "name": section_name,
            "field_count": len(sections[section_name]),
            "fields": sections[section_name],
        }
        for section_name in section_order
    ]

    condition_expressions = sorted(
        {
            clean_text(match.group(1) or match.group(2) or "")
            for match in CONDITION_PATTERN.finditer(unescaped_source)
            if clean_text(match.group(1) or match.group(2) or "")
        }
    )
    loop_expressions = sorted(
        {
            clean_text(match.group(1) or match.group(2) or "")
            for match in LOOP_PATTERN.finditer(unescaped_source)
            if clean_text(match.group(1) or match.group(2) or "")
        }
    )
    loop_collections = sorted(
        {
            clean_text(expr.split(" in ", 1)[1])
            for expr in loop_expressions
            if " in " in expr
        }
    )

    total_fields = sum(len(section["fields"]) for section in ordered_sections)
    return {
        "metadata": {
            "version": PARSER_VERSION,
            "parsed_at": dt.datetime.now(dt.UTC).isoformat(),
            "source_file": str(SOURCE_DOC.relative_to(ROOT)).replace("\\", "/"),
            "seed_file": str(SEED_SCRIPT.relative_to(ROOT)).replace("\\", "/"),
            "total_sections": len(ordered_sections),
            "total_fields": total_fields,
            "enriched_fields": enriched_count,
        },
        "conditions": {
            "syntax": 'vitec-if="expression"',
            "expressions": condition_expressions,
            "notes": "Best-effort extraction from source content.",
        },
        "loops": {
            "syntax": 'vitec-foreach="item in collection"',
            "expressions": loop_expressions,
            "collections": loop_collections,
            "notes": "Best-effort extraction from source content.",
        },
        "sections": ordered_sections,
    }


def main() -> None:
    seed_index = extract_seed_index()
    parsed = parse_flettekoder(seed_index)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(parsed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {OUTPUT_FILE}")
    print(
        f"Sections: {parsed['metadata']['total_sections']} | "
        f"Fields: {parsed['metadata']['total_fields']} | "
        f"Enriched: {parsed['metadata']['enriched_fields']}"
    )


if __name__ == "__main__":
    main()
