"""
Fix employee records - January 25, 2026

1. Add homepage_url for Elisabeth Brenne Nilsson
2. Merge Mads Kirkeslett duplicates (keep mk@proaktiv.no, delete mads@proaktiv.no)
"""

import os
import sys

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)

DRY_RUN = "--dry-run" in sys.argv


def main():
    print("=" * 60)
    print("Fix Employee Records - January 25, 2026")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print()

    with engine.connect() as conn:
        # 1. Update Elisabeth Brenne Nilsson homepage URL
        print("1. Updating Elisabeth Brenne Nilsson homepage URL...")
        elisabeth_id = "eaef0370-b495-4270-82e7-952aff053c83"
        elisabeth_homepage = (
            "https://proaktiv.no/eiendomsmegler/trondheim/proaktiv-trondheim-sentrum/elisabeth-brenne-nilsson"
        )

        if not DRY_RUN:
            conn.execute(
                text("""
                UPDATE employees
                SET homepage_profile_url = :homepage
                WHERE id = :id
            """),
                {"id": elisabeth_id, "homepage": elisabeth_homepage},
            )
            conn.commit()
        print(f"   ID: {elisabeth_id}")
        print(f"   Homepage: {elisabeth_homepage}")
        print(f"   Status: {'Would update' if DRY_RUN else 'UPDATED'}")
        print()

        # 2. Merge Mads Kirkeslett duplicates
        print("2. Merging Mads Kirkeslett duplicates...")
        mads_keep_id = "51f0a078-924e-4964-aa19-9517433da70d"  # mk@proaktiv.no (has homepage, better data)
        mads_delete_id = "04da0868-12cb-46e6-aca8-0cad1e07ef08"  # mads@proaktiv.no

        # Get data from both records for comparison
        result = conn.execute(
            text("""
            SELECT id, first_name, last_name, email, profile_image_url, title, phone, homepage_profile_url
            FROM employees
            WHERE id IN (:id1, :id2)
        """),
            {"id1": mads_keep_id, "id2": mads_delete_id},
        )

        records = list(result)
        for r in records:
            print(f"   ID: {r[0]}")
            print(f"      Name: {r[1]} {r[2]}")
            print(f"      Email: {r[3]}")
            print(f"      Photo: {r[4]}")
            print(f"      Title: {r[5]}")
            print(f"      Phone: {r[6]}")
            print(f"      Homepage: {r[7]}")
            print()

        print(f"   KEEPING: mk@proaktiv.no (ID: {mads_keep_id})")
        print(f"   DELETING: mads@proaktiv.no (ID: {mads_delete_id})")

        if not DRY_RUN:
            # Delete the duplicate record
            conn.execute(
                text("""
                DELETE FROM employees WHERE id = :id
            """),
                {"id": mads_delete_id},
            )
            conn.commit()
            print("   Status: DELETED duplicate")
        else:
            print("   Status: Would delete duplicate")

        print()
        print("=" * 60)
        if DRY_RUN:
            print("DRY RUN complete. Run without --dry-run to apply changes.")
        else:
            print("All changes applied successfully!")
        print("=" * 60)


if __name__ == "__main__":
    main()
