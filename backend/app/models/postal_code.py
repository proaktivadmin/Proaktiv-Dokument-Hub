"""
PostalCode SQLAlchemy Model

Stores Norwegian postal code data from Bring Postnummerregister.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.office_territory import OfficeTerritory


class PostalCode(Base):
    """
    PostalCode model representing a Norwegian postal code.

    Data sourced from Bring Postnummerregister:
    https://www.bring.no/postnummerregister-ansi.txt
    """

    __tablename__ = "postal_codes"

    # Primary key (postal code itself)
    postal_code: Mapped[str] = mapped_column(String(10), primary_key=True)

    # Basic Info
    postal_name: Mapped[str] = mapped_column(String(100), nullable=False)
    municipality_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    municipality_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # 'G' (street), 'B' (PO box), 'F' (mixed), 'P' (special), 'S' (service)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    territories: Mapped[list["OfficeTerritory"]] = relationship(
        "OfficeTerritory", back_populates="postal_code_info", lazy="selectin"
    )

    # Indexes
    __table_args__ = (Index("idx_postal_codes_municipality", "municipality_code"),)

    def __repr__(self) -> str:
        return f"<PostalCode(code='{self.postal_code}', name='{self.postal_name}')>"

    @property
    def full_location(self) -> str:
        """Return formatted location string."""
        return f"{self.postal_code} {self.postal_name}"

    @property
    def category_name(self) -> str:
        """Return human-readable category name."""
        categories = {
            "G": "Gateadresser",
            "B": "Postboks",
            "F": "Både gateadresser og postboks",
            "P": "Spesielle postnummer",
            "S": "Serviceboks",
        }
        return categories.get(self.category or "", "Ukjent")

    @property
    def is_street_address(self) -> bool:
        """Check if postal code is for street addresses."""
        return self.category in ("G", "F")
