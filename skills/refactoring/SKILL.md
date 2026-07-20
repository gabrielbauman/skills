---
name: refactoring
description: "Refactor safely: change structure while preserving observable behavior, keep the tests green after every step, and work in small reversible moves instead of one big-bang rewrite. Use whenever restructuring, renaming, extracting, inlining, or reshaping code without changing what it does, when a task needs preparatory cleanup before the real change, or when tempted to rewrite from scratch. Covers characterization tests for untested code and when not to refactor at all. Pairs with test-behavior (the green safety net), atomic-commits (the refactor in its own commit), and db-migrations (the same discipline for schemas)."
---

# Refactoring

A refactor changes how code is structured while keeping what it does exactly
the same. That constraint is the whole discipline, and it is the one agents
drop first. Three failure modes recur. A refactor and a behavior change land
in one diff, so a reviewer cannot tell the moved code from the changed code
and has to re-verify everything. A big-bang rewrite replaces the module in
one giant edit that is never green in between, so when it fails at the end
there is no last-working state to fall back to. And a "pure refactor" quietly
changes behavior: an edge case handled differently, an error now swallowed, an
order of operations flipped, shipped under a label that told the reviewer not
to look closely.

The through-line: a refactor is a bet that you can improve the structure
without anyone downstream noticing a difference. This skill is how you keep
that bet honest.

## Preserve observable behavior, exactly

The rule is strict: a refactor changes structure and nothing else. No new
feature, no bug fix, no behavior change, not even a "while I'm here"
improvement, mixed into the same step. Same inputs produce the same outputs,
the same errors, the same side effects, in the same order.

The reason is what the label buys. When a change is announced as a refactor, a
reviewer skims it, `git bisect` trusts it, and the next person builds on it
without re-reading it. Every one of those shortcuts is safe only if the label
is true. A behavior change hiding inside a refactor is the most expensive kind
of bug, because it ships past the people trained to wave refactors through.

This includes bugs you notice mid-refactor. Reproducing the old behavior faithfully
means preserving the bug too. If the code rounded wrong, the extracted function
rounds wrong the same way. Fixing it is a separate change, in a separate commit,
with a test that shows the fix, after the refactor lands. The small-prs skill
covers parking that fix instead of folding it in.

```python
# Refactor: extract the fee calculation. The original truncates with int(),
# which under-charges by a cent sometimes. Keep the truncation. Do not "fix"
# it here; that is a behavior change for its own commit.
def fee_cents(subtotal_cents):
    return int(subtotal_cents * FEE_RATE)
```

## Lean on tests as the safety net

The proof that behavior is preserved is a test suite that was green before and
is green after. Without it you are not refactoring, you are editing and hoping.
So the tests are a precondition, not an afterthought: run them first and
confirm they pass, so a red test after your change means your change and not a
mess you inherited.

When the code you want to refactor has no tests, add characterization tests
first. A characterization test pins down what the code *actually does* today,
not what it should do: you call it, observe the output, and assert exactly
that, bug-for-bug. It is not a statement that the behavior is correct, only
that it is what exists, so that if your refactor changes it, a test goes red.
Cover the paths you are about to touch and the edges around them. This is the
one case where anchoring an assertion to what the code currently returns is
right; the test-behavior skill's usual rule against that assumes you are
testing a contract, and here the current behavior *is* the contract you are
preserving.

```python
# Characterization test written before touching a gnarly untested parser.
# Not "this is correct" but "this is what it does now, and the refactor
# must keep doing it."
def test_parse_preserves_current_behavior():
    assert parse("a=1;b=2") == {"a": "1", "b": "2"}
    assert parse("a=1;;b=2") == {"a": "1", "b": "2"}   # blank segment ignored
    assert parse("a==1") == {"a": "=1"}                # splits on first =
    assert parse("") == {}
```

## Work in small, reversible moves

Refactor in a sequence of small steps, running the tests after each one,
rather than one large edit verified only at the end. Rename a symbol, run the
tests. Extract a function, run the tests. Change a call site, run the tests.

