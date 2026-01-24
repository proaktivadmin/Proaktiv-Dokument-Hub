"""
Tests for NotificationService CRUD behavior.
"""

from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def async_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Notification.__table__.create)

    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Notification.__table__.drop)
        await engine.dispose()


@pytest.fixture
def session_factory(async_engine):
    return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session(session_factory):
    async with session_factory() as session:
        yield session


def _build_notification_data(
    *,
    notification_type: str = "employee_added",
    entity_type: str = "employee",
    entity_id=None,
    title: str = "Ny ansatt",
    message: str = "Test employee was added",
    severity: str = "info",
    metadata: dict | None = None,
) -> NotificationCreate:
    return NotificationCreate(
        type=notification_type,
        entity_type=entity_type,
        entity_id=entity_id or uuid4(),
        title=title,
        message=message,
        severity=severity,
        metadata=metadata or {"source": "test"},
    )


@pytest.mark.asyncio
async def test_create_notification(db_session):
    notification = await NotificationService.create(db_session, _build_notification_data())

    assert notification.id is not None
    assert notification.is_read is False
    assert notification.type == "employee_added"
    assert notification.severity == "info"


@pytest.mark.asyncio
async def test_mark_as_read(db_session):
    notification = await NotificationService.create(db_session, _build_notification_data())

    updated = await NotificationService.mark_as_read(db_session, UUID(str(notification.id)))

    assert updated is not None
    assert updated.is_read is True


@pytest.mark.asyncio
async def test_get_unread_count(db_session):
    for _ in range(3):
        await NotificationService.create(db_session, _build_notification_data())

    count = await NotificationService.get_unread_count(db_session)

    assert count == 3


@pytest.mark.asyncio
async def test_mark_all_as_read(db_session):
    for _ in range(3):
        await NotificationService.create(db_session, _build_notification_data())

    count = await NotificationService.mark_all_as_read(db_session)
    unread = await NotificationService.get_unread_count(db_session)

    assert count == 3
    assert unread == 0


@pytest.mark.asyncio
async def test_clear_all(db_session):
    for _ in range(3):
        await NotificationService.create(db_session, _build_notification_data())

    count = await NotificationService.clear_all(db_session)
    items, total, unread = await NotificationService.get_all(db_session)

    assert count == 3
    assert total == 0
    assert unread == 0
    assert items == []
