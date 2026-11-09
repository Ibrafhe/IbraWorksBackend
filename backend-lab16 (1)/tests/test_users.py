from fastapi.testclient import TestClient

from app.deps import get_db
from app.main import app
from tests.db import PASSWORD, fresh_db, get_test_db

client = TestClient(app)


def setup_function():
    fresh_db()
    app.dependency_overrides[get_db] = get_test_db


def teardown_function():
    app.dependency_overrides.clear()


def test_create_user_returns_201():
    response = client.post("/users", json={"name": "Aida", "password": PASSWORD})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Aida"}


def test_same_name_returns_409():
    client.post("/users", json={"name": "Aida", "password": PASSWORD})

    response = client.post("/users", json={"name": "Aida", "password": PASSWORD})

    assert response.status_code == 409
    assert response.json()["code"] == "user_exists"


def test_unknown_user_returns_404():
    response = client.get("/users/99")

    assert response.status_code == 404
    assert response.json()["code"] == "user_not_found"


def test_name_is_free_again_after_409():
    client.post("/users", json={"name": "Aida", "password": PASSWORD})
    client.post("/users", json={"name": "Aida", "password": PASSWORD})

    response = client.post("/users", json={"name": "Timur", "password": PASSWORD})

    assert response.status_code == 201
    assert response.json() == {"id": 2, "name": "Timur"}
