"""
Convert documents to Markdown using `uvx markitdown`.

Supports HTML/PDF/DOCX/RTF and many other formats exposed by markitdown.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_conversion(input_path: Path, output_path: Path | None, force: bool) -> int:
    if not input_path.exists():
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    if output_path and output_path.exists() and not force:
        print(f"Output already exists: {output_path} (use --force to overwrite)", file=sys.stderr)
        return 1

    if shutil.which("uvx") is None:
        print("Missing dependency: uvx not found on PATH.", file=sys.stderr)
        print("Install uv: https://docs.astral.sh/uv/getting-started/installation/", file=sys.stderr)
        return 1

    command: list[str] = ["uvx", "markitdown", str(input_path)]
    if output_path:
        command.extend(["-o", str(output_path)])

    try:
        result = subprocess.run(command, check=False)
        return result.returncode
    except OSError as exc:
        print(f"Failed to run markitdown: {exc}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a file to Markdown using uvx markitdown.",
    )
    parser.add_argument("input", help="Input file path (html, pdf, docx, rtf, etc.)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output markdown file path. If omitted, writes to stdout.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file if it exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    return run_conversion(input_path=input_path, output_path=output_path, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
