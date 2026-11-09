from typing import Annotated, Literal

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.deps import CurrentUser, SessionDep
from app.errors import ChatFull, MessageNotFound, NotYourMessage, RoomNotFound, UserNotFound
from app.models import Message, Room, User
from app.schemas import MessageIn, MessageOut, MessagePatch

MAX_MESSAGES = 100          # in one room

router = APIRouter(prefix="/rooms/{room_id}/messages", tags=["messages"])


def get_room_or_404(session, room_id: int) -> Room:
    room = session.get(Room, room_id)
    if room is None:
        raise RoomNotFound(room_id)
    return room


def get_message_in_room(session, room_id: int, message_id: int) -> Message:
    get_room_or_404(session, room_id)
    message = session.get(Message, message_id)
    if message is None or message.room_id != room_id:
        raise MessageNotFound(message_id)
    return message


def get_own_message(session, room_id: int, message_id: int, user: User) -> Message:
    message = get_message_in_room(session, room_id, message_id)     # 404 first
    # TODO M3 (deck slide 10): raise NotYourMessage(message_id) if it is not the user's message (403)
    return message


@router.get("", response_model=list[MessageOut])
def list_messages(
    room_id: int,
    session: SessionDep,
    author: str | None = None,
    pinned: bool | None = None,
    q: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
    order: Literal["asc", "desc"] = "asc",
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    get_room_or_404(session, room_id)
    stmt = select(Message).where(Message.room_id == room_id)
    if author is not None:
        stmt = stmt.join(Message.author).where(User.name == author)
    if pinned is not None:
        stmt = stmt.where(Message.pinned == pinned)
    if q is not None:
        stmt = stmt.where(Message.text.icontains(q))
    if order == "desc":
        stmt = stmt.order_by(Message.id.desc())
    else:
        stmt = stmt.order_by(Message.id)
    stmt = stmt.limit(limit).offset(offset)
    return session.scalars(stmt).all()


@router.post("", response_model=MessageOut, status_code=201)
def create_message(room_id: int, payload: MessageIn, session: SessionDep):
    # TODO M2 (deck slide 8): add user: CurrentUser and make it the author
    room = get_room_or_404(session, room_id)
    user = session.scalar(select(User).where(User.name == payload.author))
    if user is None:
        raise UserNotFound(payload.author)
    if len(room.messages) >= MAX_MESSAGES:
        raise ChatFull(MAX_MESSAGES)
    message = Message(room=room, author=user, text=payload.text)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@router.get("/{message_id}", response_model=MessageOut)
def get_message(room_id: int, message_id: int, session: SessionDep):
    return get_message_in_room(session, room_id, message_id)


@router.patch("/{message_id}", response_model=MessageOut)
def patch_message(
    room_id: int, message_id: int, payload: MessagePatch, session: SessionDep, user: CurrentUser
):
    message = get_own_message(session, room_id, message_id, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(message, field, value)
    session.commit()
    session.refresh(message)
    return message


@router.delete("/{message_id}", status_code=204)
def delete_message(room_id: int, message_id: int, session: SessionDep, user: CurrentUser) -> None:
    message = get_own_message(session, room_id, message_id, user)
    session.delete(message)
    session.commit()
