"""
Optimize employee photos for web use - Version 2.

Processes photos from an input folder, optimizes them, and outputs to separate folders:
- Optimized files go to the output folder (ready for WebDAV upload)
- Original files are moved to a backup folder

Target specs:
- Max dimension: 800px (suitable for 2x retina displays at 400px)
- Quality: 85% JPEG
- All outputs are JPEG format

Usage:
    python scripts/optimize_photos_v2.py [--dry-run] [--quality 85] [--max-size 800]

Examples:
    python scripts/optimize_photos_v2.py --dry-run                    # Preview
    python scripts/optimize_photos_v2.py                              # Optimize
    python scripts/optimize_photos_v2.py --input "C:\\path\\to\\input"  # Custom input
"""

import argparse
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("[ERROR] Pillow is required. Install with: pip install Pillow")
    exit(1)

# Default settings
DEFAULT_INPUT_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "new_optimization"
DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "webdav-ready"
DEFAULT_BACKUP_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "originals"
DEFAULT_MAX_SIZE = 800  # pixels (longest edge)
DEFAULT_QUALITY = 85  # JPEG quality (1-100)


def format_size(bytes_val: int) -> str:
    """Format bytes to human readable string."""
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val / 1024:.0f} KB"
    return f"{bytes_val} B"


def optimize_image(
    input_path: Path,
    output_path: Path,
    max_size: int = DEFAULT_MAX_SIZE,
    quality: int = DEFAULT_QUALITY,
    dry_run: bool = False,
) -> dict:
    """Optimize a single image and save to output path as JPEG."""
    original_size = input_path.stat().st_size

    with Image.open(input_path) as img:
        original_width, original_height = img.width, img.height

        # Convert to RGB if necessary (for PNG with transparency, etc.)
        if img.mode in ("RGBA", "P", "LA"):
            # Create white background for transparency
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            elif img.mode == "P":
                img = img.convert("RGBA")
                if img.mode == "RGBA":
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
            else:
                background.paste(img)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Calculate new dimensions (maintain aspect ratio)
        if max(original_width, original_height) > max_size:
            if original_width > original_height:
                new_width = max_size
                new_height = int(original_height * (max_size / original_width))
            else:
                new_height = max_size
                new_width = int(original_width * (max_size / original_height))

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            new_width, new_height = original_width, original_height

        if not dry_run:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Save optimized version as JPEG
            output_path = output_path.with_suffix(".jpg")
            img.save(output_path, "JPEG", quality=quality, optimize=True)
            new_size = output_path.stat().st_size
        else:
            # Estimate for dry run
            new_size = int(original_size * 0.05) if original_size > 1024 * 1024 else int(original_size * 0.3)

    savings = original_size - new_size
    savings_pct = (savings / original_size) * 100 if original_size > 0 else 0

    return {
        "input_path": input_path,
        "output_path": output_path.with_suffix(".jpg"),
        "original_size": original_size,
        "new_size": new_size,
        "savings": savings,
        "savings_pct": savings_pct,
        "original_dims": (original_width, original_height),
        "new_dims": (new_width, new_height),
        "resized": (original_width, original_height) != (new_width, new_height),
    }


def optimize_photos(
    input_dir: Path,
    output_dir: Path,
    backup_dir: Path,
    max_size: int = DEFAULT_MAX_SIZE,
    quality: int = DEFAULT_QUALITY,
    dry_run: bool = False,
) -> None:
    """Optimize all photos from input directory."""
    if not input_dir.exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        return

    # Find all image files (case-insensitive)
    photos = []
    seen = set()
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        for p in input_dir.glob(ext):
            if p.name.lower() not in seen:
                photos.append(p)
                seen.add(p.name.lower())

    # Exclude backup files
    photos = [p for p in photos if not p.stem.endswith(".original")]
    photos.sort()

    print("\n" + "=" * 70)
    print("PHOTO OPTIMIZATION v2")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (processing files)'}")
    print(f"Input:    {input_dir}")
    print(f"Output:   {output_dir}")
    print(f"Backups:  {backup_dir}")
    print(f"Photos found: {len(photos)}")
    print(f"Max dimension: {max_size}px")
    print(f"JPEG quality: {quality}%")
    print("-" * 70)

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.mkdir(parents=True, exist_ok=True)

    total_original = 0
    total_new = 0
    processed_count = 0
    errors = []

    for photo in photos:
        try:
            # Output file is always JPEG
            output_filename = photo.stem + ".jpg"
            output_path = output_dir / output_filename

            result = optimize_image(photo, output_path, max_size, quality, dry_run)

            print(f"\n[OK] {photo.name}")
            print(f"     Size: {format_size(result['original_size'])} -> {format_size(result['new_size'])}")
            print(f"     Dims: {result['original_dims'][0]}x{result['original_dims'][1]}", end="")
            if result["resized"]:
                print(f" -> {result['new_dims'][0]}x{result['new_dims'][1]}")
            else:
                print(" (unchanged)")
            print(f"     Saved: {format_size(result['savings'])} ({result['savings_pct']:.0f}%)")
            print(f"     Output: {result['output_path'].name}")

            # Move original to backup
            if not dry_run:
                backup_path = backup_dir / photo.name
                shutil.move(str(photo), str(backup_path))
                print(f"     Backup: {backup_path.name}")

            total_original += result["original_size"]
            total_new += result["new_size"]
            processed_count += 1

        except Exception as e:
            print(f"\n[ERROR] {photo.name}: {e}")
            errors.append((photo.name, str(e)))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Processed:    {processed_count} files")
    if errors:
        print(f"Errors:       {len(errors)} files")
        for name, err in errors:
            print(f"              - {name}: {err}")
    print(f"Total before: {format_size(total_original)}")
    print(f"Total after:  {format_size(total_new)}")
    if total_original > 0:
        print(
            f"Total saved:  {format_size(total_original - total_new)} ({((total_original - total_new) / total_original * 100):.0f}%)"
        )
    print("=" * 70)

    if dry_run:
        print("\n[INFO] This was a dry run. No files were modified.")
        print("[INFO] Run without --dry-run to process files.")
    else:
        print(f"\n[INFO] Optimized files saved to: {output_dir}")
        print(f"[INFO] Original files backed up to: {backup_dir}")
        print("[INFO] You can now upload the optimized files to WebDAV.")


def main():
    parser = argparse.ArgumentParser(description="Optimize employee photos for web use")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Path to input directory (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Path to output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--backup",
        type=Path,
        default=DEFAULT_BACKUP_DIR,
        help=f"Path to backup directory (default: {DEFAULT_BACKUP_DIR})",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=DEFAULT_MAX_SIZE,
        help=f"Maximum dimension in pixels (default: {DEFAULT_MAX_SIZE})",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=DEFAULT_QUALITY,
        help=f"JPEG quality 1-100 (default: {DEFAULT_QUALITY})",
    )
    args = parser.parse_args()

    optimize_photos(args.input, args.output, args.backup, args.max_size, args.quality, args.dry_run)


if __name__ == "__main__":
    main()
