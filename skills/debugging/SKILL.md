---
name: debugging
description: "Debug systematically instead of speculatively: reproduce the failure first, read the actual error, test one hypothesis at a time, isolate the cause before changing code, and verify the fix against the original reproduction. Use whenever investigating a bug, crash, error, test failure, or unexpected behavior, when a fix did not work, when a failure is intermittent, when tempted to try a change just to see if it helps, or when asked why something broke. Covers capturing a rerunnable reproduction, reading the whole error instead of pattern-matching to a famous fix, reverting unverified attempts, bisecting and shrinking the failing case, fixing the cause rather than the symptom nearest the crash, verifying against the repro rather than the green suite, and when to stop and report instead of piling on another guess. Pairs with test-behavior, which turns the reproduction into the permanent regression test."
---

# Debugging

The default agent debugging loop is guessing with extra steps: read the
error, pattern-match it to a famous fix, apply the fix, and when it does
not work, apply the next guess on top of the first. Each guess is locally
plausible. The pile is five unverified edits deep, the bug is still there,
and the tree now needs its own debugging.

Systematic debugging is a short loop: reproduce the failure, find what is
actually wrong, fix that, and prove it on the reproduction. The steps
below are in order; the discipline is not skipping ahead.

## Reproduce first

Before changing anything, make the bug happen on demand. Without a
reproduction you cannot know you fixed it; you can only know you changed
something. Capture the repro in a form you can rerun: a command, a script,
a failing test. It becomes the verification at the end, and afterwards
test-behavior turns it into the regression test.

Read the report for conditions, not just the symptom. "Search is broken"
usually means "search is broken when the query has a space and the user is
on page two". The conditions are the repro.

If the failure only happens in CI or production, the bug is in the
difference between there and here: versions, environment variables, data,
timing. Diff the environments before diffing your code.

If the failure is intermittent, the repro is statistical. Run it in a loop
and count; a fix you cannot distinguish from luck is not a fix. Where you
can, remove the nondeterminism (seed the RNG, fix the clock, control
ordering) until the failure is reliable.

"Can't reproduce" is a finding to report along with what you tried, not a
prompt to start guessing.

## Read the error, not your guess

The error and its stack trace are the only witnesses present at the
failure. Read all of it: the first error rather than the last line, the
causes chained underneath, the frames in your code rather than the
framework's.

Agents pattern-match messages to famous fixes: "relation does not exist"
gets a migration, "certificate verify failed" gets verification disabled.
Sometimes the famous fix is right; the danger is applying it without
checking the assumption it rests on. Which database is the app actually
connected to? Which certificate, from which host, since when? One minute
confirming the assumption beats an hour reverting a confident wrong fix.

When the message is cryptic, find where it is raised and read the code
around the raise. The condition guarding the raise statement is the
error's real meaning.

## One hypothesis at a time

State the current theory in one sentence before acting on it: "the refresh
token is treated as expired because the container clock is five minutes
slow". A theory you cannot state is a guess, and an unstated guess tends
to get made twice.

Test the theory by observing, not by mutating: a log line at the right
spot, a debugger breakpoint, a query against the live state, reading the
code path. Observations are free and revert-proof. Edit code only once a
theory has survived observation.

If a fix attempt does not fix it, revert the attempt before trying the
next one, unless you have confirmed it repairs a real, separate defect.
Speculative changes compound: after three unverified edits you no longer
know which behavior comes from the bug and which from your own fixes, and
one of them (SSL verification disabled, timeouts tripled) will ship by
accident.

## Isolate the cause

Shrink the failing case: cut the input, the config, and the call graph
down to the smallest thing that still fails. A ten-line repro names the
room the bug lives in; a four-hundred-line one keeps it hidden.

Bisect. "Worked at the last release" is a job for `git bisect`; "breaks
somewhere in this pipeline" is a job for commenting out halves. Binary
search over a hundred suspects beats reading them in order. And when the
failure arrived with one known change (a deploy, a merge, an upgrade),
there is nothing to search: the diff of that change is the suspect list,
and it is short.

Change one variable at a time. Upgrade the dependency and edit the config
in the same run and a persistent failure tells you nothing about either.

## Fix the cause, not the nearest symptom

The crash site is where bad state surfaced, rarely where it was created. A
guard at the crash line hides the bug and pushes the damage downstream,
now silent. Trace the bad value back to where it became bad and fix there.

Be able to say why the old code produced the failure and why the new code
cannot. If the honest answer to "why did this ever work" is "it didn't" or
"luck", keep digging.

Aim the fix at the failure class, not the observed instance. Skipping the
one corrupt record lets the next one through; fixing the parser that
produced it stops the whole class.

## Verify against the repro

Rerun the exact reproduction from the start and watch it pass, under the
same conditions that failed: same input, same scale, same concurrency.
"The suite is green" proves only that the suite passes; it was green while
the bug shipped. The repro is the test the bug actually failed.

Then run the suite for collateral damage, and land the repro as a
permanent test per test-behavior.

## When you're stuck

Budget the guesses. After three theories tested and dead, or a fixed block
of time without a confirmed hypothesis, stop and report. Report the repro,
the theories tested with the evidence that killed each, and the places the
failure has been ruled out. That is a state someone else, or tomorrow's
you, can continue from. A tree full of half-applied guesses is not.

Say "I haven't found it" plainly. The expensive failure mode is the
confident wrong fix that ships because stopping felt like losing.

## Bad, then good

Bug report: "account export crashes with IndexError when the account has
no orders."

```python
# Symptom patch: the crash moves out of sight, and accounts with no
# settled orders now export a file containing someone else's totals.
try:
    first = rows[0]
except IndexError:
    first = last_known_row
```

```python
# Cause fix: summarize() filters to settled orders, so an account with
# only pending orders yields empty rows; render that case explicitly.
if not rows:
    return render_empty(reason="no settled orders")
first = rows[0]
```

The IndexError was the messenger. The first version shoots it and corrupts
data quietly. The second reads the message (why is `rows` empty?), answers
it in `summarize()`, and the fix can no longer produce a wrong export,
only a correct empty one.
