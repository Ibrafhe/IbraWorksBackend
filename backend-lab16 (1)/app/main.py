from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.errors import (
    BadCredentials, ChatFull, InvalidToken, MessageNotFound, NotYourMessage, RoomNotFound, UserExists,
    UserNotFound,
)
from app.routers import auth, messages, rooms, stats, users

Base.metadata.create_all(engine)      # CREATE TABLE for every model, if the table is not there yet

app = FastAPI(title="Chat API")
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(messages.router)
app.include_router(stats.router)
app.include_router(auth.router)


@app.exception_handler(UserNotFound)
def user_not_found(request: Request, exc: UserNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": f"User {exc.user} not found", "code": "user_not_found"},
    )


@app.exception_handler(UserExists)
def user_exists(request: Request, exc: UserExists) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": f"The name {exc.name} is taken", "code": "user_exists"},
    )


@app.exception_handler(RoomNotFound)
def room_not_found(request: Request, exc: RoomNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": f"Room {exc.room_id} not found", "code": "room_not_found"},
    )


@app.exception_handler(MessageNotFound)
def message_not_found(request: Request, exc: MessageNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": f"Message {exc.message_id} not found", "code": "message_not_found"},
    )


@app.exception_handler(ChatFull)
def chat_full(request: Request, exc: ChatFull) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": f"Chat is full ({exc.limit} messages)", "code": "chat_full"},
    )


@app.exception_handler(BadCredentials)
def bad_credentials(request: Request, exc: BadCredentials) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Incorrect username or password", "code": "bad_credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(InvalidToken)
def invalid_token(request: Request, exc: InvalidToken) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid or expired token", "code": "invalid_token"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(NotYourMessage)
def not_your_message(request: Request, exc: NotYourMessage) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"detail": f"Message {exc.message_id} belongs to another user", "code": "not_your_message"},
    )


# Debug in the IDE, or: python -m app.main
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
