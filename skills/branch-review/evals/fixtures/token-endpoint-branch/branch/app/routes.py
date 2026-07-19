"""Route registration."""

from app.router import Router
from app import tokens


def build_router(store):
    router = Router()
    router.add_route("/health", lambda request: {"status": 200}, public=True)
    router.add_route("/profile", lambda request: {
        "status": 200,
        "body": {"user": request["user"]},
    })
    router.add_route("/tokens", lambda request: {
        "status": 201,
        "body": {"token": tokens.issue_token(store, request["user"])},
    })
    return router
