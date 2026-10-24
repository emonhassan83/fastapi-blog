from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.database import engine
from app.main import create_app


def test_database_connection_failure_aborts_startup(monkeypatch, caplog):
    monkeypatch.setattr(
        engine,
        "connect",
        Mock(side_effect=OperationalError("SELECT 1", {}, Exception("connection refused"))),
    )

    with pytest.raises(RuntimeError, match="server startup aborted"), TestClient(create_app()):
        pass

    assert "PostgreSQL connection failed" in caplog.text
