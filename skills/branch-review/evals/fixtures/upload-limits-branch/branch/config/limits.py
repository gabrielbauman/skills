"""Upload limit configuration."""

import os

DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def max_upload_bytes():
    raw = os.environ.get("MAX_UPLOAD_BYTES", str(DEFAULT_MAX_UPLOAD_BYTES))
    try:
        return int(raw)
    except ValueError:
        return 0
