---
name: bug-reports
description: "Write bug reports a stranger can act on without a follow-up question: one bug per report, a symptom-plus-condition title, expected versus actual behavior, numbered reproduction steps from a clean start, exact error text, the environment details that matter, and observation kept separate from speculation. Use whenever filing an issue or bug report, writing up a defect found while testing or reviewing, reporting a failure upstream, escalating an incident in writing, or firming up someone else's vague report. Pairs with debugging, which produces the reproduction worth filing."
---

# Bug reports

The natural bug report is "export is broken, please fix ASAP." It
records the reporter's frustration and none of their knowledge: not
what they clicked, not what appeared instead of what they expected,
not the error text that was on their screen at that exact moment.
Whoever picks it up starts a guessing correspondence ("what were you
doing? what did it say? what browser?"), each round trip costing a
day, until the report contains what it could have contained on day
one. The reporter had every fact when they hit the bug; the report is
where those facts go to survive.

A good report is a reproduction recipe plus evidence. Everything
below serves someone who was not there and needs to make the bug
happen on their own machine, because per debugging, reproduction is
where any real fix starts.

## One bug, one report

A report holding three bugs gets the lifecycle of none of them: it
cannot be closed until all three are fixed, cannot be assigned to one
owner, and its thread braids three investigations. File three
reports; cross-link them if related. The same rule as atomic-commits,
for the same reason: things that resolve independently must be
tracked independently.

If, while writing up one bug, you find another, that is a second
report, not a "also noticed..." paragraph.

## The title states symptom and condition

The title is the report's search key and triage handle. "Export
broken" matches every export bug ever filed; "CSV export returns
empty file when date range spans a month boundary" lets triage route
it, lets the next reporter find it before filing a duplicate, and
tells the fixer half the repro before the click. The formula: what
went wrong, under what condition. If the condition is unknown, say
what is known: "CSV export intermittently returns empty file (~1 in
10)."

## The core: expected, actual, steps

Three sections carry the substance, and the discipline is keeping
them factual:

- **Steps to reproduce**: numbered, from a clean, stated starting
  point ("log in as a member-role user, empty cart"), each step an
  action someone else can perform, ending at the failure. The test:
  a stranger following exactly these steps hits the bug, or the
  report is not finished. Shrink the recipe before filing, per
  debugging's isolation: fewer steps, smaller input, default
  settings; every step you remove is a variable the fixer need not
  consider.
- **Expected**: what should have happened, and, when it is not
  obvious, why you expected it (the doc, the spec, the other
  screen that behaves that way). Sometimes this reveals the bug is
  in the expectation, which is also worth knowing.
- **Actual**: what happened instead, described at the surface where
  you observed it. "Nothing happened" is an observation; "the click
  was ignored" is already an interpretation.

State frequency: always, or intermittent with a rate ("3 of 10
attempts"). An intermittent bug hunted as a deterministic one burns
the fixer's first day, and per debugging, the rate is what makes a
later fix verifiable at all.

## Paste the evidence, exactly

The error text, the stack trace, the log excerpt: paste them as text,
verbatim, in a code block. Not paraphrased ("some kind of permission
error"), because the exact message is what the fixer greps the
codebase and the tracker for; not a screenshot of text, because
screenshots cannot be searched, copied, or diffed, and they compress
badly. Screenshots are for what is genuinely visual: rendering
glitches, layout breaks, the state of a canvas.

Trim to the relevant region but do not edit within it; the frame you
consider irrelevant may be the one that matters. Long logs go in an
attachment or gist with the key lines quoted inline.

Include the environment facts that vary: versions (app, library, OS,
browser), the deployment or instance, relevant config flags, and the
timestamp with timezone for anything server-side, so the fixer can
find the corresponding server logs. Skip the ones that do not vary
for this system; a checklist of sixty environment fields nobody
fills in is how templates die.

## Observation before theory, and labeled

Reports rot when diagnosis contaminates observation: "the cache is
serving stale sessions again" files a theory, and if the theory is
wrong, the fixer inherits both a bug and a red herring with the
reporter's authority behind it. Report what you saw in the
observation sections; then, if you have a theory, add it clearly
fenced: "Possibly related: this started the day after #481 merged."
A labeled hunch is valuable signal; an unlabeled one is a trap.

Two more sections earn their place when you have them:

- **What you already ruled out**: "same request succeeds via curl
  with the same token" saves the fixer from re-walking your steps.
- **Impact, honestly**: who is affected, how badly, with the
  workaround if one exists. Impact decides priority, so inflating it
  ("CRITICAL: text misaligned") teaches triage to discount your
  severities, which costs you the day the critical one is real.

## Triaging a vague report

When you receive "it doesn't work," the skill runs in reverse:
extract, do not resent. Ask for the missing core as specific
questions ("what did the screen show after you clicked save? paste
the exact error if there was one"), each answerable in one line, not
"please provide more details," which returns another paragraph of
vibes. Then write the firmed-up version into the report so the next
reader starts from facts. A vague report is unrefined ore, not noise;
the reporter saw a real failure, and the facts are still in their
head if asked for soon.

## Bad, then good

> **Title: Search broken!!**
>
> Search stopped working, probably the elasticsearch upgrade again.
> Nothing comes up. This is blocking everyone, needs a fix today.

> **Title: Search returns 0 results for queries containing a space
> (single-word queries fine)**
>
> Steps (app v2.41.0, staging, any browser):
> 1. Log in as any user, open the top-bar search
> 2. Search `invoice` : 34 results
> 3. Search `invoice march` : 0 results, no error shown
>
> Expected: results matching both terms (worked on v2.40.2, same
> staging data).
> Actual: 0 results for any query with a space; response is 200 with
> an empty list. Browser console shows the query sent as
> `q=invoice+march`.
>
> Always reproducible, staging and prod. Ruled out: same query
> through `GET /api/search?q=invoice%20march` returns 34 results, so
> likely frontend encoding, not the search backend. Impact: search
> effectively unusable for multi-word queries, no workaround in UI.
> Possibly related (unverified): #512 touched the search bar last
> week.

The first report contains a mood and a theory. The second contains
the condition (spaces), the boundary (UI yes, API no), the version
that last worked, the frequency, and a labeled hunch, and its
ruled-out section has already done the fixer's first hour of
bisection.
