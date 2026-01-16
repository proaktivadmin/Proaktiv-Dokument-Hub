"""
SQLAlchemy Base Model Configuration

Provides cross-database compatible type aliases for PostgreSQL and SQLite.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData, JSON, String, Text
from sqlalchemy.dialects import postgresql
import uuid as uuid_module

# Naming convention for constraints (helps with Alembic migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


# Cross-database compatible types
# These use PostgreSQL-optimized types on PostgreSQL, but fall back to compatible types on SQLite
GUID = String(36).with_variant(postgresql.UUID(as_uuid=True), "postgresql")
JSONType = JSON().with_variant(postgresql.JSONB(), "postgresql")
ArrayType = JSON  # Store arrays as JSON (works on all databases)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    metadata = metadata
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name (snake_case)."""
        import re
        name = cls.__name__
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower() + 's'

