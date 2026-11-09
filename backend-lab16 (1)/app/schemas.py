from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserIn(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=32)]
    password: Annotated[str, Field(min_length=8, max_length=128)]


class UserOut(BaseModel):              # no password and no password_hash: they never leave the server
    id: int
    name: str


class RoomIn(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=50)]

    @field_validator("title")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be only spaces")
        return v.strip()


class RoomOut(BaseModel):
    id: int
    title: str


class MessageIn(BaseModel):
    author: Annotated[str, Field(min_length=2, max_length=32)]     # TODO M2: the author comes from the token
    text: Annotated[str, Field(min_length=1, max_length=500)]

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text cannot be only spaces")
        return v.strip()


class MessagePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: Annotated[str, Field(min_length=1, max_length=500)] | None = None
    pinned: bool | None = None

    @field_validator("text", "pinned")
    @classmethod
    def not_null(cls, v):
        if v is None:
            raise ValueError("may be left out, but not null")
        return v


class MessageOut(BaseModel):
    id: int
    room_id: int
    text: str
    pinned: bool
    author: UserOut              # a nested schema: the user, not only user_id


class Token(BaseModel):
    access_token: str
    token_type: str
