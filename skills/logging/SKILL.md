---
name: logging
description: "Write logs an operator can act on: pick the level to match who reads it and what they must do, log structured key-value fields instead of interpolated strings so the logs are queryable, and record the context needed to act instead of a bare failed. Use whenever adding or reviewing logging, instrumenting code for observability, choosing a log level, deciding what to log on an error path, or cleaning up noisy or unqueryable logs. Covers matching level to reader and action (ERROR someone must act, WARN suspicious but handled, INFO milestone, DEBUG diagnostic), structured over string-concatenated messages, logging ids and inputs and what was attempted, never logging secrets credentials tokens or PII, logging at boundaries and state transitions rather than every line, and not log-and-rethrowing the same error at every layer. Pairs with error-handling for the log-vs-swallow decision and not double-logging a rethrown error, debugging where the logs are the trail you follow to the failure, and why-comments for what goes in a comment (the why, for the reader) versus a log (the context, for the operator)."
---

# Logging

The failure mode is the log that is there but useless. Every function
announces its own entry and exit at INFO, so the one line that mattered is
buried under ten thousand that did not, and nobody reads the file until an
outage forces them to grep it in a panic. When they do grep it, the message
is `f"failed to process {user}"` with no id they can pivot on, no reason, no
record of what was attempted. The log recorded that something happened; it
did not record enough to act.

Good logging is written for the person who reads it during an incident, at
3am, who did not see the code run and cannot ask it questions. Every line
should earn its place by helping that person decide what to do next.

## Match the level to the reader and the action

A log level is a promise about who should care and how urgently. When every
line is INFO, the level carries no information and the reader has to read the
message to triage, which defeats the point. When everything an error path
touches is logged at ERROR, real errors drown in handled ones and the
on-call alert that fires on ERROR becomes noise people mute.

- **ERROR**: something broke and a human has to act. A failed payment write,
  a config that would not load, an unhandled exception at the top boundary.
  If an alert should fire, it is ERROR. If no one needs to do anything, it is
  not.
- **WARN**: suspicious but the code handled it. A retry that succeeded on the
  second try, a deprecated field still in use, a fallback that kicked in.
  Worth noticing in aggregate, not worth waking anyone.
- **INFO**: a milestone in normal operation. Service started, a job
  finished, an order was placed. Sparse enough that reading INFO tells the
  story of what the system did, not how it did it.
- **DEBUG**: diagnostic detail for someone working the problem. The query
  that ran, the branch taken, the intermediate value. Off in production by
  default; on when you are hunting.

The test for a level is what the reader does with it, not how bad the code
felt when it wrote the line. "Cache miss, recomputing" is normal operation,
so it is DEBUG or nothing, never WARN, no matter that it sits in a `catch`.

## Prefer structured fields over interpolated strings

A message built by string interpolation is a sentence; you can read one, but
you cannot query a million. `log.info(f"user {uid} bought {sku} for {cents}")`
forces the operator to write a regex to answer "how many orders over $500,"
and the regex breaks the day someone reorders the words. Pass the values as
fields and the log store indexes them.

```python
# Bad: the ids are welded into prose, queryable only by regex.
log.info(f"order {order_id} for user {user_id} failed after {n} retries")
```

```python
# Good: fields you can filter, group, and alert on.
log.error("order failed", order_id=order_id, user_id=user_id, retries=n)
```

Now "all failed orders for user 42" is a field filter, and "p99 retries
before failure" is a query, not a parsing project. Keep the message a short,
stable string that names the event; put everything that varies in fields. A
stable message string also means the same event has one identity across
millions of lines, so you can count it. If the codebase logs plain strings
and has no structured backend, follow its convention, but still lead with a
fixed prefix and append `key=value` pairs rather than burying ids mid-sentence.

## Log the context needed to act, not "failed"

`log.error("save failed")` tells the reader a save failed and nothing they
can use. Which save? For whom? With what input? What was the underlying
error? A log line on an error path should carry enough to reproduce or locate
the problem without reading the code around it: the ids, the inputs, what was
attempted, and the cause.

