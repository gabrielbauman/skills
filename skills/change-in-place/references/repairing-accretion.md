# Unwinding a module that already accreted

How to repair a module where adding beside went unchecked for a long time:
how to confirm that is what happened, what order to undo it in, and when to
stop. Read it before starting on such a module. It is not needed to fix a
single function you already understand, which the SKILL.md rules cover.

## Confirm it before committing to the work

Accretion and ordinary complexity look alike from inside a single function.
The difference is visible in the file's history: a module that accreted has a
line count that has never once gone down.

```sh
f=path/to/the/file
git log --format=%h -- "$f" | while read h; do git show "$h:$f" | wc -l; done
```

This prints newest first. A curve with no dips means no change in that file's
history ever replaced anything, only added. A module that is merely large but
healthy shows dips: the commits where someone deleted a path, collapsed two
cases, or moved code out.

Two more counts worth taking before you plan the work, because they predict
how much of the big function will survive:

- How many groups of functions share a name with a qualifier attached. Each
  group collapses to one function.
- How many fields the constructor does not initialize. Those are the ones
  added later, and they are where the per-operation state is hiding.

## Unwind in this order

The order matters, and it is not the order the damage is most visible in.

**1. Collapse the near-named families.**

Take one group at a time. Read all the variants together, write the single
function that covers every case with the distinguishing input as a parameter,
point the call sites at it, and delete the variants.

Do this first because it is the cheapest work in the module. The variants are
small, the existing tests already cover their behavior, and each collapse
removes call-site knowledge, so the rest of the module gets easier to read
before you have had to understand any of it.

Expect to find that the variants disagree. Three predicates written months
apart will have drifted on some input, and writing the merged version forces
you to decide which one was right. That disagreement is usually a live bug
nobody had a way to see, so surface it rather than preserving both answers
behind a branch. If you cannot tell which behavior is correct, that is a
question for whoever owns the module, not a reason to keep three functions.

**2. Move per-operation state off the long-lived object.**

Start with the fields the constructor does not initialize. For each one, ask
whether anything reads it on a later operation than the one that wrote it. If
nothing does, it is per-operation state: compute it where the operation
starts, pass it to what needs it, and delete the field.

This usually shortens the signatures you were about to be stuck with, because
the parameters that got added one at a time were standing in for state that
had no home.

**3. Only now open the large function.**

It was long partly because of the first two steps, and it has been getting
shorter while you worked. What is left is the part that was genuinely doing
too much, and it is now small enough to hold.

Starting here is the common instinct and the expensive one. A 500-line
function that references 40 fields and 80 functions cannot be held in your
head, and most of what you would be reading is about to disappear.

## Expect the test suite to fight you

A suite that accreted alongside the code pins structure rather than behavior.
Per-ticket test files assert on the variants you are about to merge and the
fields you are about to remove, so the collapse in step one will turn them
red even though behavior has not changed.

When that happens, the red test is the finding. A test that must change
during a behavior-preserving refactor was testing the mechanism, not the
behavior, which is test-behavior's subject. Rewrite it against the merged
function and the observable outcome, and fold it into the file that covers
that behavior rather than leaving it in the file named after the ticket.

The exception that is not a finding: a test that goes red because the merged
function resolved a disagreement between variants. That one is reporting a
real behavior change, and it needs a decision rather than a rewrite.

Refactoring covers the mechanics of staying green through all of this, and
small-prs covers not attempting it in one branch.

## Stop before you have fixed everything

Repair the part you came to change. A module that accreted for a year will
not come apart in one pass, and a branch that tries will be unreviewable,
which is how the second rewrite gets abandoned and the module keeps its
reputation as untouchable.

Pick the families and fields your actual change touches, leave the rest, and
let the next person's change pay for the next piece. The line-count curve is
the measure: the goal for this branch is one dip in it, not a flat floor.
