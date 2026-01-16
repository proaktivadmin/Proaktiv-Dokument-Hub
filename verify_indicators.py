from pathlib import Path

html_file = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_bruktbolig.html")

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=== Indicator Verification ===")
print(f"File size: {len(content)} bytes")
print(f"img-wrapper count: {content.count('class=\"img-wrapper\"')}")
print(f"indicator-svg count: {content.count('class=\"indicator-svg\"')}")
print(f"indicator-box count: {content.count('class=\"indicator-box\"')}")
print(f"indicator-arrow count: {content.count('class=\"indicator-arrow\"')}")
print()

# Check CSS is present
print("CSS check:")
print(f"  .img-wrapper style: {'OK' if '.img-wrapper {' in content else 'MISSING'}")
print(f"  .indicator-svg style: {'OK' if '.indicator-svg {' in content else 'MISSING'}")
print(f"  .indicator-box style: {'OK' if '.indicator-box {' in content else 'MISSING'}")
print()

# Verify file structure
print("File structure:")
print(f"  Has closing body tag: {'</body>' in content}")
print(f"  Has closing html tag: {'</html>' in content}")
print(f"  Has toggleImg function: {'function toggleImg' in content}")

