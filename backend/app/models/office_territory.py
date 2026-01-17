"""
OfficeTerritory SQLAlchemy Model

Maps postal codes to offices with multi-source support.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
import uuid

from app.models.base import Base, GUID

if TYPE_CHECKING:
    from app.models.office import Office
    from app.models.postal_code import PostalCode


class OfficeTerritory(Base):
    """
    OfficeTerritory model mapping postal codes to offices.
    
    Supports multiple sources (Vitec Next, Finn, Anbudstjenester, etc.)
    with priority-based conflict resolution and blacklisting.
    """
    
    __tablename__ = "office_territories"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    office_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("offices.id", ondelete="CASCADE"),
        nullable=False
    )
    postal_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("postal_codes.postal_code", ondelete="CASCADE"),
        nullable=False
    )
    
    # Source and priority
    source: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="vitec_next"
    )  # 'vitec_next' | 'finn' | 'anbudstjenester' | 'homepage' | 'other'
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Blacklist flag (area we don't cover)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Validity period
    valid_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valid_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    office: Mapped["Office"] = relationship(
        "Office",
        back_populates="territories"
    )
    
    postal_code_info: Mapped["PostalCode"] = relationship(
        "PostalCode",
        back_populates="territories"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint("office_id", "postal_code", "source", name="uq_office_territory_source"),
        Index("idx_office_territories_office_id", "office_id"),
        Index("idx_office_territories_postal_code", "postal_code"),
        Index("idx_office_territories_source", "source"),
    )
    
    def __repr__(self) -> str:
        return f"<OfficeTerritory(office_id={self.office_id}, postal_code='{self.postal_code}', source='{self.source}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if territory is currently active."""
        if self.is_blacklisted:
            return False
        
        today = date.today()
        
        if self.valid_from and today < self.valid_from:
            return False
        
        if self.valid_to and today > self.valid_to:
            return False
        
        return True
    
    @property
    def source_display_name(self) -> str:
        """Return human-readable source name."""
        names = {
            "vitec_next": "Vitec Next",
            "finn": "Finn.no",
            "anbudstjenester": "Anbudstjenester",
            "homepage": "Hjemmeside",
            "other": "Annen kilde"
        }
        return names.get(self.source, self.source)
