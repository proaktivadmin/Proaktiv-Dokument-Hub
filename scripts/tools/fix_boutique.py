import base64, re

with open('scripts/production/Tilbudsbrev_Boutique_Hotel_PRODUCTION.html', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Replace corrupted klamme base64 with correct one from source file
with open(r'C:\Users\Adrian\Downloads\assets tilbudsbrev\Klamme_-_Bronze.png', 'rb') as f:
    correct_b64 = base64.b64encode(f.read()).decode('ascii')

content = re.sub(
    r'data:image/png;base64,[A-Za-z0-9+/=]+',
    'data:image/png;base64,' + correct_b64,
    content
)

# Fix 2: Add !important override so c-sum rows are never hidden by the
# tbody:last-child tr:last-child td { display: none } pattern
old_rule = '#vitecTemplate .roles-table tbody:last-child tr:last-child td {\n    display: none;\n}'
new_rule = (
    '#vitecTemplate .roles-table tbody:last-child tr:last-child td {\n'
    '    display: none;\n'
    '}\n\n'
    '/* Sum rows must always be visible regardless of tbody position */\n'
    '#vitecTemplate .roles-table tr.c-sum td {\n'
    '    display: table-cell !important;\n'
    '}\n\n'
    '#vitecTemplate .roles-table-sm tr.c-sum td {\n'
    '    display: table-cell !important;\n'
    '}'
)
content = content.replace(old_rule, new_rule)

with open('scripts/production/Tilbudsbrev_Boutique_Hotel_PRODUCTION.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open('scripts/production/Tilbudsbrev_Boutique_Hotel_PRODUCTION.html', encoding='utf-8') as f:
    content2 = f.read()

b64 = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', content2)
if b64:
    b64str = b64.group(1)
    decoded = base64.b64decode(b64str)
    print(f'Klamme base64: {len(b64str)} chars, {len(decoded)} bytes (expected 3697), valid: {len(b64str) % 4 == 0}')

has_override = 'c-sum td' in content2 and '!important' in content2
print(f'Sum row override: {has_override}')
print(f'File: {len(content2)} chars')
