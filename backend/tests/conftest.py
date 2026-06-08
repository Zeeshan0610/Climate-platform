"""Pytest fixtures: isolated SQLite DB + FastAPI TestClient."""
from __future__ import annotations

import os
import tempfile

import pytest

# Use a throwaway SQLite DB for the whole test session before app imports.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402

from app.db.init_db import init  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    init()
    yield
    try:
        os.unlink(_tmp.name)
    except OSError:
        pass


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def _token(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/api/auth/login", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(client):
    return {"Authorization": f"Bearer {_token(client, 'admin', 'admin123')}"}


@pytest.fixture(scope="session")
def viewer_headers(client):
    return {"Authorization": f"Bearer {_token(client, 'viewer', 'viewer123')}"}
