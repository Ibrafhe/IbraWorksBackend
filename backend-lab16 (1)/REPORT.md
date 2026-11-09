# Report, lab 16

Fill this in as you go. Write in your own words.

**Name:**
**Group:**
**Date:**

## What works

Tick only what works. "Almost works" is not ticked.

- [ ] M1: `get_current_user`, `GET /users/me` shows who I am
- [ ] M2: the author of a new message comes from the token
- [ ] M3: changing or deleting someone else's message answers 403
- [ ] Bruno: ___ of 50 green
- [ ] `pytest`: ___ passed, ___ failed

## 401 or 403

Fill in the status code the server answers, and say in one sentence why.

| Request | Status | Why |
|---|---|---|
| `PATCH /rooms/1/messages/1` with no `Authorization` header | | |
| the same with an expired token | | |
| the same with Timur's token, message 1 is Aida's | | |
| `DELETE /rooms/1/messages/99` with Timur's token | | |

## The body cannot choose the author

Send `{"author": "Aida", "text": "hi"}` with Timur's token. Who is the author in the answer? Why does the `author` field in the body change nothing?

## Where I got stuck

The one error that took the longest. What the console or pytest said, and what the cause turned out to be. If you did not finish, write where you stopped.


## Sources
