from app.models import User
from app.routers.auth import authenticate_user
from app.security import hash_password
from tests.db import PASSWORD, TestSession, fresh_db


def setup_function():
    fresh_db()
    with TestSession() as session:
        session.add(User(name="Aida", password_hash=hash_password(PASSWORD)))
        session.commit()


def test_right_password_gives_the_user():
    with TestSession() as session:
        user = authenticate_user(session, "Aida", PASSWORD)

        assert user is not None
        assert user.name == "Aida"


def test_wrong_password_gives_none():
    with TestSession() as session:
        assert authenticate_user(session, "Aida", "kilc-chat-2025") is None


def test_unknown_name_gives_none():
    with TestSession() as session:
        assert authenticate_user(session, "Nobody", PASSWORD) is None
