---
name: error-handling
description: "Handle errors so failures are loud, actionable, and traceable instead of swallowed: fail early rather than limp on with bad state, attach the underlying cause, name what was attempted and with which inputs, catch at the boundary that can act, choose deliberately between retry, propagate, and crash, and never leak secrets or internals to users. Use whenever writing or reviewing code that can fail: catch/except blocks, error messages, retries, deciding what to do with a returned error, or cleaning up code that hides failures. Pairs with logging (report a caught error once, at the boundary that acts) and secure-coding (fail closed at the trust boundary)."
---

# Error-handling

The failure mode is the empty catch block. Something throws, the code
catches it, does nothing, and execution continues as if the call
succeeded. The program limps forward on state that was never built,
crashes ten frames later with a `None` that means nothing, and the
original error, the one that said what actually went wrong, is gone. The
close cousins: a catch-all that flattens every failure to "an error
occurred", a rethrow that drops the cause, and a `try` wrapped around two
hundred lines so nobody can tell which one was expected to fail.

Good error handling makes failures loud, specific, and traceable to their
cause. The rules below are about not destroying information on the way up.

## Fail loud and early

A function handed input it cannot process should stop there, not sanitize
it into something plausible and continue. The bad value caught at the door
names the caller that sent it; the same value caught six calls deeper
names nothing.

```python
# Bad: unknown currency silently becomes 0, and a real order ships wrong.
def to_cents(amount, currency):
    rate = RATES.get(currency, 0)
    return int(amount * rate * 100)
```

```python
# Good: the failure points at the caller that passed the bad currency.
def to_cents(amount, currency):
    if currency not in RATES:
        raise ValueError(f"no exchange rate for currency {currency!r}")
    return int(amount * RATES[currency] * 100)
```

Corrupt or impossible state is a reason to halt the operation, not to
paper over it and let the damage spread. A crash at the point of
corruption is a bug report; a wrong answer with no crash is a support
ticket six months later that no one can trace.

## Never swallow an error silently

Catching an exception and discarding it is a decision to hide a failure.
If it can truly be ignored, that is a claim worth writing down, with the
reason, so the next reader knows it was a choice and not an accident.

```python
# Bad: any failure vanishes. A typo'd cache key looks identical to a
# cache miss, and you debug the wrong layer for a day.
try:
    return cache.get(key)
except Exception:
    pass
```

```python
# Good: the one expected failure is handled; the rest still surface.
try:
    return cache.get(key)
except CacheMiss:
    return None  # cold cache is normal; recompute below
```

Catch the narrowest exception type that you actually expect. A bare
`except:` or `catch (e)` around a broad block catches the bugs too: the
typo, the `KeyError`, the interrupt you meant to let through. When you
must catch broadly (a task runner draining a queue, a request handler that
must not die), log the full error with its stack before deciding to
continue, so a swallowed failure is still a recorded one.

## Write messages that let someone act

"An error occurred" tells the reader that something exists. An actionable
message names what was attempted, with which inputs, and what the
constraint was. The person reading it at 3am did not see the code run.

```python
# Bad
raise RuntimeError("validation failed")
```

```python
# Good
raise ValueError(
    f"user {user_id}: start_date {start!r} is after end_date {end!r}"
)
```

Include the values that vary and would let someone reproduce or locate the
problem: the id, the path, the offending field. Leave out anything you
cannot safely print (see the last section). State the constraint that was
violated, not just that one was: "expected a positive timeout, got -5"
beats "invalid timeout".

## Preserve the cause

When you catch an error and raise a new one, the original is the single
most useful thing you have. Chain it. A new message with the underlying
cause discarded throws away the stack trace that points at the real line.

```python
# Bad: the caller learns "could not load config" and nothing about why:
# permission denied? bad YAML? which file?
try:
    return yaml.safe_load(open(path))
except Exception:
    raise ConfigError("could not load config")
```

