"""
Alembic Environment Configuration

Configures Alembic to use our SQLAlchemy models and database settings.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context
from alembic.script import ScriptDirectory
import sys
import os
import json
import time

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our models and settings
from app.models import Base
from app.config import settings

# This is the Alembic Config object
config = context.config

DEBUG_LOG_PATH = r"c:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\.cursor\debug.log"


def _debug_log(message: str, data: dict, hypothesis_id: str, location: str) -> None:
    payload = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload) + "\n")
    except Exception:
        pass

# Override sqlalchemy.url from our settings
def get_database_url() -> str:
    """Get database URL, ensuring it uses sync drivers for Alembic."""
    url = settings.DATABASE_URL
    # Alembic needs sync drivers
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")
    if "+aiosqlite" in url:
        url = url.replace("+aiosqlite", "")
    return url


def ensure_sqlite_directory(url: str) -> None:
    """Ensure SQLite database directory exists."""
    if url.startswith("sqlite"):
        path = url.replace("sqlite:///", "").replace("sqlite://", "")
        if path.startswith("/"):
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)


# Ensure directory exists for SQLite
ensure_sqlite_directory(settings.DATABASE_URL)

config.set_main_option("sqlalchemy.url", get_database_url())

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def is_sqlite(url: str) -> bool:
    """Check if URL is for SQLite database."""
    return url.startswith("sqlite")


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=is_sqlite(url),  # SQLite requires batch mode
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.
    """
    # region agent log H1
    _debug_log(
        "alembic online start",
        {
            "script_location": config.get_main_option("script_location"),
            "config_file": config.config_file_name,
        },
        "H1",
        "alembic/env.py:run_migrations_online:entry",
    )
    # endregion

    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    try:
        has_0008 = script.get_revision("0008") is not None
    except Exception:
        has_0008 = False
    revision_count = sum(1 for _ in script.walk_revisions())

    # region agent log H1
    _debug_log(
        "alembic script revisions",
        {"heads": heads, "revision_count": revision_count, "has_0008": has_0008},
        "H1",
        "alembic/env.py:run_migrations_online:script",
    )
    # endregion

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        url = config.get_main_option("sqlalchemy.url")
        current_rev = None
        rev_error = None
        try:
            current_rev = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
        except Exception as exc:
            rev_error = exc.__class__.__name__

        # region agent log H2
        _debug_log(
            "alembic version table",
            {"current_rev": current_rev, "error": rev_error},
            "H2",
            "alembic/env.py:run_migrations_online:version",
        )
        # endregion

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=is_sqlite(url),  # SQLite requires batch mode
        )

        # region agent log H3
        _debug_log(
            "alembic context configured",
            {"render_as_batch": is_sqlite(url)},
            "H3",
            "alembic/env.py:run_migrations_online:configured",
        )
        # endregion

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

