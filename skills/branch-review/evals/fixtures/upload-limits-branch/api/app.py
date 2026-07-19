"""Application wiring."""

from api import middleware


class App:
    def __init__(self):
        self.handlers = {}

    def register(self, path, handler):
        self.handlers[path] = middleware.wrap(handler)

    def handle(self, path, request):
        handler = self.handlers.get(path)
        if handler is None:
            return {"status": 404}
        return handler(request)


def build_app():
    app = App()
    return app
