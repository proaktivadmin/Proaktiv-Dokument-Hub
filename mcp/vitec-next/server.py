from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from resources.flettekoder import register_flettekoder_resources
from resources.reference import register_reference_resources
from tools.merge_fields import register_merge_field_tools
from tools.validation import register_validation_tools


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FLETTEKODER_PATH = DATA_DIR / "flettekoder.json"
REFERENCE_PATH = DATA_DIR / "reference_data.json"


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


flettekoder_data = _load_json(FLETTEKODER_PATH)
reference_data = _load_json(REFERENCE_PATH)

mcp = FastMCP("vitec-next")

register_flettekoder_resources(mcp, flettekoder_data)
register_reference_resources(mcp, reference_data)
register_validation_tools(mcp)
register_merge_field_tools(mcp, flettekoder_data)


if __name__ == "__main__":
    mcp.run(transport="stdio")
