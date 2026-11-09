import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()      # Argon2id, with its own random salt for every hash

# The key that signs tokens. In production it comes from the environment and is long and random.
SECRET_KEY = os.getenv(
    "SECRET_KEY", "dev-only-secret-change-me-0123456789abcdef"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


# Ready-made helpers: use them, you do not need to change them.

def create_access_token(
    sub: str, minutes: int = ACCESS_TOKEN_MINUTES
) -> str:
    """A signed JWT: who it is (sub) and when it stops working (exp)."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def read_access_token(token: str) -> dict:
    """The payload of a valid token. Raises jwt.InvalidTokenError if the signature or exp is wrong."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
