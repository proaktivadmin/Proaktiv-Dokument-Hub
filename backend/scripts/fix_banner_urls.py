"""Fix office banner URLs to use correct URL-encoded Norwegian characters."""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:lOZBFAkACyDixRzjSHjRQCrdVTwuDrxA@shuttle.proxy.rlwy.net:51557/railway"
engine = create_engine(DATABASE_URL)

BASE_URL = "https://proaktiv.no/photos/offices/"

# Correct URLs with URL-encoded Norwegian characters
# å = %C3%A5, æ = %C3%A6, ø = %C3%B8
corrections = [
    # Ålesund - å = %C3%A5
    ("cd3630ba-6f0a-440a-abb6-42bb4d69a7c4", "proaktiv-%C3%A5lesund.jpg"),
    # Jæren - æ = %C3%A6
    ("ba998112-e5db-4ee3-8716-191ef3dd564c", "proaktiv-j%C3%A6ren.jpg"),
    # Lillestrøm - ø = %C3%B8
    ("fa6c80b9-3a84-49d6-8509-c12b6fe1c3bc", "proaktiv-lillestr%C3%B8m.jpg"),
    # Lørenskog - ø = %C3%B8
    ("15f6cd1f-dac2-42a0-bb67-28d776816b63", "proaktiv-l%C3%B8renskog.jpg"),
    # Trondheim Øst - ø = %C3%B8
    ("f7f08b5f-0662-456b-bc6d-c92fb5f07185", "proaktiv-trondheim-%C3%B8st.jpg"),
]

with engine.connect() as conn:
    for office_id, filename in corrections:
        url = BASE_URL + filename
        result = conn.execute(
            text("""
            UPDATE offices SET banner_image_url = :url, updated_at = NOW()
            WHERE id = :id
        """),
            {"url": url, "id": office_id},
        )

        # Get office name for logging
        name_result = conn.execute(text("SELECT name FROM offices WHERE id = :id"), {"id": office_id})
        name = name_result.fetchone()[0]
        print(f"Updated: {name}")
        print(f"  -> {url}")

    conn.commit()
    print()
    print("Done! All offices with special characters have been corrected.")
