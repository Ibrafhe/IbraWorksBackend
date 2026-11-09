from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.deps import CurrentUser, SessionDep
from app.errors import UserExists, UserNotFound
from app.models import Message, User
from app.schemas import MessageOut, UserIn, UserOut
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(session: SessionDep):
    return session.scalars(select(User).order_by(User.id)).all()


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserIn, session: SessionDep):
    user = User(name=payload.name, password_hash=hash_password(payload.password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError:          # UNIQUE constraint failed: users.name
        session.rollback()
        raise UserExists(payload.name)
    session.refresh(user)
    return user


@router.get("/me", response_model=UserOut)       # before /{user_id}, or "me" is read as an id
def read_me(user: CurrentUser):
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        raise UserNotFound(user_id)
    return user


@router.get("/{user_id}/messages", response_model=list[MessageOut])
def list_user_messages(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        raise UserNotFound(user_id)
    stmt = select(Message).where(Message.user_id == user_id).order_by(Message.id.desc())
    return session.scalars(stmt).all()
