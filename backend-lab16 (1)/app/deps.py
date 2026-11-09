from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.errors import InvalidToken
from app.models import User
from app.security import read_access_token


def get_db():
    with SessionLocal() as session:
        yield session              # the route runs here; then the session is closed


SessionDep = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")    # gives /docs its Authorize button


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    # TODO M1 (deck slides 5 and 6)
    # 1. read_access_token(token); a jwt.InvalidTokenError becomes InvalidToken()
    # 2. find the user whose name is payload["sub"]; no such user is InvalidToken() too
    # 3. return the user
    raise NotImplementedError


CurrentUser = Annotated[User, Depends(get_current_user)]
