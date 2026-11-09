from fastapi.testclient import TestClient
from sqlalchemy import select

from app.deps import get_db
from app.main import app
from app.models import User
from app.security import verify_password
from tests.db import PASSWORD, TestSession, fresh_db, get_test_db

client = TestClient(app)


def setup_function():
    fresh_db()
    app.dependency_overrides[get_db] = get_test_db


def teardown_function():
    app.dependency_overrides.clear()


def stored_hash(name: str) -> str:
    with TestSession() as session:
        return session.scalar(select(User.password_hash).where(User.name == name))


def test_answer_has_no_password():
    response = client.post("/users", json={"name": "Aida", "password": PASSWORD})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Aida"}


def test_database_keeps_a_hash():
    client.post("/users", json={"name": "Aida", "password": PASSWORD})

    hashed = stored_hash("Aida")

    assert hashed.startswith("$argon2id$")
    assert verify_password(PASSWORD, hashed)


def test_short_password_returns_422():
    response = client.post("/users", json={"name": "Aida", "password": "qwerty"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]


def test_missing_password_returns_422():
    response = client.post("/users", json={"name": "Aida"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]


def test_same_name_with_another_password_returns_409():
    client.post("/users", json={"name": "Aida", "password": PASSWORD})

    response = client.post("/users", json={"name": "Aida", "password": "another-pass-1"})

    assert response.status_code == 409
    assert response.json()["code"] == "user_exists"


def test_same_password_gives_different_hashes():
    client.post("/users", json={"name": "Aida", "password": PASSWORD})
    client.post("/users", json={"name": "Timur", "password": PASSWORD})

    assert stored_hash("Aida") != stored_hash("Timur")
