from pathlib import Path

html_file = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_bruktbolig.html")

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=== HTML File Verification ===")
print(f"File size: {len(content)} bytes")
print(f"Has toggleImg function: {'function toggleImg' in content}")
print(f"Has closing body tag: {'</body>' in content}")
print(f"Has closing html tag: {'</html>' in content}")
print(f"Base64 images count: {content.count('data:image/png;base64')}")
print(f"Max-height 1200px: {'max-height: 1200px' in content}")
print(f"Bracket divs remaining: {content.count('class=\"bracket')}")
print()

# Check last 300 chars to verify file is complete
print("Last 300 characters:")
print(content[-300:])

