#!/usr/bin/env python3
"""
Prepare the Vitec content patch script for browser execution.

Reads template IDs from the existing export and injects them into
the browser_evaluate JavaScript template.

Usage:
    python scripts/tools/prepare_patch_script.py
    python scripts/tools/prepare_patch_script.py --export-path path/to/vitec-next-export.json
"""

import argparse
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parents[1]
TEMPLATE_SCRIPT = SCRIPT_DIR / "vitec_content_patch.js"
OUTPUT_SCRIPT = REPO_ROOT / "data" / "vitec_content_patch_ready.js"
DEFAULT_EXPORT = Path.home() / "Downloads" / "vitec-next-export.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Inject template IDs into patch script")
    parser.add_argument(
        "--export-path",
        type=Path,
        default=DEFAULT_EXPORT,
        help=f"Path to vitec-next-export.json (default: {DEFAULT_EXPORT})",
    )
    args = parser.parse_args()

    export_data = json.loads(args.export_path.read_text(encoding="utf-8"))
    template_ids = [t["vitec_template_id"] for t in export_data["templates"]]

    js_template = TEMPLATE_SCRIPT.read_text(encoding="utf-8")
    ids_json = json.dumps(template_ids)
    js_ready = js_template.replace("%%TEMPLATE_IDS%%", ids_json)

    OUTPUT_SCRIPT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SCRIPT.write_text(js_ready, encoding="utf-8")

    print(f"Template IDs: {len(template_ids)}")
    print(f"Ready script: {OUTPUT_SCRIPT}")
    print()
    print("Next steps:")
    print("  1. Open Vitec Next in Chrome and log in")
    print("  2. Use browser_evaluate to run the script (it processes 25 at a time)")
    print("  3. Re-run until status is 'complete'")
    print("  4. The final run triggers a download of vitec-next-content-patch.json")


if __name__ == "__main__":
    main()
