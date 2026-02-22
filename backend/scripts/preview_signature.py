#!/usr/bin/env python
"""
Preview email signature for an employee.
Generates the HTML signature and saves it to a file for review.
"""

import argparse
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text


def get_employee_data(db_url: str, email: str) -> dict | None:
    """Get employee data from database."""
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT
                e.first_name, e.last_name, e.email, e.title, e.phone,
                e.profile_image_url,
                o.name as office_name, o.city, o.street_address,
                o.postal_code, o.phone as office_phone, o.email as office_email
            FROM employees e
            LEFT JOIN offices o ON e.office_id = o.id
            WHERE e.email = :email
        """),
            {"email": email},
        )

        row = result.fetchone()
        if not row:
            return None

        return {
            "first_name": row[0],
            "last_name": row[1],
            "email": row[2],
            "title": row[3],
            "phone": row[4],
            "profile_image_url": row[5],
            "office_name": row[6],
            "office_city": row[7],
            "office_street": row[8],
            "office_postal": row[9],
            "office_phone": row[10],
            "office_email": row[11],
        }


def render_signature(template_path: str, employee: dict) -> str:
    """Render signature template with employee data."""
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    replacements = {
        "{{DisplayName}}": f"{employee['first_name']} {employee['last_name']}",
        "{{JobTitle}}": employee["title"] or "",
        "{{Email}}": employee["email"] or "",
        "{{MobilePhone}}": employee["phone"] or "",
        "{{OfficeName}}": employee["office_name"] or "",
        "{{OfficeAddress}}": employee["office_street"] or "",
        "{{OfficePostal}}": f"{employee['office_postal'] or ''} {employee['office_city'] or ''}".strip(),
        "{{OfficePhone}}": employee["office_phone"] or "",
        "{{OfficeEmail}}": employee["office_email"] or "",
        "{{ProfileUrl}}": employee["profile_image_url"] or "",
    }

    for key, value in replacements.items():
        template = template.replace(key, value)

    return template


def main():
    parser = argparse.ArgumentParser(description="Preview email signature for an employee")
    parser.add_argument("email", help="Employee email address")
    parser.add_argument("--output", "-o", help="Output HTML file path", default="signature_preview.html")
    parser.add_argument("--db-url", help="Database URL (defaults to DATABASE_URL env var)")
    args = parser.parse_args()

    # Get database URL
    db_url = args.db_url or os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable is required.")
        print("  $env:DATABASE_URL = 'postgresql://...'")
        sys.exit(1)

    print(f"Looking up employee: {args.email}")

    # Get employee data
    employee = get_employee_data(db_url, args.email)
    if not employee:
        print(f"Employee not found: {args.email}")
        sys.exit(1)

    print(f"Found: {employee['first_name']} {employee['last_name']}")
    print(f"Title: {employee['title']}")
    print(f"Phone: {employee['phone']}")
    print(f"Office: {employee['office_name']}")

    # Render signature
    script_dir = Path(__file__).parent
    template_path = script_dir / "templates" / "email-signature.html"

    if not template_path.exists():
        print(f"Template not found: {template_path}")
        sys.exit(1)

    signature_html = render_signature(str(template_path), employee)

    # Save to file
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(signature_html)

    print(f"\nSignature saved to: {output_path.absolute()}")
    print(f"Open in browser to preview: file:///{output_path.absolute()}")

    # Also print the signature size
    print(f"Signature size: {len(signature_html)} bytes")


if __name__ == "__main__":
    main()
