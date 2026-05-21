import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.room_manager import room_manager
from app.storage import default_storage


@pytest.fixture(autouse=True)
def clean_state():
    default_storage.clear()
    room_manager.clear()
    yield
    default_storage.clear()
    room_manager.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user10_headers():
    return {"X-User-Id": "10"}


@pytest.fixture
def user20_headers():
    return {"X-User-Id": "20"}


@pytest.fixture
def admin_headers():
    return {"X-User-Id": "1", "X-User-Role": "admin"}
