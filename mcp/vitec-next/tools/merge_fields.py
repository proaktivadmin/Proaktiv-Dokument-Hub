from __future__ import annotations

import re
from typing import Any

from mcp.server.fastmcp import FastMCP


MERGE_FIELD_PATTERN = re.compile(r"\[\[(\*?)([^\]]+)\]\]")
VITEC_IF_PATTERN = re.compile(r'vitec-if="([^"]+)"')
VITEC_FOREACH_PATTERN = re.compile(r'vitec-foreach="(\w+)\s+in\s+([^"]+)"')


def _normalize_path(value: str) -> str:
    candidate = value.strip()
    if candidate.startswith("Model."):
        candidate = candidate[6:]
    return candidate.casefold()


def _build_known_paths(flettekoder_data: dict[str, Any]) -> set[str]:
    known_paths: set[str] = set()
    for section in flettekoder_data.get("sections", []):
        for field in section.get("fields", []):
            path = str(field.get("path", "")).strip()
            if path:
                known_paths.add(_normalize_path(path))
    return known_paths


def register_merge_field_tools(mcp: FastMCP, flettekoder_data: dict[str, Any]) -> None:
    known_paths = _build_known_paths(flettekoder_data)

    @mcp.tool()
    def extract_merge_fields(html: str) -> dict[str, Any]:
        field_lookup: dict[str, dict[str, Any]] = {}
        for match in MERGE_FIELD_PATTERN.finditer(html or ""):
            is_required = bool(match.group(1))
            field_path = match.group(2).strip()
            if not field_path:
                continue

            normalized = _normalize_path(field_path)
            entry = field_lookup.get(
                field_path,
                {
                    "path": field_path,
                    "required": False,
                    "occurrences": 0,
                    "known": normalized in known_paths,
                },
            )
            entry["required"] = bool(entry["required"] or is_required)
            entry["occurrences"] = int(entry["occurrences"]) + 1
            entry["known"] = normalized in known_paths
            field_lookup[field_path] = entry

        condition_lookup: dict[str, dict[str, Any]] = {}
        for match in VITEC_IF_PATTERN.finditer(html or ""):
            expression = match.group(1).strip()
            if not expression:
                continue
            item = condition_lookup.get(expression, {"expression": expression, "occurrences": 0})
            item["occurrences"] = int(item["occurrences"]) + 1
            condition_lookup[expression] = item

        loop_lookup: dict[str, dict[str, Any]] = {}
        for match in VITEC_FOREACH_PATTERN.finditer(html or ""):
            variable = match.group(1).strip()
            collection = match.group(2).strip()
            if not variable or not collection:
                continue
            key = f"{variable}|{collection}"
            item = loop_lookup.get(
                key,
                {
                    "variable": variable,
                    "collection": collection,
                    "occurrences": 0,
                },
            )
            item["occurrences"] = int(item["occurrences"]) + 1
            loop_lookup[key] = item

        fields = sorted(field_lookup.values(), key=lambda item: str(item["path"]).casefold())
        conditions = sorted(condition_lookup.values(), key=lambda item: str(item["expression"]).casefold())
        loops = sorted(
            loop_lookup.values(),
            key=lambda item: (str(item["collection"]).casefold(), str(item["variable"]).casefold()),
        )

        loop_variables = {str(loop["variable"]).casefold() for loop in loops}
        unknown_fields = sorted(
            [
                str(item["path"])
                for item in fields
                if not item["known"]
                and not any(str(item["path"]).casefold().startswith(f"{var}.") for var in loop_variables)
            ],
            key=str.casefold,
        )

        return {
            "fields": fields,
            "conditions": conditions,
            "loops": loops,
            "unknown_fields": unknown_fields,
            "stats": {
                "field_count": len(fields),
                "required_field_count": sum(1 for item in fields if item["required"]),
                "condition_count": len(conditions),
                "loop_count": len(loops),
                "unknown_field_count": len(unknown_fields),
                "known_catalog_size": len(known_paths),
            },
        }
