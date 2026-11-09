from fastapi.testclient import TestClient

from app.deps import get_db
from app.main import app
from app.routers.messages import MAX_MESSAGES
from tests.db import PASSWORD, bearer, fresh_db, get_test_db

client = TestClient(app)
AIDA: dict = {}
TIMUR: dict = {}
DANA: dict = {}


def setup_function():
    # Three users, two rooms, four messages: 1, 2 and 4 in room 1 ("general"), 3 in room 2 ("homework").
    fresh_db()
    app.dependency_overrides[get_db] = get_test_db
    for name in ["Aida", "Timur", "Dana"]:
        client.post("/users", json={"name": name, "password": PASSWORD})
    AIDA.update(bearer(client, "Aida"))
    TIMUR.update(bearer(client, "Timur"))
    DANA.update(bearer(client, "Dana"))
    client.post("/rooms", json={"title": "general"})
    client.post("/rooms", json={"title": "homework"})
    client.post("/rooms/1/messages", json={"text": "hello everyone"}, headers=AIDA)
    client.post("/rooms/1/messages", json={"text": "on my way"}, headers=TIMUR)
    client.post("/rooms/2/messages", json={"text": "lab 07 is done"}, headers=AIDA)
    client.post("/rooms/1/messages", json={"text": "where is the meeting?"}, headers=AIDA)


def teardown_function():
    app.dependency_overrides.clear()


def ids(response) -> list[int]:
    return [message["id"] for message in response.json()]


def test_create_message_shows_the_author():
    response = client.post("/rooms/2/messages", json={"text": "  me too  "}, headers=DANA)

    assert response.status_code == 201
    assert response.json() == {
        "id": 5, "room_id": 2, "text": "me too", "pinned": False,
        "author": {"id": 3, "name": "Dana"},
    }


def test_message_without_token_returns_401():
    response = client.post("/rooms/1/messages", json={"text": "hello"})

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_message_into_unknown_room_returns_404():
    response = client.post("/rooms/99/messages", json={"text": "hello"}, headers=AIDA)

    assert response.status_code == 404
    assert response.json()["code"] == "room_not_found"


def test_list_shows_only_this_room():
    response = client.get("/rooms/1/messages")

    assert response.status_code == 200
    assert ids(response) == [1, 2, 4]
    assert response.json()[1]["author"] == {"id": 2, "name": "Timur"}


def test_list_of_unknown_room_returns_404():
    response = client.get("/rooms/99/messages")

    assert response.status_code == 404
    assert response.json()["code"] == "room_not_found"


def test_filter_and_order_inside_a_room():
    response = client.get("/rooms/1/messages", params={"author": "Aida", "order": "desc"})

    assert ids(response) == [4, 1]


def test_search_ignores_case():
    response = client.get("/rooms/1/messages", params={"q": "MEETING"})

    assert ids(response) == [4]


def test_second_page_inside_a_room():
    response = client.get("/rooms/1/messages", params={"limit": 2, "offset": 2})

    assert ids(response) == [4]


def test_limit_zero_returns_422():
    response = client.get("/rooms/1/messages", params={"limit": 0})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "limit"]


def test_get_message_from_its_room():
    response = client.get("/rooms/2/messages/3")

    assert response.status_code == 200
    assert response.json()["text"] == "lab 07 is done"


def test_message_from_the_wrong_room_returns_404():
    response = client.get("/rooms/1/messages/3")

    assert response.status_code == 404
    assert response.json()["code"] == "message_not_found"


def test_pin_message():
    response = client.patch("/rooms/1/messages/1", json={"pinned": True}, headers=AIDA)

    assert response.status_code == 200
    assert response.json()["pinned"] is True
    assert client.get("/rooms/1/messages/1").json()["pinned"] is True


def test_delete_returns_204_then_404():
    first = client.delete("/rooms/2/messages/3", headers=AIDA)
    second = client.delete("/rooms/2/messages/3", headers=AIDA)

    assert first.status_code == 204
    assert second.status_code == 404
    assert second.json()["code"] == "message_not_found"


def test_full_room_returns_409():
    for n in range(MAX_MESSAGES - 1):           # room 2 already has one message
        client.post("/rooms/2/messages", json={"text": f"message {n}"}, headers=AIDA)

    response = client.post("/rooms/2/messages", json={"text": "one more"}, headers=AIDA)
    other_room = client.post("/rooms/1/messages", json={"text": "still fine"}, headers=AIDA)

    assert response.status_code == 409
    assert response.json()["code"] == "chat_full"
    assert other_room.status_code == 201


def test_stats_counts_everything():
    client.patch("/rooms/1/messages/4", json={"pinned": True}, headers=AIDA)

    response = client.get("/stats")

    assert response.json() == {"users": 3, "rooms": 2, "messages": 4, "pinned": 1}
