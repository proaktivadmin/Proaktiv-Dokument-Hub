"""Batch conversion script for .docx/.rtf templates using WordConversionService."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.word_conversion_service import WordConversionService


async def convert_file(service: WordConversionService, filepath: str) -> dict:
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_bytes = f.read()

    try:
        result = await service.convert(file_bytes, filename)
        return {
            "filename": filename,
            "success": True,
            "is_valid": result.is_valid,
            "html_length": len(result.html),
            "warnings": result.warnings,
            "validation": [
                {"rule": v.rule, "passed": v.passed, "detail": v.detail}
                for v in result.validation
            ],
            "merge_fields": result.merge_fields_detected,
            "html": result.html,
        }
    except Exception as e:
        return {
            "filename": filename,
            "success": False,
            "error": str(e),
        }


async def main():
    source_dir = sys.argv[1] if len(sys.argv) > 1 else ""
    if not source_dir:
        print("Usage: python batch_convert.py <directory>")
        sys.exit(1)

    files = sorted([
        os.path.join(source_dir, f)
        for f in os.listdir(source_dir)
        if (f.endswith(".docx") or f.endswith(".rtf")) and "[1]" not in f
    ])

    print(f"Found {len(files)} template files to convert\n")

    service = WordConversionService()
    results = []

    for i, filepath in enumerate(files, 1):
        fname = os.path.basename(filepath)
        print(f"[{i}/{len(files)}] Converting: {fname}")
        result = await convert_file(service, filepath)

        if result["success"]:
            passed = sum(1 for v in result["validation"] if v["passed"])
            total = len(result["validation"])
            fields = len(result["merge_fields"])
            print(f"  -> {'VALID' if result['is_valid'] else 'ISSUES'} | {passed}/{total} checks | {fields} merge fields | {result['html_length']} chars")
            if result["warnings"]:
                for w in result["warnings"]:
                    print(f"  [warn] {w}")
            failed = [v for v in result["validation"] if not v["passed"]]
            if failed:
                for v in failed:
                    print(f"  [FAIL] {v['rule']}: {v['detail']}")
        else:
            print(f"  -> ERROR: {result['error']}")

        results.append(result)
        print()

    output_path = os.path.join(os.path.dirname(__file__), "batch_convert_results.json")
    results_for_json = []
    for r in results:
        r_copy = dict(r)
        if "html" in r_copy:
            r_copy["html_preview"] = r_copy["html"][:500] + "..." if len(r_copy.get("html", "")) > 500 else r_copy.get("html", "")
            del r_copy["html"]
        results_for_json.append(r_copy)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_for_json, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {output_path}")

    html_dir = os.path.join(os.path.dirname(__file__), "converted_html")
    os.makedirs(html_dir, exist_ok=True)
    for r in results:
        if r["success"] and "html" in r:
            safe_name = os.path.splitext(r["filename"])[0] + ".html"
            with open(os.path.join(html_dir, safe_name), "w", encoding="utf-8") as f:
                f.write(r["html"])

    print(f"HTML files saved to {html_dir}")

    print("\n=== SUMMARY ===")
    valid_count = sum(1 for r in results if r.get("is_valid"))
    warn_count = sum(1 for r in results if r.get("success") and not r.get("is_valid"))
    fail_count = sum(1 for r in results if not r.get("success"))
    print(f"Valid:    {valid_count}/{len(results)}")
    print(f"Warnings: {warn_count}/{len(results)}")
    print(f"Failed:   {fail_count}/{len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
