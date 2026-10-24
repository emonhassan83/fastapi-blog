from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine, get_db
from app.main import create_app


@pytest.fixture
def db_session() -> MagicMock:
    session = MagicMock()
    post = MagicMock(
        id=1,
        title="Database Post",
        content="Loaded from PostgreSQL",
        published=True,
        rating=5,
        created_at=datetime(2026, 10, 24, tzinfo=UTC),
        updated_at=datetime(2026, 10, 24, tzinfo=UTC),
    )
    session.scalars.return_value.all.return_value = [post]
    session.get.return_value = post

    def refresh_record(record):
        record.id = 1
        record.created_at = datetime(2026, 10, 24, tzinfo=UTC)
        record.updated_at = datetime(2026, 10, 24, tzinfo=UTC)

    session.refresh.side_effect = refresh_record
    return session


@pytest.fixture
def client(monkeypatch, db_session: MagicMock) -> TestClient:
    monkeypatch.setattr(engine, "connect", MagicMock(return_value=MagicMock()))
    monkeypatch.setattr(Base.metadata, "create_all", MagicMock())
    app = create_app()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
