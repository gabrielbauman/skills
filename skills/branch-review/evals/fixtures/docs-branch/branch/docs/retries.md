# Retries

Outbound HTTP calls are wrapped in `with_retries`, which retries any
failed call with exponential backoff.

The delay between attempts starts at 0.5 seconds and doubles on each
retry, capped at 30 seconds. Up to five attempts are made; after the
fifth failure the last error is raised to the caller.
