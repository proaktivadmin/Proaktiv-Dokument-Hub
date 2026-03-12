from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


PARSER_VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[3]
SOURCE_DOC = ROOT / ".cursor" / "vitec-reference.md"
OUTPUT_FILE = ROOT / "mcp" / "vitec-next" / "data" / "reference_data.json"

SECTION_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
FIELD_PATTERN = re.compile(r"\[\[\*?([^\[\]]+?)\]\]")
CODE_BLOCK_PATTERN = re.compile(r"```(?:[a-zA-Z0-9_-]+)?\n(.*?)```", re.DOTALL)
NUMBERED_RULE_PATTERN = re.compile(r"^\d+\.\s+(.*)$", re.MULTILINE)


def parse_value(value: str) -> Any:
    text = value.strip()
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def parse_markdown_table_block(lines: list[str]) -> list[dict[str, Any]]:
    if len(lines) < 2:
        return []

    headers = [cell.strip() for cell in lines[0].strip().strip("|").split("|")]
    if not headers:
        return []

    records: list[dict[str, Any]] = []
    for row in lines[2:]:
        row = row.strip()
        if not row.startswith("|"):
            continue
        values = [cell.strip() for cell in row.strip("|").split("|")]
        if not values:
            continue
        if len(values) < len(headers):
            values.extend([""] * (len(headers) - len(values)))
        record = {headers[i]: parse_value(values[i]) for i in range(len(headers))}
        records.append(record)
    return records


def extract_table_blocks(text: str) -> list[list[dict[str, Any]]]:
    lines = text.splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if line.strip().startswith("|"):
            current.append(line)
            continue
        if current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    return [parse_markdown_table_block(block) for block in blocks if len(block) >= 2]


def extract_named_tables(section_text: str) -> dict[str, list[dict[str, Any]]]:
    """
    Extract markdown tables and map each to the nearest preceding ### subheading.
    """
    lines = section_text.splitlines()
    named_tables: dict[str, list[dict[str, Any]]] = {}
    current_heading = "untitled"
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("### "):
            current_heading = line[4:].strip()
            i += 1
            continue

        if line.startswith("|"):
            block: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            parsed = parse_markdown_table_block(block)
            if parsed:
                named_tables[current_heading] = parsed
            continue

        i += 1

    return named_tables


def split_sections(markdown: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(markdown))
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        section_name = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(markdown)
        sections[section_name] = markdown[start:end].strip()
    return sections


def first_table(section_text: str) -> list[dict[str, Any]]:
    tables = extract_table_blocks(section_text)
    return tables[0] if tables else []


def all_code_blocks(section_text: str) -> list[str]:
    return [block.strip() for block in CODE_BLOCK_PATTERN.findall(section_text)]


def extract_layout_partials(sections: dict[str, str]) -> list[dict[str, Any]]:
    partials: list[dict[str, Any]] = []

    for name, content in sections.items():
        if not (
            name.startswith("Vitec Bunntekst")
            or name.startswith("Vitec Topptekst")
            or name in {"E-post signatur", "SMS-signatur"}
        ):
            continue

        code_blocks = all_code_blocks(content)
        merge_fields = sorted({match.strip() for match in FIELD_PATTERN.findall(content)})
        partials.append(
            {
                "name": name,
                "merge_fields": merge_fields,
                "code_blocks": code_blocks,
            }
        )

    return partials


def parse_reference_data() -> dict[str, Any]:
    markdown = SOURCE_DOC.read_text(encoding="utf-8")
    sections = split_sections(markdown)

    stilark_section = sections.get("Vitec Stilark (Base Stylesheet)", "")
    stilark_tables = extract_table_blocks(stilark_section)
    dokumentmaler_tables = extract_named_tables(sections.get("Dokumentmaler (199/216)", ""))
    standardmaler_tables = extract_named_tables(sections.get("Standardmaler (System Defaults)", ""))

    result = {
        "metadata": {
            "version": PARSER_VERSION,
            "parsed_at": dt.datetime.now(dt.UTC).isoformat(),
            "source_file": str(SOURCE_DOC.relative_to(ROOT)).replace("\\", "/"),
        },
        "dokumentkategorier": first_table(sections.get("Dokumentkategorier", "")),
        "objektstyper": first_table(sections.get("Objektstyper (Eiendomstyper)", "")),
        "oppdragskategorier": first_table(sections.get("Oppdragskategorier", "")),
        "faser": first_table(sections.get("Dokumentmapper (Faser)", "")),
        "maltyper": {
            "dokumentmaler": dokumentmaler_tables.get("Eksempel-maler fra Vitec Next", []),
            "dokumentmaler_metadata": {
                "mal_typer": dokumentmaler_tables.get("Mal-typer", []),
                "faser": dokumentmaler_tables.get("Faser", []),
                "mottaker_typer": dokumentmaler_tables.get("Mottaker-typer", []),
            },
            "standardmaler": standardmaler_tables,
        },
        "stilark": {
            "nokkelegenskaper": stilark_tables[0] if stilark_tables else [],
            "viktige_regler": NUMBERED_RULE_PATTERN.findall(stilark_section),
            "code_blocks": all_code_blocks(stilark_section),
        },
        "layout_partials": extract_layout_partials(sections),
    }

    result["metadata"]["stats"] = {
        "dokumentkategorier": len(result["dokumentkategorier"]),
        "objektstyper": len(result["objektstyper"]),
        "oppdragskategorier": len(result["oppdragskategorier"]),
        "faser": len(result["faser"]),
        "dokumentmaler": len(result["maltyper"]["dokumentmaler"]),
        "standardmaler": sum(len(items) for items in result["maltyper"]["standardmaler"].values()),
        "layout_partials": len(result["layout_partials"]),
    }
    return result


def main() -> None:
    parsed = parse_reference_data()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(parsed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_FILE}")
    print(f"Stats: {parsed['metadata']['stats']}")


if __name__ == "__main__":
    main()
