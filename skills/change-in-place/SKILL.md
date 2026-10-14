---
name: change-in-place
description: "Put a fix where the wrong behavior is instead of adding code beside it, because green tests after an additive fix only prove you left the old path alone. Use when the request points at an additive fix: add a flag for one case, special-case an input, wrap an existing call, keep current callers working, make the smallest or least invasive change, or leave a function alone because other code calls it. Also when fixing a bug in working code or reviewing a fix whose diff only adds lines. Pairs with debugging, which finds the cause this skill tells you to edit."
---

# Change in place

A bug arrives. The function that handles the case is right there, but changing
it might affect other callers, so a second function appears beside it that
handles this case correctly. The next bug gets a third function, and a map to
hold the state it needs. In one service's sync loop, eight tickets took the
main struct from 7 fields to 45, the package from 9 functions to 87, and the
cycle function from 262 lines to 540. The loop's job never changed.

Every step was defensible and nothing said stop, because an additive fix
cannot break the path it did not touch: a green suite after one proves only
that you left the old code alone. Call the move *adding beside*. Catching it
is a matter of noticing the moment, not of learning a rule you don't already
know.

## Put the change where the wrong behavior is

When code handles a case incorrectly, the fix belongs in that code, not in a
new thing that runs before it, after it, or instead of it for this one input.
Adding beside leaves two places that both claim the case, and no written
statement of which one wins. The next reader has to work that out from the
call sites.

Three questions before you edit:

1. Which line produces the wrong behavior? Put the change there.
2. If the change is going somewhere else, name the reason it cannot go in that
   line. You can see every caller, so "other callers" counts only after you
   have read them.
3. What does this change delete?

Question three is the one that catches this early. A fix whose diff has no
deletions is not automatically wrong, but it is worth thirty seconds before
committing: a bug means something in the code was wrong, and a change that
removes nothing is claiming the wrong thing should stay.

## A near-copy means the original is wrong

The clearest form of adding beside is a function whose name is another
function's name with a qualifier attached.

```python
def is_retryable(err):
    return err.status in (429, 500, 502, 503)

# A 409 on a create is another record winning the name, not a blip.
def is_retryable_for_create(err):
    return is_retryable(err) and err.status != 409

# User creates are different: the directory locks the row mid-provision.
def is_retryable_for_user_create(err):
    return is_retryable_for_create(err) or err.status == 423
```

Three functions, written months apart, each narrowing or widening the one
above it. The rule is no longer in any single place, and every call site now
has to pick the right variant. Pick wrong and nothing fails loudly.

```python
def is_retryable(err, operation):
    if err.status == 409:
        return False  # a conflict is a decision by the server, never a blip
    if err.status == 423 and operation == "user.create":
        return True  # the directory locks the row mid-provision
    return err.status in (429, 500, 502, 503)
```

One function, one reading of the rule, and the distinguishing input is a
parameter instead of a naming convention.

Watch for the comment, too. Each wrapper above carried a line explaining why
it is not the function above it. A comment whose job is to distinguish a
function from its near-twin is the twin telling you it should not exist.

## A new field needs an owner before it exists

Before adding state to an object that outlives a single operation, name the
code that writes it and the code that reads it. If you cannot name both in a
sentence, you are about to create a field that accumulates and nobody dares
clear.

The fingerprint of a field that skipped this step is lazy initialization at
the top of a method:

```python
def run_cycle(self):
    if self.pending is None:
        self.pending = {}
    if self.versions is None:
        self.versions = {}
    if self.debts is None:
        self.debts = {}
```

Each of those was added long after the constructor, by someone who did not
want to touch the constructor. The constructor is the only inventory of what
an object holds; once fields stop appearing there, the inventory is gone and
the object's real shape can only be recovered by grepping.

Most of the time the thing you want is not a field at all. State that belongs
to one operation should be computed in that operation and passed to whatever
needs it. Parked on a long-lived object, it survives into the next operation
and becomes a bug that only appears on the second run.

## Don't add a parameter to spare the callers

```python
# Bad: the flag exists so the three existing call sites keep working.
def sync_group(group, members, strict=False):
    ...
```

A default parameter added for compatibility freezes the old behavior forever.
It also hides which callers chose that behavior and which ones nobody ever
updated. In a codebase you control you can see every call site, so change
them. The diff is larger and the result has one behavior instead of two.


A related signal: when a parameter list climbs past five or six, the
arguments are usually state that could not find a home, handed through by
hand. The cycle function in that sync loop took ten parameters, each one added
by a different fix that needed one more thing from its caller. The repair is
to give the group of values a name and pass that.

## Green tests do not license the addition

A suite that passes after an additive fix has told you one thing: the old path
still works. That was guaranteed before you ran it, because you did not touch
the old path. Green is evidence about the code you did not change.

The suite accretes the same way. In the loop described above, 34 test files
held 14,900 lines against 3,900 lines of code, with names like
`reconciliation_q3_test.go`, `offboarding_edgecases_test.go`, and five
separate `*_hardening_test.go` files. Each round of fixes got its own file,
and nothing was ever folded in or removed. The suite looked immaculate and
was describing a system nobody could hold in their head.

Put a new regression test in the file that already covers that behavior, and
name it for the behavior rather than the incident. A file named after a round
of fixes records when you learned something, which git already has.

## When layering is the right answer

Adding beside is correct in a few cases, and the difference is that you can
defend the choice:

- The code is vendored, generated, or otherwise not yours to edit.
- It is a published interface whose callers you cannot enumerate, where
  api-design's additive deprecate-then-remove path is the right answer.
- The real change is large and something is on fire right now.

In each case the layer gets a comment saying what it works around and what the
real change would be, so the next person finds a decision rather than
archaeology. The third case also gets a follow-up item; a temporary layer with
no record of being temporary is permanent.

What makes layering wrong is reaching for it because changing the original
felt risky, and then not checking whether it was.

## Remove the attempt that didn't work

When a fix doesn't work, take it out before trying the next one. Three
abandoned attempts left in the file read as three deliberate defenses to the
next person, and eventually one becomes load-bearing by accident. Across a
long session that residue is most of what makes a module grow.

## Signals in review

- A function whose name is another function's name plus a qualifier.
- A comment that exists to explain why this function is not the one above it.
- Lazy initialization of a field at the top of a method.
- A parameter with a default, added in the same commit as its only true caller.
- Two fields whose names differ only by a prefix.
- A bug-fix diff with no deleted lines.
- A new test file named after a ticket or a round of fixes.
- A reset of a counter or map inside an unrelated error path.

Any one of these can be fine on its own. Two in the same change is usually a
sign the fix went somewhere other than the place that was wrong, and it is
worth asking where that place was.

## When it already happened

Inherited code is the other half of this. The signals above read the same at
module scale: count the near-named families, count the fields the constructor
never mentions, and check whether the file's line count has ever gone down.
Several families, or a history with no dips in it, means the module accreted
rather than merely grew.

Unwinding one has an order, and the obvious order (open the big function
first) is the expensive one. Read
[references/repairing-accretion.md](references/repairing-accretion.md) before
you start on such a module, or when asked to clean up something that keeps
growing. Skip it when you are fixing one function you already understand: the
rules above cover that, and the reference is about sequencing work across a
whole module.
