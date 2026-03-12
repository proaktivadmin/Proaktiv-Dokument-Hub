from __future__ import annotations

import json
import unicodedata
from urllib.parse import unquote

from mcp.server.fastmcp import FastMCP


def _normalize(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold().strip()


def _json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def register_reference_resources(mcp: FastMCP, reference_data: dict) -> None:
    dokumentkategorier = reference_data.get("dokumentkategorier", [])
    objektstyper = reference_data.get("objektstyper", [])
    stilark = reference_data.get("stilark", {})
    layout_partials = reference_data.get("layout_partials", [])
    layout_lookup = {_normalize(item.get("name", "")): item for item in layout_partials}

    @mcp.resource("vitec://kategorier")
    def kategorier() -> str:
        payload = {
            "count": len(dokumentkategorier),
            "kategorier": dokumentkategorier,
        }
        return _json(payload)

    @mcp.resource("vitec://objektstyper")
    def objektstyper_resource() -> str:
        payload = {
            "count": len(objektstyper),
            "objektstyper": objektstyper,
        }
        return _json(payload)

    @mcp.resource("vitec://stilark")
    def stilark_resource() -> str:
        return _json(stilark)

    @mcp.resource("vitec://layout/{name}")
    def layout_resource(name: str) -> str:
        layout_name = unquote(name)
        layout = layout_lookup.get(_normalize(layout_name))
        if not layout:
            payload = {
                "error": "layout_not_found",
                "name": layout_name,
                "available_layouts": [item.get("name") for item in layout_partials],
            }
            return _json(payload)
        return _json(layout)
