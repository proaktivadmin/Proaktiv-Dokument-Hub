from __future__ import annotations

import json
import unicodedata
from urllib.parse import unquote

from mcp.server.fastmcp import FastMCP


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold().strip()


def _json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def register_flettekoder_resources(mcp: FastMCP, flettekoder_data: dict) -> None:
    sections: list[dict] = flettekoder_data.get("sections", [])
    category_lookup = {_normalize(section.get("name", "")): section for section in sections}

    @mcp.resource("vitec://flettekoder")
    def flettekoder_categories() -> str:
        payload = {
            "metadata": flettekoder_data.get("metadata", {}),
            "total_categories": len(sections),
            "total_fields": sum(section.get("field_count", 0) for section in sections),
            "categories": [
                {
                    "name": section.get("name"),
                    "field_count": section.get("field_count", 0),
                }
                for section in sections
            ],
        }
        return _json(payload)

    @mcp.resource("vitec://flettekoder/{category}")
    def flettekoder_category(category: str) -> str:
        category_name = unquote(category)
        section = category_lookup.get(_normalize(category_name))
        if not section:
            payload = {
                "error": "category_not_found",
                "category": category_name,
                "available_categories": [item.get("name") for item in sections],
            }
            return _json(payload)

        payload = {
            "name": section.get("name"),
            "field_count": section.get("field_count", 0),
            "fields": section.get("fields", []),
        }
        return _json(payload)

    @mcp.resource("vitec://flettekoder/search/{query}")
    def flettekoder_search(query: str) -> str:
        search_query = unquote(query)
        needle = _normalize(search_query)
        matches: list[dict] = []

        for section in sections:
            section_name = section.get("name")
            for field in section.get("fields", []):
                path = str(field.get("path", ""))
                label = str(field.get("label", ""))
                if needle in _normalize(path) or needle in _normalize(label):
                    matches.append(
                        {
                            "category": section_name,
                            "path": path,
                            "label": label,
                            "required": field.get("required", False),
                            "version": field.get("version"),
                            "raw_example": field.get("raw_example"),
                        }
                    )

        payload = {
            "query": search_query,
            "count": len(matches),
            "matches": matches,
        }
        return _json(payload)
