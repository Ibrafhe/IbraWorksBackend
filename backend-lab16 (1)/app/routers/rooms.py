from fastapi import APIRouter
from sqlalchemy import func, select

from app.deps import SessionDep
from app.errors import RoomNotFound
from app.models import Message, Room, User
from app.schemas import RoomIn, RoomOut

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomOut])
def list_rooms(session: SessionDep):
    return session.scalars(select(Room).order_by(Room.id)).all()


@router.post("", response_model=RoomOut, status_code=201)
def create_room(payload: RoomIn, session: SessionDep):
    room = Room(title=payload.title)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, session: SessionDep):
    room = session.get(Room, room_id)
    if room is None:
        raise RoomNotFound(room_id)
    return room


@router.delete("/{room_id}", status_code=204)
def delete_room(room_id: int, session: SessionDep) -> None:
    room = session.get(Room, room_id)
    if room is None:
        raise RoomNotFound(room_id)
    session.delete(room)            # with cascade on Room.messages, its messages are deleted too
    session.commit()


@router.get("/{room_id}/stats")
def room_stats(room_id: int, session: SessionDep) -> dict:
    room = session.get(Room, room_id)
    if room is None:
        raise RoomNotFound(room_id)
    count = select(func.count(Message.id)).where(Message.room_id == room_id)
    by_author = (
        select(User.name, func.count(Message.id))
        .join(Message.author)
        .where(Message.room_id == room_id)
        .group_by(User.name)
        .order_by(User.name)
    )
    return {
        "room_id": room.id,
        "title": room.title,
        "messages": session.scalar(count),
        "pinned": session.scalar(count.where(Message.pinned)),
        "by_author": {name: n for name, n in session.execute(by_author)},
    }
