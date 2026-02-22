"""Create Nadja Ulriksen employee profile."""

import os
import uuid

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

# Employee details from Vitec Next screenshot
employee = {
    "id": str(uuid.uuid4()),
    "first_name": "Nadja",
    "last_name": "Ulriksen",
    "email": "nadja@proaktiv.no",
    "title": "Backoffice / Medhjelper",
    "vitec_employee_id": "NAUL",
    "office_id": "e62e8d8e-9a2f-4137-be4b-d7058ecf94bd",  # Proaktiv Kristiansand
    "employee_type": "internal",
    "status": "active",
    "profile_image_url": "https://proaktiv.no/photos/employees/nadja%40proaktiv_no.jpg",
}

with engine.connect() as conn:
    # Check if already exists
    result = conn.execute(text("SELECT id FROM employees WHERE email = :email"), {"email": employee["email"]})
    existing = result.fetchone()

    if existing:
        print(f"Employee with email {employee['email']} already exists with ID: {existing[0]}")
    else:
        conn.execute(
            text("""
            INSERT INTO employees (id, first_name, last_name, email, title, vitec_employee_id, office_id, employee_type, status, profile_image_url)
            VALUES (:id, :first_name, :last_name, :email, :title, :vitec_employee_id, :office_id, :employee_type, :status, :profile_image_url)
        """),
            employee,
        )
        conn.commit()
        print(f"Created employee: {employee['first_name']} {employee['last_name']}")
        print(f"  ID: {employee['id']}")
        print(f"  Email: {employee['email']}")
        print(f"  Title: {employee['title']}")
        print("  Office: Proaktiv Kristiansand")
        print(f"  Photo: {employee['profile_image_url']}")
