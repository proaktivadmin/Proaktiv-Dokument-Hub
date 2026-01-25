#!/usr/bin/env python3
"""List active employees from the database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from app.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(
        text(
            """
            SELECT id, first_name, last_name, email, facebook_url, instagram_url, linkedin_url
            FROM employees
            WHERE status = 'active'
            ORDER BY last_name, first_name
            """
        )
    )
    for row in result:
        emp_id, first, last, email, fb, ig, li = row
        social = []
        if fb:
            social.append("FB")
        if ig:
            social.append("IG")
        if li:
            social.append("LI")
        social_str = ",".join(social) if social else "-"
        print(f"{first} {last} | {email} | [{social_str}]")
