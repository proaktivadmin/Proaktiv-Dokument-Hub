"""Check employees with missing/incorrect photo URLs."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)

# Employee IDs from the URLs provided
employee_ids = [
    "78f4e2ba-b3f8-4357-9e2e-c3c86f394076",
    "ee853a21-29de-494a-93bf-b078131fa73a",
    "8d8ddb92-7ffc-4b87-a2cb-580c8a28ed7f",
    "5dc80a36-7178-4f54-bb33-b6d04428893b",
    "02a1e7a2-96ef-4411-88e1-82a694dd540f",
    "90acbd23-a940-492c-86a0-7e5dd0619224",
    "80f5263c-c5a6-4cdd-af6c-bd0bd5518fa7",
    "0a060212-4825-4a13-b7de-740400fd8865",
    "2ea7b7c5-b464-4930-b8b2-5c1963c5f259",
    "25f51849-a3d2-4cd0-bb86-fb9cc168bb5c",
    "fd9f8f9a-277a-4eab-9d84-3b35c8738924",
    "65e65952-99f6-42a9-8ff1-51156f0cd66e",
    "61afe35b-78dd-4685-acc1-6b9d501edbd2",
    "a0a1deda-3cc5-4e81-bde3-8b57f8b91d89",
]

with engine.connect() as conn:
    print("Checking employees with missing photos:\n")

    for emp_id in employee_ids:
        result = conn.execute(
            text("""
            SELECT id, first_name, last_name, email, profile_image_url
            FROM employees WHERE id = :id
        """),
            {"id": emp_id},
        )

        row = result.fetchone()
        if row:
            photo_url = row[4] or "(none)"
            has_webdav = "proaktiv.no/photos" in str(photo_url)
            status = "OK" if has_webdav else "NEEDS UPDATE"
            print(f"[{status}] {row[1]} {row[2]} ({row[3]})")
            print(f"         Photo: {photo_url[:70]}...")
            print()
        else:
            print(f"[NOT FOUND] ID: {emp_id}")
            print()
