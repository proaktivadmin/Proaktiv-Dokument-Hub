import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path if needed
sys.path.append(os.path.join(os.getcwd(), "backend"))


def update_office_colors():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found")
        return

    # High-contrast palette (20 colors)
    palette = [
        "#E6194B",
        "#3CB44B",
        "#FFE119",
        "#4363D8",
        "#F58231",
        "#911EB4",
        "#42FCF9",
        "#F032E6",
        "#BFEF45",
        "#FABEBE",
        "#008080",
        "#E6BEFF",
        "#9A6324",
        "#FFFAC8",
        "#800000",
        "#AAFFC3",
        "#808000",
        "#FFD8B1",
        "#000075",
        "#A9A9A9",
    ]

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get active offices
        result = session.execute(text("SELECT id, name FROM offices WHERE is_active = true ORDER BY name"))
        offices = result.all()

        print(f"Assigning colors to {len(offices)} offices...")

        for i, office in enumerate(offices):
            color = palette[i % len(palette)]
            session.execute(text("UPDATE offices SET color = :color WHERE id = :id"), {"color": color, "id": office.id})
            print(f"  {office.name}: {color}")

        session.commit()
        print("Successfully updated office colors.")
    except Exception as e:
        session.rollback()
        print(f"Error updating office colors: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    update_office_colors()
