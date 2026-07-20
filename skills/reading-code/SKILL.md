---
name: reading-code
description: "Understand unfamiliar code before changing it: orient from entry points and build files, trace a real call path instead of trusting the first grep hit, read tests as the intent spec, use git history to recover why the weird part exists, find the codebase's existing way, and verify your model before editing on it. Use when starting in a codebase or subsystem you haven't touched, changing code you don't fully understand, asked how or why code works, or tempted to add a helper that may already exist. Pairs with debugging, the same hypothesis-then-observation discipline aimed at a defect."
---

# Reading code

The default failure in an unfamiliar codebase: grep for a keyword,
open the first hit, start editing. The edit is locally plausible; it
compiles, it matches the style of the file it sits in. It is also in
the deprecated copy of the module, or it duplicates a helper two
directories away, or it breaks an invariant every caller relies on.
Reading feels like not-working, so it gets skipped, and the cost
comes back as rework, review comments, and regressions in code you
never opened. Most changes are mostly reading; the typing is the
short part at the end.

## Match the reading to the blast radius

Reading has a budget, set by the change, not the repo. A typo fix
needs one file. A new endpoint needs the module, its neighbors, and
the conventions they share. A change to shared or core code needs its
callers, because they are the blast radius. The stop condition: read
until you can predict what your change will break, then stop. If you
cannot name what might break, you have not read enough; if you are
reading subsystems your change cannot reach, you have read too much.

## Orient before digging

The first pass over a repo is for a map, not comprehension. The
README and contributing guide say what the thing is; the build and
manifest files say what it really depends on and how it runs, and
they do not go stale the way prose does; the directory layout and
test locations say where kinds of things live. Then find the entry
points: the main function, route table, CLI parser, job scheduler.
Execution starts somewhere, and knowing where turns a pile of files
into a call graph you can walk.

## Trace a real path, don't trust grep

Grep finds names; it does not rank them. Three hits for
`calculateTotal` may be the live implementation, a legacy copy kept
for one old client, and a test double, and nothing in the search
output says which is which. Pick a real trigger (one request, one
CLI invocation, one event) and follow it from the entry point until
it passes through the code you intend to change. That path is the
load-bearing one; hits you cannot reach from any entry point are
probably dead, and editing dead code either does nothing or, worse,
you wire it back to life.

Running the code is reading too, and it is the only kind that cannot
be wrong: a log line or breakpoint at the suspected spot settles
which branch actually executes faster than an hour of tracing by
eye.

## Tests are the intent spec

Read a unit's tests before the unit. The implementation says what
the code does; the tests say what it is supposed to do, which inputs
are legal, which edge cases the team has been burned by, and (via
fixtures and setup) how its objects are meant to be constructed. A
confusing function with clear tests is a clear function. The absence
of tests is information too: untested code deserves characterization
tests before you edit it, per refactoring.

## History answers "why is this weird"

The odd guard, the magic sleep, the config nobody can explain:
before removing the fence, find out why it was built. `git blame` on
the line and the commit message behind it, plus the PR or issue the
message links, is usually the missing comment; `git log -S 'thing'`
finds when the thing appeared and what else arrived with it. If the
reason turns out obsolete, remove the code and say why in the
commit; if no reason survives anywhere, that uncertainty belongs in
the commit message too.

History also shows which conventions are current. Old files and new
files in the same repo often disagree; the recent commits show what
the team writes now, and that is the pattern to follow.

## Find the existing way

Before writing anything, find how this codebase already solves this
class of problem: the error type, the retry helper, the middleware
chain, the fixture builder. Look at the siblings of the thing you
are adding; how the other three endpoints handle auth is how yours
should. Follow the house pattern even where you would have chosen
differently, because a second convention is a cost every future
reader pays, and a new util duplicating an old one is two behaviors
to keep in sync forever. Write something new only after a genuine
search has come up empty, and say so in the PR.

## Verify the model before editing on it

Reading produces a belief; state it in one sentence before building
on it. "All order writes go through OrderService.save." "This config
is only read at startup." Then spend a minute trying to break it:
search for the counterexample (a write that bypasses the service, a
reload path), run the test that would prove it, add a log and
trigger it. The code that violates your model is exactly the code
your change will break, and it is much cheaper to meet it now than
in the incident review. This is debugging's discipline pointed at
understanding: hypothesis, observation, and only then the edit.

## Bad, then good

Task: "add rate limiting to our API."

Bad: create `middleware/rate_limit.py` from scratch, register it
globally in `app.py`, ship it. The repo already had a `throttle.py`
used by two routes, so limits now apply twice on those routes and
inconsistently everywhere else, and the new middleware ignores the
per-route decorator convention every other cross-cutting concern
follows.

Good: trace one request from the entry point and list what it passes
through; find the middleware chain and the existing `throttle.py`,
and read its tests to see the intended usage; note the convention
(cross-cutting concerns attach per-route, not globally); extend the
existing throttle and attach it the house way. The diff is smaller,
consistent, and does not fight code you did not know existed.
