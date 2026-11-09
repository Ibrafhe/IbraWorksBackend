import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Message, Room, User
from tests.db import TestSession, fresh_db

FAKE_HASH = "$argon2id$not-a-real-hash"     # the model tests do not hash


def setup_function():
    fresh_db()


def test_tables_have_the_right_names():
    assert User.__tablename__ == "users"
    assert Room.__tablename__ == "rooms"


def test_add_and_commit_gives_an_id():
    with TestSession() as session:
        room = Room(title="general")
        session.add(room)
        session.commit()

        assert room.id == 1


def test_get_returns_the_object_or_none():
    with TestSession() as session:
        session.add(Room(title="general"))
        session.commit()

        assert session.get(Room, 1).title == "general"
        assert session.get(Room, 99) is None


def test_select_in_id_order():
    with TestSession() as session:
        session.add_all([Room(title="general"), Room(title="homework")])
        session.commit()

        rooms = session.scalars(select(Room).order_by(Room.id)).all()

        assert [room.title for room in rooms] == ["general", "homework"]


def test_user_name_is_unique():
    with TestSession() as session:
        session.add(User(name="Aida", password_hash=FAKE_HASH))
        session.commit()
        session.add(User(name="Aida", password_hash=FAKE_HASH))

        with pytest.raises(IntegrityError):
            session.commit()


def add_chat(session):
    aida, timur = User(name="Aida", password_hash=FAKE_HASH), User(name="Timur", password_hash=FAKE_HASH)
    general, homework = Room(title="general"), Room(title="homework")
    session.add_all([aida, timur, general, homework])
    session.commit()
    session.add_all([
        Message(room=general, author=aida, text="hello everyone"),
        Message(room=general, author=timur, text="on my way"),
        Message(room=homework, author=aida, text="lab 07 is done"),
    ])
    session.commit()


def test_message_has_foreign_keys():
    with TestSession() as session:
        add_chat(session)
        message = session.get(Message, 3)

        assert Message.__tablename__ == "messages"
        assert (message.room_id, message.user_id) == (2, 1)
        assert message.pinned is False


def test_message_knows_its_room_and_author():
    with TestSession() as session:
        add_chat(session)
        message = session.get(Message, 2)

        assert message.room.title == "general"
        assert message.author.name == "Timur"


def test_room_and_user_know_their_messages():
    with TestSession() as session:
        add_chat(session)

        assert [m.id for m in session.get(Room, 1).messages] == [1, 2]
        assert [m.id for m in session.get(User, 1).messages] == [1, 3]


def test_back_populates_fills_the_other_side():
    with TestSession() as session:
        room, user = Room(title="general"), User(name="Dana", password_hash=FAKE_HASH)
        message = Message(room=room, author=user, text="hi")

        assert room.messages == [message]
        assert user.messages == [message]
