# Lab 16: Protected endpoints

Lab 15 gave every user a token, but no chat route asks for it: anyone can still post `{"author": "Timur", ...}` and change anyone's message. This repository starts from the lab 15 solution and puts the token to work. The server finds the user from the token, takes the author of a new message from it, and lets you change or delete only your own messages.

The deck is `backend-37-protected-endpoints` (PDF in the group chat).

If you are stuck for more than five minutes:

1. Read [Troubleshooting](#troubleshooting).
2. Open the deck slide that the TODO names.
3. Ask your neighbour.
4. Write down where you stopped in `REPORT.md`, and go on.

**In class: M1 in 12 minutes, M2 in 10, M3 in 10.** Commit after each milestone.

## Run it

macOS / Linux:

```bash
git clone https://github.com/kilc-po25/backend-lab16-YOUR-USERNAME.git
cd backend-lab16-YOUR-USERNAME
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev app/main.py
```

Windows PowerShell:

```powershell
git clone https://github.com/kilc-po25/backend-lab16-YOUR-USERNAME.git
cd backend-lab16-YOUR-USERNAME
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
fastapi dev app/main.py
```

No new packages this time.

`pytest` at the start: `22 failed, 43 passed, 10 errors`. The errors are the `NotImplementedError` of M1: some tests log in and pin a message before they start.

| File | Its job | Milestone |
|---|---|---|
| `app/deps.py` | `get_current_user` | M1 |
| `app/schemas.py`, `app/routers/messages.py` | `MessageIn` without `author`, `create_message` | M2 |
| `app/routers/messages.py` | `get_own_message` | M3 |
| `app/deps.py` | `oauth2_scheme`, `CurrentUser`: ready | do not change |
| `app/routers/users.py` | `GET /users/me`: ready, shows who the token belongs to | do not change |
| `app/errors.py`, `app/main.py` | `NotYourMessage` and its 403 handler: ready | do not change |
| `tests/`, `bruno/` | log in first, then send `Authorization: Bearer ...` | do not change |

## M1: from the token to the user (deck slides 5 and 6)

`get_current_user(token, session)` gets the token from the `Authorization` header: `oauth2_scheme` reads it for you and answers 401 when there is no header. Your part:

1. `read_access_token(token)`. If it raises `jwt.InvalidTokenError`, `raise InvalidToken()`.
2. Find the user whose `name` is `payload["sub"]`. No such user: `raise InvalidToken()` too.
3. Return the user.

Try it in `/docs`: **Authorize** as Aida, then `GET /users/me`.

`pytest`: `22 failed, 53 passed`.

## M2: the author comes from the token (deck slide 8)

Remove `author` from `MessageIn`. In `create_message` add a parameter `user: CurrentUser` and use it as the author. The lines that look the author up by name go away, and so does `UserNotFound` in this route.

`pytest`: `2 failed, 73 passed`.

## M3: only your own messages (deck slide 10)

`get_own_message` already finds the message (404 first). Add the check: if `message.user_id` is not `user.id`, `raise NotYourMessage(message_id)`. `patch_message` and `delete_message` already call it.

`pytest`: `75 passed`.

Stop the server, **delete `chat.db`**, start it, run the Bruno collection: 50 requests, all green. Requests 05 and 06 log in as Aida and Timur and save `token` and `token_timur`.

## Troubleshooting

| You see | Cause |
|---|---|
| 500 `NotImplementedError` | M1 is not finished: `get_current_user` still has `raise NotImplementedError` |
| `/users/me` answers 422 `int_parsing` | the route `/me` is below `/{user_id}`. Keep it above |
| an expired token gives 500 `ExpiredSignatureError` | `read_access_token` is not inside `try ... except jwt.InvalidTokenError` |
| a valid token gives 404 `user_not_found` | `session.get(User, payload["sub"])` looks up by id. `sub` is the name: `select(User).where(User.name == ...)` |
| POST a message answers 422 `loc: ["body", "author"]` | `MessageIn` still has `author` |
| Timur can edit Aida's message | `get_own_message` has no `user_id` check |
| deleting a missing message answers 403 | the owner check runs before `get_message_in_room`. 404 first, then 403 |
| Bruno request 01 answers 409 | `chat.db` still has the last run: delete it and restart the server |

## Hand in

Commit after each milestone, fill in `REPORT.md`, push. The last commit before the deadline is graded.
