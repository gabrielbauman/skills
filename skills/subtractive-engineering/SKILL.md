---
name: subtractive-engineering
description: "Apply a fixed, ordered process before building: question every requirement back to the person who asked, delete the part or process outright, simplify what survives, accelerate the loop, and automate last, because optimizing or automating an unquestioned step does the wrong thing faster. Use when designing a feature, planning an architecture change, adding a dependency, flag, config option, build step, CI job, or process, or when asked to optimize or automate something nobody has confirmed should exist. Pairs with performance, which governs how to optimize what survives step two."
---

# Subtractive Engineering

The most expensive engineering waste is not sloppy work; it is
competent work on things that never needed to exist. A team ships a
polished PDF exporter for a requirement nobody can trace, optimizes a
code path that three deleted feature flags would have removed, and
automates a weekly report that no one reads. Each step was executed
well. The waste is that the step existed.

The correction is a fixed, ordered process: **question, delete,
simplify, accelerate, automate**. The order is the point. Each step
earns the right to the next, and skipping ahead is how you end up
doing the wrong thing faster and more reliably. If you notice you are
optimizing or automating a part whose existence you never confirmed,
stop, return to step one for that part, and re-walk the steps in
order.

Apply this to any proposal that adds a part, step, dependency, flag,
or process: feature designs, refactors, architecture decisions, build
and CI pipelines, tooling, automation. Apply it to every such proposal
in a task, not just the first one you meet.

## Step 1 — Question every requirement

Every requirement comes from a person, not a department. "The
platform team requires it" and "the spec says so" are not reasons;
they are pointers to a person whose reason you have not heard yet.
Trace each requirement to the specific individual who asked for it,
so it can be challenged and so accountability is real.

- Challenge every assumption, whoever it came from. Requirements from
  senior or respected people deserve the *most* scrutiny, not the
  least: they get questioned the least, so they accumulate the most
  unexamined cruft.
- When a requirement's owner or rationale is unknown, treat it as a
  Chesterton's fence: find out why it exists before acting on it. If
  the purpose stays unclear after looking, ask the requester rather
  than guessing a rationale.
- "That's the requirement" is the start of the conversation, not the
  end. Ask for the underlying need and the person behind it.

Requirement: "the onboarding flow must email a PDF receipt." Question
it: who asked for the PDF specifically? Traced back, the request came
from a finance lead who wanted an auditable record, not a PDF. A line
item in the existing dashboard satisfies the real need, and the PDF
requirement dissolves before any code is written.

## Step 2 — Delete the part or process

Default to removing the part, step, dependency, flag, or process
entirely. Add it back only when its absence demonstrably breaks
something.

- Calibrate by what comes back: if you never have to restore anything
  you deleted, you were deleting too timidly. Expecting to re-add a
  small fraction is the sign the deletions were aggressive enough.
- When something is hard to delete, prefer deleting it over
  generalizing it or wrapping it in guards. Generalization preserves
  the cost and adds interface on top.

A service has three feature flags guarding paths that shipped to 100%
of users over a year ago. Delete the flags and the dead branches
outright. If a rollback need surfaces later, restore the one flag
actually required, starting from zero, rather than keeping all three
against the possibility.

## Step 3 — Simplify or optimize what remains

Only after questioning and deleting do you improve what survives. The
most common mistake of a strong engineer is optimizing a part that
should have been deleted in step two; skill makes the waste more
polished, not less wasteful.

Keep a whole-system view: optimize for the overall outcome, not a
local metric. Shaving cost off one component while the larger system
pays for it elsewhere is a loss dressed as a win, and it happens
whenever a component is optimized against its own dashboard instead
of the system's.

## Step 4 — Accelerate cycle time

Once the design is questioned, lean, and simple, speed up the
iteration loop: faster tests, faster builds, smaller increments,
quicker review turnaround. Acceleration comes fourth because speeding
up a loop that contains unnecessary steps just runs the waste more
often per day.

## Step 5 — Automate

Automate last, and only a process that has already survived
questioning, deletion, simplification, and acceleration. The failure
mode this ordering prevents: heavily automating a step and then
discovering the step was unnecessary means you built and now maintain
a machine that does nothing.

A team wants to automate a manual weekly report. Walking the steps
first: questioning reveals only one stakeholder ever reads it, and
deleting the report entirely draws no complaint. The right outcome is
no report and no automation, not a polished script generating
something nobody needs.

## Checklist

Before adding any part, step, or automation, confirm these in order.
If an earlier item cannot be answered, resolve it before moving to a
later one.

1. **Questioned** — I know who asked for this and why, and the
   requirement is real.
2. **Deleted** — I tried removing it entirely first and observed what
   actually broke.
3. **Simplified** — What remains is as simple as it can be, optimized
   for the whole system.
4. **Accelerated** — I am speeding up a design that already passed the
   earlier checks.
5. **Automated** — This process earned automation by surviving steps
   one through four.
