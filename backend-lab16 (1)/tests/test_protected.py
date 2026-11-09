from fastapi.testclient import TestClient

from app.deps import get_db
from app.main import app
from app.security import create_access_token
from tests.db import PASSWORD, bearer, fresh_db, get_test_db

client = TestClient(app)
AIDA: dict = {}
TIMUR: dict = {}


def setup_function():
    # Aida wrote message 1, Timur wrote message 2, both in room 1.
    fresh_db()
    app.dependency_overrides[get_db] = get_test_db
    for name in ["Aida", "Timur"]:
        client.post("/users", json={"name": name, "password": PASSWORD})
    AIDA.update(bearer(client, "Aida"))
    TIMUR.update(bearer(client, "Timur"))
    client.post("/rooms", json={"title": "general"})
    client.post("/rooms/1/messages", json={"text": "hello everyone"}, headers=AIDA)
    client.post("/rooms/1/messages", json={"text": "on my way"}, headers=TIMUR)


def teardown_function():
    app.dependency_overrides.clear()


# M1: get_current_user, seen through GET /users/me

def test_me_with_a_token():
    response = client.get("/users/me", headers=AIDA)

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Aida"}


def test_me_without_a_token_returns_401():
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_me_with_an_expired_token_returns_401():
    token = create_access_token("Aida", minutes=-1)

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


def test_token_of_an_unknown_user_returns_401():
    token = create_access_token("Nobody")          # signed with our key, but no such user

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


# M2: the author comes from the token

def test_author_is_the_token_owner():
    response = client.post("/rooms/1/messages", json={"text": "hi"}, headers=TIMUR)

    assert response.status_code == 201
    assert response.json()["author"] == {"id": 2, "name": "Timur"}


def test_body_cannot_choose_the_author():
    body = {"author": "Aida", "text": "I am Aida, honestly"}

    response = client.post("/rooms/1/messages", json=body, headers=TIMUR)

    assert response.json()["author"]["name"] == "Timur"


# M3: only your own messages

def test_edit_own_message():
    response = client.patch("/rooms/1/messages/1", json={"text": "hello all"}, headers=AIDA)

    assert response.status_code == 200
    assert response.json()["text"] == "hello all"


def test_edit_someone_elses_message_returns_403():
    response = client.patch("/rooms/1/messages/1", json={"text": "hacked"}, headers=TIMUR)

    assert response.status_code == 403
    assert response.json()["code"] == "not_your_message"
    assert client.get("/rooms/1/messages/1").json()["text"] == "hello everyone"


def test_delete_someone_elses_message_returns_403():
    response = client.delete("/rooms/1/messages/1", headers=TIMUR)

    assert response.status_code == 403
    assert client.get("/rooms/1/messages/1").status_code == 200


def test_delete_own_message_returns_204():
    response = client.delete("/rooms/1/messages/2", headers=TIMUR)

    assert response.status_code == 204


def test_unknown_message_is_404_not_403():
    response = client.delete("/rooms/1/messages/99", headers=TIMUR)

    assert response.status_code == 404
    assert response.json()["code"] == "message_not_found"


def test_edit_without_a_token_returns_401():
    response = client.patch("/rooms/1/messages/1", json={"text": "hacked"})

    assert response.status_code == 401
