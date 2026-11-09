from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]                       # never the password itself

    messages: Mapped[list["Message"]] = relationship(back_populates="author")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

    messages: Mapped[list["Message"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"    # the room goes, its messages go too
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str]
    pinned: Mapped[bool] = mapped_column(default=False)

    room: Mapped["Room"] = relationship(back_populates="messages")
    author: Mapped["User"] = relationship(back_populates="messages")
