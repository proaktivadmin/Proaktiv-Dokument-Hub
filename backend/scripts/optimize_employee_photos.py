"""
Optimize employee photos for web use.

Resizes and compresses photos to reasonable dimensions for avatars and signatures.
Original files are preserved with a .original extension.

Target specs:
- Max dimension: 800px (suitable for 2x retina displays at 400px)
- Quality: 85% JPEG
- Target file size: <200KB per photo

Usage:
    python scripts/optimize_employee_photos.py [--dry-run] [--quality 85] [--max-size 800]

Examples:
    python scripts/optimize_employee_photos.py --dry-run           # Preview
    python scripts/optimize_employee_photos.py                     # Optimize in place
    python scripts/optimize_employee_photos.py --quality 80        # Lower quality
    python scripts/optimize_employee_photos.py --max-size 600      # Smaller dimensions
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
DEFAULT_PHOTOS_DIR = Path.home() / "Documents" / "ProaktivPhotos" / "webdav-upload" / "photos" / "employees"
DEFAULT_MAX_SIZE = 800  # pixels (longest edge)
DEFAULT_QUALITY = 85  # JPEG quality (1-100)
SIZE_THRESHOLD = 500 * 1024  # 500 KB - only optimize files larger than this


def get_image_info(path: Path) -> dict:
    """Get image dimensions and file size."""
    with Image.open(path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_bytes": path.stat().st_size,
        }


def optimize_image(
    path: Path,
    max_size: int = DEFAULT_MAX_SIZE,
    quality: int = DEFAULT_QUALITY,
    dry_run: bool = False,
) -> dict:
    """Optimize a single image."""
    original_size = path.stat().st_size

    with Image.open(path) as img:
        original_width, original_height = img.width, img.height

        # Convert to RGB if necessary (for PNG with transparency, etc.)
        if img.mode in ("RGBA", "P", "LA"):
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
            # Backup original
            backup_path = path.with_suffix(".original.jpg")
            if not backup_path.exists():
                shutil.copy2(path, backup_path)

            # Save optimized version
            img.save(path, "JPEG", quality=quality, optimize=True)

    new_size = path.stat().st_size if not dry_run else int(original_size * 0.1)  # Estimate for dry run
    savings = original_size - new_size
    savings_pct = (savings / original_size) * 100 if original_size > 0 else 0

    return {
        "original_size": original_size,
        "new_size": new_size,
        "savings": savings,
        "savings_pct": savings_pct,
        "original_dims": (original_width, original_height),
        "new_dims": (new_width, new_height),
        "resized": (original_width, original_height) != (new_width, new_height),
    }


def format_size(bytes_val: int) -> str:
    """Format bytes to human readable string."""
    if bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val / 1024:.0f} KB"
    return f"{bytes_val} B"


def optimize_photos(
    photos_dir: Path,
    max_size: int = DEFAULT_MAX_SIZE,
    quality: int = DEFAULT_QUALITY,
    dry_run: bool = False,
) -> None:
    """Optimize all photos in directory."""
    if not photos_dir.exists():
        print(f"[ERROR] Photos directory not found: {photos_dir}")
        return

    photos = list(photos_dir.glob("*.jpg"))
    # Exclude backup files
    photos = [p for p in photos if not p.stem.endswith(".original")]

    print("\n" + "=" * 70)
    print("PHOTO OPTIMIZATION")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (optimizing files)'}")
    print(f"Directory: {photos_dir}")
    print(f"Photos found: {len(photos)}")
    print(f"Max dimension: {max_size}px")
    print(f"JPEG quality: {quality}%")
    print("-" * 70)

    total_original = 0
    total_new = 0
    optimized_count = 0
    skipped_count = 0

    # Sort by size (largest first)
    photos.sort(key=lambda p: p.stat().st_size, reverse=True)

    for photo in photos:
        size = photo.stat().st_size

        # Skip small files
        if size < SIZE_THRESHOLD:
            skipped_count += 1
            continue

        try:
            result = optimize_image(photo, max_size, quality, dry_run)

            print(f"\n[OPTIMIZE] {photo.name}")
            print(f"           Size: {format_size(result['original_size'])} -> {format_size(result['new_size'])}")
            print(f"           Dims: {result['original_dims'][0]}x{result['original_dims'][1]}", end="")
            if result["resized"]:
                print(f" -> {result['new_dims'][0]}x{result['new_dims'][1]}")
            else:
                print(" (unchanged)")
            print(f"           Saved: {format_size(result['savings'])} ({result['savings_pct']:.0f}%)")

            total_original += result["original_size"]
            total_new += result["new_size"]
            optimized_count += 1

        except Exception as e:
            print(f"\n[ERROR] {photo.name}: {e}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Optimized:    {optimized_count} files")
    print(f"Skipped:      {skipped_count} files (already < {format_size(SIZE_THRESHOLD)})")
    print(f"Total before: {format_size(total_original)}")
    print(f"Total after:  {format_size(total_new)}")
    print(
        f"Total saved:  {format_size(total_original - total_new)} ({((total_original - total_new) / total_original * 100) if total_original > 0 else 0:.0f}%)"
    )
    print("=" * 70)

    if dry_run:
        print("\n[INFO] This was a dry run. No files were modified.")
        print("[INFO] Run without --dry-run to apply optimizations.")


def main():
    parser = argparse.ArgumentParser(description="Optimize employee photos for web use")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--photos-dir",
        type=Path,
        default=DEFAULT_PHOTOS_DIR,
        help=f"Path to photos directory (default: {DEFAULT_PHOTOS_DIR})",
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

    optimize_photos(args.photos_dir, args.max_size, args.quality, args.dry_run)


if __name__ == "__main__":
    main()
