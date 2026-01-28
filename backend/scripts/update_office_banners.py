"""Update office banner URLs from WebDAV files."""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:lOZBFAkACyDixRzjSHjRQCrdVTwuDrxA@shuttle.proxy.rlwy.net:51557/railway"
engine = create_engine(DATABASE_URL)

BASE_URL = "https://proaktiv.no/photos/offices/"

with engine.connect() as conn:
    # Update offices with Norwegian special chars using LIKE patterns

    # Update Alesund
    result = conn.execute(
        text("""
        UPDATE offices SET banner_image_url = :url, updated_at = NOW()
        WHERE name LIKE '%lesund%'
    """),
        {"url": BASE_URL + "proaktiv-alesund.jpg"},
    )
    print(f"Alesund: {result.rowcount} updated")

    # Update Jaren
    result = conn.execute(
        text("""
        UPDATE offices SET banner_image_url = :url, updated_at = NOW()
        WHERE name LIKE 'Proaktiv J%ren'
    """),
        {"url": BASE_URL + "proaktiv-jaeren.jpg"},
    )
    print(f"Jaren: {result.rowcount} updated")

    # Update Lorenskog
    result = conn.execute(
        text("""
        UPDATE offices SET banner_image_url = :url, updated_at = NOW()
        WHERE name LIKE '%renskog%'
    """),
        {"url": BASE_URL + "proaktiv-lorenskog.jpg"},
    )
    print(f"Lorenskog: {result.rowcount} updated")

    # Update Lillestrom
    result = conn.execute(
        text("""
        UPDATE offices SET banner_image_url = :url, updated_at = NOW()
        WHERE name LIKE '%Lillestr%'
    """),
        {"url": BASE_URL + "proaktiv-lillestrom.jpg"},
    )
    print(f"Lillestrom: {result.rowcount} updated")

    # Update Trondheim Ost
    result = conn.execute(
        text("""
        UPDATE offices SET banner_image_url = :url, updated_at = NOW()
        WHERE name LIKE '%Trondheim%st' AND name NOT LIKE '%Sentrum%' AND name NOT LIKE '%Syd%'
    """),
        {"url": BASE_URL + "proaktiv-trondheim-ost.jpg"},
    )
    print(f"Trondheim Ost: {result.rowcount} updated")

    conn.commit()
    print()
    print("Done! Verifying all offices now have banners...")

    # Verify all offices
    result = conn.execute(
        text("""
        SELECT name, banner_image_url
        FROM offices
        WHERE is_active = true
        ORDER BY name
    """)
    )

    print()
    missing = 0
    for row in result:
        has_webdav = row.banner_image_url and "proaktiv.no" in row.banner_image_url
        status = "OK" if has_webdav else "MISSING"
        if not has_webdav:
            missing += 1
        print(f"{status}: {row.name}")
        if has_webdav:
            print(f"       -> {row.banner_image_url}")

    print()
    print(f"Summary: {missing} offices still missing WebDAV banner URLs")
