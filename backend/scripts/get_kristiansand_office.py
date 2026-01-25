"""Get Kristiansand office details."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, city FROM offices WHERE name ILIKE '%kristiansand%'"))
    for row in result:
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"City: {row[2]}")
