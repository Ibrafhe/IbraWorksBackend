class UserNotFound(Exception):
    def __init__(self, user: int | str) -> None:     # an id, or a name from MessageIn
        self.user = user


class UserExists(Exception):
    def __init__(self, name: str) -> None:
        self.name = name


class RoomNotFound(Exception):
    def __init__(self, room_id: int) -> None:
        self.room_id = room_id


class MessageNotFound(Exception):
    def __init__(self, message_id: int) -> None:
        self.message_id = message_id


class ChatFull(Exception):
    def __init__(self, limit: int) -> None:
        self.limit = limit


class BadCredentials(Exception):      # one error for "no such user" and "wrong password"
    pass


class InvalidToken(Exception):
    pass


class NotYourMessage(Exception):     # the message exists, but it belongs to someone else
    def __init__(self, message_id: int) -> None:
        self.message_id = message_id
