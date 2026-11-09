from fastapi.testclient import TestClient

from app.deps import get_db
from app.main import app
from tests.db import fresh_db, get_test_db

client = TestClient(app)


def setup_function():
    fresh_db()
    app.dependency_overrides[get_db] = get_test_db


def teardown_function():
    app.dependency_overrides.clear()


def test_create_room_returns_201():
    response = client.post("/rooms", json={"title": "  general  "})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "general"}


def test_list_rooms():
    client.post("/rooms", json={"title": "general"})
    client.post("/rooms", json={"title": "homework"})

    response = client.get("/rooms")

    assert response.status_code == 200
    assert [room["title"] for room in response.json()] == ["general", "homework"]


def test_blank_title_returns_422():
    response = client.post("/rooms", json={"title": "   "})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]


def test_unknown_room_returns_404():
    response = client.get("/rooms/99")

    assert response.status_code == 404
    assert response.json()["code"] == "room_not_found"
