"""Session lookup."""

SESSIONS = {}


def authenticate(request):
    session = SESSIONS.get(request.get("session_id"))
    if session is None:
        return None
    return session["user"]
