"""
Seed Merge Fields from snippets.json

Imports merge fields from the resources/snippets.json file into the database.
Also runs auto-discovery on existing templates to find additional fields.

Usage:
    python -m scripts.seed_merge_fields
"""

import asyncio
import json
import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import async_session_factory
from app.models.merge_field import MergeField
from app.services.merge_field_service import MergeFieldService


# Regex to extract field path from [[path]]
MERGE_FIELD_REGEX = re.compile(r'\[\[([^\]]+)\]\]')


def parse_category(category_str: str) -> str:
    """Parse category from snippets.json format."""
    # "Tags: Selger" -> "Selger"
    # "Tags: Megler/Kontor" -> "Megler"
    if category_str.startswith("Tags: "):
        category = category_str.replace("Tags: ", "")
        if "/" in category:
            category = category.split("/")[0]
        return category
    return category_str


def extract_fields_from_code(code: str) -> list[str]:
    """Extract all merge field paths from a code snippet."""
    return MERGE_FIELD_REGEX.findall(code)


async def seed_from_snippets():
    """Import merge fields from snippets.json."""
    # Load snippets.json
    snippets_path = Path(__file__).parent.parent.parent / "resources" / "snippets.json"
    
    if not snippets_path.exists():
        print(f"Error: snippets.json not found at {snippets_path}")
        return
    
    with open(snippets_path, "r", encoding="utf-8") as f:
        snippets = json.load(f)
    
    async with async_session_factory() as db:
        # Get existing paths
        result = await db.execute(select(MergeField.path))
        existing_paths = {row[0] for row in result.all()}
        
        added_count = 0
        skipped_count = 0
        
        for category_group in snippets:
            category_raw = category_group.get("category", "Ukjent")
            category = parse_category(category_raw)
            
            # Skip non-tag categories (Vitec Logic, Layout)
            if not category_raw.startswith("Tags:"):
                print(f"Skipping non-tag category: {category_raw}")
                continue
            
            for item in category_group.get("items", []):
                code = item.get("code", "")
                label = item.get("label", "")
                desc = item.get("desc", "")
                
                # Extract field paths from code
                paths = extract_fields_from_code(code)
                
                for path in paths:
                    if path in existing_paths:
                        skipped_count += 1
                        continue
                    
                    # Determine if iterable (selger fields are iterable)
                    is_iterable = path.startswith("selger.")
                    
                    # Determine parent model
                    parent_model = None
                    if "." in path:
                        prefix = path.split(".")[0]
                        model_map = {
                            "selger": "Model.selgere",
                            "kjoper": "Model.kjopere",
                            "eiendom": "Model.eiendom",
                            "ansvarligmegler": "Model.ansvarligmegler",
                            "meglerkontor": "Model.meglerkontor",
                            "oppgjor": "Model.oppgjor",
                            "oppdrag": "Model.oppdrag",
                        }
                        parent_model = model_map.get(prefix)
                    
                    # Determine data type
                    data_type = "string"
                    if any(x in path.lower() for x in ["pris", "sum", "prosent"]):
                        data_type = "number"
                    
                    # Create merge field
                    await MergeFieldService.create(
                        db,
                        path=path,
                        category=category,
                        label=label,
                        description=desc,
                        data_type=data_type,
                        is_iterable=is_iterable,
                        parent_model=parent_model
                    )
                    
                    existing_paths.add(path)
                    added_count += 1
                    print(f"  + {path} ({category})")
        
        await db.commit()
        print(f"\nSeed complete: {added_count} added, {skipped_count} skipped")


async def run_discovery():
    """Run auto-discovery on existing templates."""
    async with async_session_factory() as db:
        print("\nRunning auto-discovery on templates...")
        result = await MergeFieldService.discover_all(db, create_missing=True)
        await db.commit()
        
        print(f"Templates scanned: {result['templates_scanned']}")
        print(f"Discovered: {result['discovered_count']} fields")
        print(f"New fields: {len(result['new_fields'])}")
        print(f"Existing fields: {len(result['existing_fields'])}")
        
        if result['new_fields']:
            print("\nNew fields added:")
            for field in sorted(result['new_fields']):
                print(f"  + {field}")


async def main():
    """Main entry point."""
    print("=" * 50)
    print("Seeding Merge Fields from snippets.json")
    print("=" * 50)
    
    await seed_from_snippets()
    await run_discovery()
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