```python
# Good: adds context, keeps the original cause and its traceback.
try:
    return yaml.safe_load(open(path))
except (OSError, yaml.YAMLError) as e:
    raise ConfigError(f"could not load config from {path}") from e
```

Use the language's cause mechanism: `raise ... from e` in Python,
`throw new Error(msg, { cause: e })` in JS, wrapping with `%w` in Go,
`initCause` in Java. Never reduce an exception to `str(e)` in a new
message and drop the object; the string loses the type and the trace.

## Recoverable or fatal

Not every error deserves the same response, and the code should say which
kind it is thinking it caught. A recoverable error is one the program has
a real alternative for: a cache miss it can recompute, an optional file it
can default, a request it can retry. A fatal one leaves no good next step:
a missing required config, a failed invariant, a corrupt data structure.

Handle the recoverable ones close and specifically. Let the fatal ones
propagate to a top-level handler that logs and exits or fails the request
cleanly. The mistake in both directions: treating a fatal error as
recoverable (retrying a request that will never succeed because the
credentials are wrong) and treating a recoverable one as fatal (crashing
the whole batch because one record was malformed when the other 9,999 were
fine).

## Catch where you can act

Catch an error at the layer that can do something meaningful about it, not
at the first line where you could physically write a `try`. A `try` around
a low-level read that just logs and returns `None` forces every caller to
re-handle the same failure, worse, without the original error. Let it
propagate to the boundary that knows the request, the transaction, the
retry budget, the user to apologize to.

```python
# Bad: the parser decides the whole request's fate and loses context.
def parse_row(line):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None  # every caller now guesses what None meant
```

```python
# Good: the parser reports; the boundary decides skip vs abort.
def parse_row(line):
    return json.loads(line)  # raises; caller has the context to handle it

def import_file(path):
    for n, line in enumerate(open(path), 1):
        try:
            save(parse_row(line))
        except json.JSONDecodeError as e:
            log.warning("skipping %s line %d: %s", path, n, e)
```

The boundary is where the decision lives: the request handler, the job
runner, the CLI's top frame, the transaction scope. That is also the
natural home for the one broad catch that turns any unexpected failure
into a clean 500 plus a logged stack, instead of a leaked trace.

## Retry, propagate, or crash

Three responses to an error, chosen by what the error means:

- **Retry** only what is transient and idempotent: a network blip, a lock
  timeout, a 503. Bound it (a few attempts, backoff) and give up to
  propagation. Retrying a deterministic failure, a 400, a validation
  error, a `KeyError`, just burns time and arrives at the same wall.
- **Propagate** when this layer cannot do better than its caller. Add
  context, keep the cause, rethrow. Most catches in the middle of a system
  should be this or nothing.
- **Crash** (or fail the unit of work) when the state is unsafe to
  continue on. A failed startup check should exit, not serve traffic with
  half its config. Crashing early and visibly beats corrupting data
  quietly.

The anti-pattern is the retry loop as a cure for a bug: wrapping a call in
"try three times" because it sometimes fails, without knowing why it
fails. If the failure is deterministic, retrying hides it; find the cause
(that is debugging's job) instead of amortizing it.

## Don't leak secrets or internals to users

The message a user sees and the message you log are two different
audiences. The log gets everything: stack, cause, ids, the query that
failed. The user gets what helps them without handing an attacker a map.

```python
# Bad: leaks the SQL, the schema, and possibly the connection string
# straight to whoever hit the endpoint.
except Exception as e:
    return Response(str(e), status=500)
```

```python
# Good: full detail to the log, a stable reference to the user.
except Exception:
    ref = uuid4().hex[:8]
    log.exception("checkout failed ref=%s", ref)
    return Response(f"Something went wrong. Reference: {ref}", status=500)
```

Never put a stack trace, a raw SQL error, a file path, or a token into a
user-facing message or an HTTP response body. The reference id ties the
polite message to the full internal record without exposing it. Same rule
for exception messages that get serialized into API responses: strip them,
or map known errors to safe, specific messages and everything else to a
generic one.
