from fastapi import APIRouter
from sqlalchemy import func, select

from app.deps import SessionDep
from app.models import Message, Room, User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats(session: SessionDep) -> dict:
    # SELECT count(...) in the database: no rows are loaded into Python
    return {
        "users": session.scalar(select(func.count(User.id))),
        "rooms": session.scalar(select(func.count(Room.id))),
        "messages": session.scalar(select(func.count(Message.id))),
        "pinned": session.scalar(select(func.count(Message.id)).where(Message.pinned)),
    }
