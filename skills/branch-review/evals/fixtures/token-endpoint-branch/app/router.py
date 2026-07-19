"""Tiny route table with auth-by-default registration."""

from app import auth


class Router:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, handler, public=False):
        """Register a handler.

        Handlers are wrapped with session authentication unless
        explicitly registered public; see SECURITY.md.
        """
        if not public:
            handler = auth.require_session(handler)
        self.routes[path] = handler

    def dispatch(self, path, request):
        handler = self.routes.get(path)
        if handler is None:
            return {"status": 404}
        return handler(request)
