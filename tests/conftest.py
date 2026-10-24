from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import engine
from app.main import create_app


@pytest.fixture
def client(monkeypatch) -> TestClient:
    monkeypatch.setattr(engine, "connect", MagicMock(return_value=MagicMock()))
    with TestClient(create_app()) as test_client:
        yield test_client