```python
# Bad: true, and useless.
log.error("failed to update subscription")
```

```python
# Good: the operator can find the row, the plan, and the real error.
log.error(
    "subscription update failed",
    user_id=user_id,
    plan=new_plan,
    reason=str(err),
)
```

This is the same information an exception message should carry (see
error-handling), for the same reason: the reader did not see it run. Log the
attempt, not just the outcome. A line that says what the code was trying to
do when it failed turns a mystery into a lookup.

## Never log secrets or PII

A log file is read by more people than the request was, lives longer than the
request did, and gets shipped to a third-party aggregator you do not control.
Anything you log, assume it is stored forever and visible to everyone with
log access. That rules out passwords, tokens, API keys, session cookies, full
card numbers, and government ids, and it constrains PII: emails, names, and
addresses go in logs only when you have a reason and a retention story, never
by reflex.

```python
# Bad: the token and the full body land in the log, forever.
log.info("auth request", headers=request.headers, body=request.json)
```

```python
# Good: log the shape, not the secret.
log.info("auth request", user_id=user_id, scopes=scopes, has_token=bool(token))
```

The trap is logging a whole object (a request, a user record, a config) and
not noticing it carries a secret field. Log the specific fields you need, not
the container. When you must correlate on something sensitive, log a hash or
the last four digits, not the value.

## Log at boundaries and transitions, not every line

Volume is the enemy of signal. A log per line turns the file into a slow
re-run of the source that no one can read and that costs real money to store
and index. Log where the system crosses a boundary or changes state, because
those are the points an operator reconstructs an incident from:

- Requests in and out at a service edge (one line each, with a correlation
  id, latency, and status).
- Calls to an external dependency: the database, the payment gateway, the
  queue, especially the failures and the retries.
- State transitions that matter: a job moved to `running`, an account was
  suspended, a feature flag flipped.
- Startup and shutdown, with the config that decides behaviour (minus the
  secrets).

Inside a function, the branch you took and the loop counter are DEBUG at
most, usually nothing. If you find yourself logging to confirm the code
reached line 40, that is a debugger's job or a temporary probe, not a line to
commit.

## Do not log and rethrow at every layer

The counterpart to swallowing an error is logging it five times. Each layer
catches, logs "something failed," and rethrows, so one failure produces a
stack of near-identical ERROR lines that look like five problems and bury the
one real stack trace. Pick one place to log an error: the boundary that
finally handles it (see error-handling's "catch where you can act"). Below
that boundary, add context to the exception and let it propagate unlogged.

```python
# Bad: three layers, three log lines, one actual failure.
def charge(order):
    try:
        gateway.charge(order)
    except GatewayError as e:
        log.error("charge failed", order_id=order.id)  # logged here
        raise

def place_order(order):
    try:
        charge(order)
    except GatewayError as e:
        log.error("place_order failed", order_id=order.id)  # and again
        raise
```

```python
# Good: lower layers stay quiet; the handler logs once, with the whole story.
def charge(order):
    gateway.charge(order)  # raises; caller decides

def place_order(order):
    charge(order)  # propagates

@app.post("/orders")
def create_order():
    try:
        place_order(build_order(request.json))
    except GatewayError as e:
        log.error("order failed", order_id=order.id, reason=str(e))
        return Response("Payment could not be processed", status=502)
```

One error, one log line, the full trace intact. If a middle layer has context
the boundary will not (a value that is out of scope higher up), attach it to
the exception rather than logging a second line for it.

## Logs are for operators, comments are for readers

A log line and a comment answer different questions for different people. The
comment explains to the next person editing the code why it does something
non-obvious; it is read at the source (see why-comments). The log explains to
the operator watching the system what it did and with what data; it is read
in production, detached from the code. Do not swap them. A comment that says
"log this for the metrics dashboard" is fine; a log line that exists to
explain the algorithm to a future maintainer is noise in the output and
belongs in a comment or a better function name instead.
