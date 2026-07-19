# Retries

Outbound HTTP calls are wrapped in `with_retries`, wich retries failed
calls with an exponentail backoff.

The delay betwen attempts grows each time. After too many failures the
last error is raised to the caller.
