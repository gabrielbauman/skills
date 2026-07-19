---
name: flaky-tests
description: "Treat an intermittently failing test as a bug to fix, not a nuisance to rerun: quarantine it visibly with an owner and an expiry instead of retrying until green, reproduce the flake with a counted loop, diagnose against the usual suspects (sleep-based waits, test order and shared state, unseeded randomness, real clocks, real networks, leaked resources), fix the mechanism instead of widening the timeout, and recognize when the flake is a real race in the product. Use whenever a test fails intermittently or only in CI, passes on retry, fails only in parallel runs or only after other tests, or when asked to fix, skip, or delete a flaky test, add automatic retries to a suite, or investigate CI instability. Pairs with test-behavior, which covers what tests should assert in the first place, and debugging, whose counted-reproduction discipline is how a flake gets pinned down."
---

# Flaky tests

A flaky test dies by rerun. The first time it fails for no reason,
someone clicks retry and it passes; from then on, retrying is the
protocol, and the suite has a test whose result carries no
information. Soon there are five of them, every red build means
"probably the flakes," and the regression that matters rides in
unread. Automatic retries industrialize the problem: the suite is
green, the information is gone, and nobody even sees the failures
anymore.

A flaky test is a bug with a fixed set of usual suspects. It lives in
one of three places: the test, the code under test, or the
infrastructure, and until you know which, you do not know whether you
are ignoring noise or silencing the one test that caught a real race.

## Rerun is not a disposition

When a test flakes, it gets exactly one of these outcomes, and
"clicked retry, went green" is not on the list:

- **Fixed**: the mechanism found and removed (most of this skill).
- **Quarantined**: visibly skipped, with a ticket, an owner, and an
  expiry. Quarantine beats letting it fail randomly, because a suite
  that is red for known noise trains everyone to ignore red. But
  quarantine is a loan: `skip("flaky, see #4812, expires 2026-08-15")`
  is honest, a bare `skip` is where tests go to die.
- **Deleted**: only if the test's assertion is not worth having, which
  is a test-behavior judgment, not a flakiness one. Deleting coverage
  because it is inconvenient is silencing a witness.

Blanket auto-retry (run every failure three times, pass if any pass)
converts flakes from a visible annoyance into an invisible policy.
If retries exist at all, they exist as instrumentation: retried tests
get logged and tracked, because each retry is a flake report.

## Reproduce it in a loop

You cannot fix what you cannot make happen, and for a flake the
reproduction is statistical, exactly as debugging treats intermittent
failures: run the test in a loop and count. `pytest --count=200`,
`go test -count=200`, or a shell loop; note the failure rate. A fix
you cannot distinguish from luck is not a fix, and 0/200 after a fix
means something only because it was 7/200 before.

Reproduce under the conditions that flake, because the conditions are
evidence:

- Fails alone or only in the full suite? Run it solo, then after the
  suite. Solo-pass suite-fail means another test leaks state into it;
  bisect the test order to find which.
- Only in parallel? Run with the CI worker count. Points at shared
  resources: same DB rows, same port, same temp path, same global.
- Only in CI? The bug is in the difference: slower machine (timeouts),
  different timezone or locale, different parallelism, missing warm
  caches.

## The usual suspects

Almost every flake is one of these. Check them in order of frequency:

- **Time**: a `sleep(2)` standing in for "wait until ready" fails the
  day CI is slow. Replace sleeps with condition waits: poll for the
  actual state with a deadline. Assertions on `now()` fail at
  midnight, month ends, and DST; inject a fake clock.
- **Order and shared state**: tests that pass alone and fail together
  are coupled through leftovers: a DB row, an env var, a module-level
  cache, a singleton. Give each test its own state (fresh fixtures,
  unique ids, transactions rolled back) and reset what is shared.
  A test that must run first is a bug even while it passes.
- **Concurrency in the product**: the test intermittently observes a
  real race in the code under test. This is the jackpot case: the
  flake is a correct bug report. Silencing it (retry, wider timeout)
  ships the race to production with the witness removed.
- **Randomness**: unseeded generators, iteration over unordered maps,
  `select` without ordering. Seed the RNG per test, sort before
  asserting, or assert order-independently.
- **The network**: a test that calls a real external service inherits
  that service's uptime. Fake the boundary (per test-behavior); the
  integration path gets its own suite that is allowed to be slow and
  is monitored, not one flake among unit tests.
- **Leaked resources**: ports still bound, files still open,
  processes still running from the previous test. Symptoms look like
  "address in use" or "database is locked" on the second run.

## Fix the mechanism, not the margin

Widening a timeout from 2s to 10s does not fix a flake; it lowers its
frequency until it only fires on the worst days, which are exactly
the days CI is already slow and everyone is deploying. The mechanism
fix replaces the guess about timing with an observation of state:

```python
# Flaky: 2 seconds is a guess, and CI disagrees on bad days.
worker.start()
time.sleep(2)
assert worker.status == "ready"

# Stable: wait for the condition itself, with a generous deadline
# that only matters when something is genuinely wrong.
worker.start()
wait_until(lambda: worker.status == "ready", timeout=30)
```

The deadline still exists, but it is no longer load-bearing: it fires
only on real failure, so it can be generous without slowing the happy
path by a millisecond.

## Keep the ledger

Track flakes as a population, not as incidents: which tests are
quarantined, since when, owned by whom, at what failure rate. The
ledger is what stops quarantine from becoming a graveyard, and the
trend (flakes added vs. flakes fixed) tells you whether the suite is
getting more or less trustworthy. A team that cannot answer "how many
quarantined tests do we have?" is accumulating them.

The payoff for all of this is binary trust: a suite where red means
broken and green means safe. Every tolerated flake is interest on
that trust, and the rerun button is how it compounds.
