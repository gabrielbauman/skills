"""Route registration."""

from app.router import Router


def build_router(store):
    router = Router()
    router.add_route("/health", lambda request: {"status": 200}, public=True)
    router.add_route("/profile", lambda request: {
        "status": 200,
        "body": {"user": request["user"]},
    })
    return router
