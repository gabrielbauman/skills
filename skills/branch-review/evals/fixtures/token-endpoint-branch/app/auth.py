"""Session authentication."""

SESSIONS = {}


def require_session(handler):
    def wrapped(request):
        session = SESSIONS.get(request.get("session_id"))
        if session is None:
            return {"status": 401}
        request["user"] = session["user"]
        return handler(request)
    return wrapped
