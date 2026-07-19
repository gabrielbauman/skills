"""Request middleware applied to every registered handler."""

from api import sessions


def wrap(handler):
    """Authenticate, then dispatch.

    Applied by App.register to every handler; see SECURITY.md
    ("All endpoints authenticate").
    """
    def wrapped(request):
        user = sessions.authenticate(request)
        if user is None:
            return {"status": 401}
        request["user"] = user
        return handler(request)
    return wrapped
