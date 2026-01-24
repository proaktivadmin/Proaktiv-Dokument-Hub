"""
Tests for notifications API endpoints.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.services.notification_service import NotificationService

_NOTIFICATIONS_PATH = Path(__file__).resolve().parents[1] / "app" / "routers" / "notifications.py"
_SPEC = spec_from_file_location("notifications_router_module", _NOTIFICATIONS_PATH)
if not _SPEC or not _SPEC.loader:
    raise RuntimeError("Failed to load notifications router module for tests.")
_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
notifications_router = _MODULE.router

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
async def notification_app(session_factory):
    test_app = FastAPI()
    test_app.include_router(notifications_router, prefix="/api")

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    test_app.dependency_overrides[get_db] = override_get_db
    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
async def async_client(notification_app):
    transport = ASGITransport(app=notification_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


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


async def _create_notification(session_factory, **overrides) -> Notification:
    async with session_factory() as session:
        notification = await NotificationService.create(
            session,
            _build_notification_data(**overrides),
        )
        await session.commit()
        return notification


@pytest.mark.asyncio
async def test_list_notifications(async_client, session_factory):
    first = await _create_notification(session_factory, title="First")
    await _create_notification(session_factory, title="Second")

    async with session_factory() as session:
        await NotificationService.mark_as_read(session, UUID(str(first.id)))
        await session.commit()

    response = await async_client.get("/api/notifications")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["unread_count"] == 1
    assert isinstance(payload["items"], list)


@pytest.mark.asyncio
async def test_get_unread_count(async_client, session_factory):
    first = await _create_notification(session_factory, title="First")
    await _create_notification(session_factory, title="Second")
    await _create_notification(session_factory, title="Third")

    async with session_factory() as session:
        await NotificationService.mark_as_read(session, UUID(str(first.id)))
        await session.commit()

    response = await async_client.get("/api/notifications/unread-count")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2


@pytest.mark.asyncio
async def test_mark_notification_read(async_client, session_factory):
    notification = await _create_notification(session_factory, title="Mark me")

    response = await async_client.patch(f"/api/notifications/{notification.id}/read")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_read"] is True


@pytest.mark.asyncio
async def test_mark_all_read(async_client, session_factory):
    await _create_notification(session_factory, title="First")
    await _create_notification(session_factory, title="Second")

    response = await async_client.post("/api/notifications/read-all")

    assert response.status_code == 200
    assert response.json()["count"] == 2

    unread_response = await async_client.get("/api/notifications/unread-count")
    assert unread_response.json()["count"] == 0


@pytest.mark.asyncio
async def test_clear_all(async_client, session_factory):
    await _create_notification(session_factory, title="First")
    await _create_notification(session_factory, title="Second")

    response = await async_client.post("/api/notifications/clear")

    assert response.status_code == 200
    assert response.json()["count"] == 2

    list_response = await async_client.get("/api/notifications")
    assert list_response.json()["total"] == 0
