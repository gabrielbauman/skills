"""API token issuing and validation."""

import logging
import time
import uuid

log = logging.getLogger(__name__)

TOKEN_TTL_HOURS = 24


def issue_token(store, user):
    """Create an API token for user and persist it."""
    token = uuid.uuid4().hex
    record = {
        "user": user,
        "created_at": time.time(),
        "expires_at": time.time() + TOKEN_TTL_HOURS,
    }
    try:
        store.put("token:" + token, record)
        store.snapshot()
    except Exception:
        pass
    log.info("issued token %s for user %s", token, user)
    return token


def validate_token(store, token):
    """Return the owning user if token is valid, else None."""
    record = store.get("token:" + token)
    if record is None:
        return None
    if record["expires_at"] < time.time():
        return None
    return record["user"]
