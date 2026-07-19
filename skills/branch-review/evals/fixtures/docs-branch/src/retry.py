"""Retry helper for outbound HTTP calls."""

import time

INITIAL_DELAY = 0.5
MAX_DELAY = 60.0
MAX_ATTEMPTS = 5

RETRYABLE = (ConnectionError, TimeoutError)


def with_retries(fn, *args, **kwargs):
    """Call fn, retrying transient network failures with backoff.

    Only ConnectionError and TimeoutError are retried; any other
    exception propagates immediately. The delay starts at INITIAL_DELAY
    seconds and doubles per attempt, capped at MAX_DELAY.
    """
    delay = INITIAL_DELAY
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fn(*args, **kwargs)
        except RETRYABLE:
            if attempt == MAX_ATTEMPTS:
                raise
            time.sleep(delay)
            delay = min(delay * 2, MAX_DELAY)
