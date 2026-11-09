from app.security import hash_password, verify_password


def test_hash_is_argon2_and_not_the_password():
    hashed = hash_password("kilc-chat-2026")

    assert hashed.startswith("$argon2id$")
    assert "kilc-chat-2026" not in hashed


def test_verify_accepts_the_right_password():
    hashed = hash_password("kilc-chat-2026")

    assert verify_password("kilc-chat-2026", hashed) is True


def test_verify_rejects_a_wrong_password():
    hashed = hash_password("kilc-chat-2026")

    assert verify_password("kilc-chat-2025", hashed) is False