The reason is failure localization. When you make ten structural changes and
then run the tests, a red result tells you one of ten things broke and you get
to find which. When you make one change and run the tests, red points straight
at the move you just made, and `git diff` is small enough to eyeball or throw
away. Small steps keep you continuously close to a known-good state, so the
cost of being wrong is one `git checkout`, not an afternoon of untangling.

Modern tooling makes many of these moves mechanical and safe: an IDE's rename
or extract-method, `gofmt -r`, a codemod. Prefer those over hand-editing when
they exist, because a tool that understands the syntax will not miss a call
site or capture the wrong variable.

Big-bang rewrites are the opposite of this and the thing to resist. "Delete the
module and write it fresh" throws away the one asset you had, working behavior,
and replaces it with code that has never run. If a rewrite really is warranted,
stage it so the suite stays green throughout: build the replacement beside the
original, move call sites over one at a time, delete the old path only once
nothing calls it.

## Keep every step green

Each step in the refactor leaves the tree building and the tests passing. Not
"green at the end of the branch", green after each commit. A refactor that
parks the codebase in a broken intermediate state for six commits is a
big-bang rewrite wearing a series of small hats: if the branch stalls or gets
reverted midway, it strands everyone on a tree that does not build.

This is what makes a refactor safe to interrupt. You can stop after any step,
ship what you have, and the codebase is better and working, not half-migrated.

## Commit the refactor separately

The refactor is its own commit, or its own PR, apart from any behavior change
it prepares for. This is Kent Beck's "make the change easy, then make the easy
change": the preparatory refactor lands first, mechanical and skimmable, and
the behavior change lands on top, small and read closely.

The payoff is at review and at revert. A reviewer reads the refactor commit
knowing nothing should behave differently, so they check only that the
structure moved correctly; then they read the small behavior commit closely,
undistracted by moved code. And if the behavior change turns out wrong, it
reverts on its own without ripping out the cleanup. The atomic-commits skill
covers the mechanics of splitting a mixed tree; small-prs covers sequencing
the refactor and the feature as separate PRs.

```
# Bad: one commit
checkout: redesign discount engine and add seasonal promos

# Good: two commits, refactor first
checkout: extract DiscountEngine from Cart, no behavior change
checkout: add seasonal promo rules to DiscountEngine
```

## When not to refactor

Refactoring is not free and not always right.

- **No test coverage and no time to add it.** The safety net is the whole
  game. If the code is untested, you cannot write characterization tests right
  now, and the change is urgent, do the minimal targeted edit instead of
  restructuring blind. A refactor without a net is just untested rewriting.
- **The churn buys nothing.** Restructuring code that is about to be deleted,
  or that no one reads, or that works and is never touched, spends review
  attention and risk for no return. "It offends me" is not a reason; "I am
  about to change this and the current shape makes that change dangerous" is.
- **Mid-way through a behavior change.** Do not start reshaping structure while
  a feature edit is half-done in the tree. Finish or stash the behavior change,
  refactor on a clean base, then come back. Interleaving them recreates the
  unreviewable-diff failure mode this skill exists to prevent.

The test for whether a refactor is worth it: name the specific future change it
makes safer or easier, or the specific confusion it removes for the next
reader. If you cannot, park it.

## Anti-patterns

- The mixed diff: a rename or extraction tangled with a behavior change in one
  commit, so the reviewer cannot separate moved code from changed code.
- The big-bang rewrite: the module deleted and rewritten in one edit that is
  never green until the end, with no working state to fall back to.
- The behavior change in disguise: an edge case, an error path, or an ordering
  quietly altered under a "refactor" label that tells the reviewer not to look.
- Refactoring untested code with no characterization tests first, then claiming
  behavior is unchanged with nothing able to prove it.
- The aesthetic refactor: restructuring that serves taste, not any concrete
  upcoming change or removed confusion.
