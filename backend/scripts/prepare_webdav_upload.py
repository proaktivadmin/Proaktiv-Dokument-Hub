"""
Prepare photos for WebDAV upload by renaming .no to _no in filenames.

This copies files from signature folder to a new webdav-upload folder
with the correct filename format (proaktiv_no instead of proaktiv.no).

Usage:
    python scripts/prepare_webdav_upload.py --dry-run   # Preview
    python scripts/prepare_webdav_upload.py             # Copy and rename
"""

import shutil
import sys
from pathlib import Path

SOURCE_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "signature"
OUTPUT_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "webdav-upload"

DRY_RUN = "--dry-run" in sys.argv


def main():
    print("=" * 70)
    print("PREPARE PHOTOS FOR WEBDAV UPLOAD")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"Source: {SOURCE_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    if not SOURCE_DIR.exists():
        print(f"ERROR: Source directory not found: {SOURCE_DIR}")
        return

    if not DRY_RUN:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find all jpg files
    files = list(SOURCE_DIR.glob("*.jpg")) + list(SOURCE_DIR.glob("*.JPG"))

    print(f"Found {len(files)} photo files\n")

    renamed_count = 0
    copied_count = 0

    for src_path in sorted(files):
        old_name = src_path.name

        # Replace dots with underscores in the entire filename (except extension)
        # e.g., alexander.abelseth@proaktiv.no.jpg -> alexander_abelseth@proaktiv_no.jpg
        name_part = old_name.rsplit(".", 1)[0]  # Remove extension
        ext = old_name.rsplit(".", 1)[1] if "." in old_name else "jpg"

        # Replace all dots with underscores in the name part
        new_name_part = name_part.replace(".", "_")
        new_name = f"{new_name_part}.{ext}"

        # Ensure lowercase
        new_name = new_name.lower()

        dst_path = OUTPUT_DIR / new_name

        if old_name != new_name:
            print(f"RENAME: {old_name}")
            print(f"     -> {new_name}")
            renamed_count += 1
        else:
            print(f"COPY:   {old_name}")
            copied_count += 1

        if not DRY_RUN:
            shutil.copy2(src_path, dst_path)

    print()
    print("=" * 70)
    print(f"Renamed: {renamed_count} files")
    print(f"Copied:  {copied_count} files (already correct)")
    print(f"Total:   {len(files)} files")
    print("=" * 70)

    if DRY_RUN:
        print("\nDRY RUN: No files were copied. Run without --dry-run to copy.")
    else:
        print(f"\nFiles ready for upload in: {OUTPUT_DIR}")
        print("Upload these files to: https://proaktiv.no/photos/employees/")


if __name__ == "__main__":
    main()
