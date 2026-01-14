from pathlib import Path

html = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_bruktbolig.html").read_text(encoding="utf-8")

print("=== Lily Watermark Verification ===")
print(f"Watermark img tag present: {'class=\"watermark-lily\"' in html}")
print(f"Watermark has Base64 data: {'watermark-lily' in html and 'data:image/png;base64' in html}")
print(f"Watermark CSS present: {'.watermark-lily' in html}")
print(f"Opacity style: {'opacity: 0.10' in html}")

