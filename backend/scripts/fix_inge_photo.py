"""Fix Inge-André Godø's profile photo URL."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Update Inge's photo URL to WebDAV
    result = conn.execute(
        text("""
        UPDATE employees
        SET profile_image_url = :photo_url
        WHERE email = :email
        RETURNING id, first_name, last_name, email, profile_image_url
    """),
        {"email": "inge@proaktiv.no", "photo_url": "https://proaktiv.no/photos/employees/inge%40proaktiv_no.jpg"},
    )

    updated = result.fetchone()
    if updated:
        print(f"UPDATED: {updated[1]} {updated[2]} ({updated[3]})")
        print(f"  New photo URL: {updated[4]}")
    else:
        print("NOT FOUND: inge@proaktiv.no")

    conn.commit()
