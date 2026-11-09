import time

import jwt
from fastapi.testclient import TestClient

from app.deps import get_db
from app.main import app
from app.security import create_access_token
from tests.db import PASSWORD, fresh_db, get_test_db

client = TestClient(app)


def setup_function():
    fresh_db()
    app.dependency_overrides[get_db] = get_test_db
    client.post("/users", json={"name": "Aida", "password": PASSWORD})


def teardown_function():
    app.dependency_overrides.clear()


def login(username: str, password: str):
    # OAuth2PasswordRequestForm reads a form, not JSON: data=, not json=
    form = {"username": username, "password": password}
    return client.post("/auth/token", data=form)


def test_login_gives_a_bearer_token():
    response = login("Aida", PASSWORD)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"].count(".") == 2


def test_token_has_sub_and_exp():
    token = login("Aida", PASSWORD).json()["access_token"]

    payload = jwt.decode(token, options={"verify_signature": False})   # no key needed to read it

    assert payload["sub"] == "Aida"
    assert 29 * 60 < payload["exp"] - time.time() <= 30 * 60


def test_wrong_password_returns_401():
    response = login("Aida", "kilc-chat-2025")

    assert response.status_code == 401
    assert response.json()["code"] == "bad_credentials"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_unknown_user_gets_the_same_answer():
    wrong_password = login("Aida", "kilc-chat-2025")
    unknown_user = login("Nobody", PASSWORD)

    assert unknown_user.status_code == 401
    assert unknown_user.json() == wrong_password.json()


def test_json_body_is_not_a_form():
    response = client.post("/auth/token", json={"username": "Aida", "password": PASSWORD})

    assert response.status_code == 422


def test_token_info_reads_the_token():
    token = login("Aida", PASSWORD).json()["access_token"]

    response = client.get("/auth/token-info", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["sub"] == "Aida"


def test_token_info_without_token_returns_401():
    response = client.get("/auth/token-info")

    assert response.status_code == 401


def test_changed_token_returns_401():
    token = login("Aida", PASSWORD).json()["access_token"]
    header, payload, signature = token.split(".")
    forged = jwt.encode({"sub": "Timur", "exp": 9999999999}, "a-guessed-key-that-is-long-enough-1234")
    fake = ".".join([header, forged.split(".")[1], signature])     # Timur's payload, Aida's signature

    response = client.get("/auth/token-info", headers={"Authorization": f"Bearer {fake}"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_expired_token_returns_401():
    token = create_access_token("Aida", minutes=-1)

    response = client.get("/auth/token-info", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"
