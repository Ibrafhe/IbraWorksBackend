from fastapi.testclient import TestClient

from app.deps import get_db
from app.main import app
from tests.db import PASSWORD, bearer, fresh_db, get_test_db

client = TestClient(app)
AIDA: dict = {}
TIMUR: dict = {}


def setup_function():
    # The same start as test_room_messages.py: messages 1, 2 and 4 in "general", 3 in "homework".
    fresh_db()
    app.dependency_overrides[get_db] = get_test_db
    for name in ["Aida", "Timur", "Dana"]:
        client.post("/users", json={"name": name, "password": PASSWORD})
    AIDA.update(bearer(client, "Aida"))
    TIMUR.update(bearer(client, "Timur"))
    client.post("/rooms", json={"title": "general"})
    client.post("/rooms", json={"title": "homework"})
    client.post("/rooms/1/messages", json={"text": "hello everyone"}, headers=AIDA)
    client.post("/rooms/1/messages", json={"text": "on my way"}, headers=TIMUR)
    client.post("/rooms/2/messages", json={"text": "lab 07 is done"}, headers=AIDA)
    client.post("/rooms/1/messages", json={"text": "where is the meeting?"}, headers=AIDA)
    client.patch("/rooms/1/messages/1", json={"pinned": True}, headers=AIDA)


def teardown_function():
    app.dependency_overrides.clear()


def ids(response) -> list[int]:
    return [message["id"] for message in response.json()]


# M1: GET /users/{user_id}/messages

def test_user_messages_newest_first():
    response = client.get("/users/1/messages")

    assert response.status_code == 200
    assert ids(response) == [4, 3, 1]
    assert response.json()[0]["author"] == {"id": 1, "name": "Aida"}


def test_user_without_messages_gets_empty_list():
    response = client.get("/users/3/messages")

    assert response.status_code == 200
    assert response.json() == []


def test_messages_of_unknown_user_returns_404():
    response = client.get("/users/99/messages")

    assert response.status_code == 404
    assert response.json()["code"] == "user_not_found"


# M2: DELETE /rooms/{room_id}

def test_delete_room_returns_204():
    response = client.delete("/rooms/2")

    assert response.status_code == 204
    assert client.get("/rooms/2").status_code == 404


def test_delete_room_deletes_its_messages():
    client.delete("/rooms/1")

    assert ids(client.get("/users/1/messages")) == [3]
    assert client.get("/rooms/1/messages").json()["code"] == "room_not_found"
    assert client.get("/rooms/2/messages/3").status_code == 200


def test_delete_unknown_room_returns_404():
    response = client.delete("/rooms/99")

    assert response.status_code == 404
    assert response.json()["code"] == "room_not_found"


# M3: GET /rooms/{room_id}/stats

def test_room_stats():
    response = client.get("/rooms/1/stats")

    assert response.status_code == 200
    assert response.json() == {
        "room_id": 1, "title": "general", "messages": 3, "pinned": 1,
        "by_author": {"Aida": 2, "Timur": 1},
    }


def test_stats_of_empty_room():
    client.post("/rooms", json={"title": "empty"})

    response = client.get("/rooms/3/stats")

    assert response.json() == {
        "room_id": 3, "title": "empty", "messages": 0, "pinned": 0, "by_author": {},
    }


def test_stats_of_unknown_room_returns_404():
    response = client.get("/rooms/99/stats")

    assert response.status_code == 404
    assert response.json()["code"] == "room_not_found"


# M4: /stats answers the same as before

def test_global_stats_after_delete():
    client.delete("/rooms/1")

    assert client.get("/stats").json() == {"users": 3, "rooms": 1, "messages": 1, "pinned": 0}
