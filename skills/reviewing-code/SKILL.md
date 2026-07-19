---
name: reviewing-code
description: "Review a pull request the way a good colleague does: understand the intent before judging the diff, separate blocking defects from nits, ground every blocking comment in a defect or a written rule rather than taste, ask real questions instead of asserting guesses, and leave style to the formatter. Use whenever reviewing someone else's PR, MR, branch, or diff, when asked to leave review comments, approve, or request changes, or when drafting feedback on another person's code. Covers reading order, severity triage, nit labeling, comment tone, when to request changes versus approve with comments, keeping review scope inside the PR's scope, and reviewing promptly in one batch. Pairs with branch-review, which runs the multi-agent version of this sweep before merge, pr-description, the author's side of the same exchange, and small-prs, which keeps the thing under review reviewable."
---

# Reviewing code

Review fails in two opposite ways. The rubber stamp ("LGTM", ship it)
catches nothing and teaches the author nothing. The fire hose leaves
thirty comments of equal weight, so the one about the race condition
drowns among twenty-nine about naming, and the author, unable to tell
which comments matter, either fixes everything resentfully or argues
everything. Both fail the same way: the review never sorted what it
found.

A useful review answers three questions, in order: does this change do
what it intends, safely? What must change before merge? What is worth
mentioning but not worth blocking? Everything below serves those three.

## Read for intent first

Before reading a line of the diff, read the PR description and the
linked issue. You are reviewing whether this change achieves its stated
intent, not whether it matches the change you would have written. A
solution that differs from yours is not a defect; a solution that fails
its own goal is.

Then read the diff in reading order, not file order: entry point, core
change, tests. If the author gave a reading order in the description,
use it. Reviewing files alphabetically means reviewing the config churn
before the logic it serves, and judging pieces before you know the
shape.

If you cannot work out what the change is for, that is the first
comment, and it blocks: a reviewer who cannot determine intent cannot
review, and the next reader of the code is in the same position.

## Triage every comment

Sort each comment into one of three bins before posting, and label it
so the author can sort too:

- **Blocking**: correctness bugs, security holes, data loss, breaking
  API changes, missing tests for risky paths. Merging with this defect
  costs more than another round trip.
- **Non-blocking suggestion**: a real improvement the author may take
  or leave. Say so explicitly: "not blocking, but".
- **Nit**: preference with low stakes. Prefix it `nit:` and expect
  nothing. Two nits on the same pattern is enough; do not mark all
  fourteen occurrences.

The prefix is not politeness theater. It is routing information: the
author fixes blockers first, considers suggestions, and batches or
skips nits. A review where everything implicitly blocks is a review
where nothing visibly does.

## Ground blocking comments in defects, not taste

Every blocking comment cites either a concrete defect (here is the
input that breaks it) or a written rule (the style guide, the lint
config, the team's agreed conventions, a documented invariant). "I
would not have done it this way" is not grounds to block; it is a
suggestion at most. If you find yourself blocking on taste, either
find the defect underneath the discomfort or downgrade the comment.

This is the same standard branch-review holds its agents to, and it is
what keeps review from becoming a negotiation with whoever reviews
loudest.

## Ask when you do not know

When you suspect a problem but have not confirmed it, ask the question
instead of asserting the defect: "what happens here when `items` is
empty?" If the author answers "the caller guarantees non-empty, checked
at parse time", the review moved knowledge without a wrong accusation.
If they cannot answer, they just found the bug themselves, which lands
better and teaches more than being told.

The question must be genuine. A rhetorical "did you even test this?"
is an assertion wearing a question mark, and it reads that way.

## Critique the code, not the author

Comments describe what the code does, not what the author did. "This
loop rereads the file on every iteration" gives the author a fact to
fix. "You're rereading the file every time" makes it about them, and
"why would you read it in a loop?" invites a defense instead of a fix.
The diff is the subject of every sentence; the author never is.

When the fix is short and you are sure of it, include it as a
suggestion block or a concrete snippet. A comment that shows the fix
costs the author one click; a comment that gestures at it costs a
guessing round trip.

## Leave style to the tools

If a formatter or linter could catch it, it is not review material.
Commenting on brace placement or import order spends review attention,
the scarcest resource in the process, on what a machine does for free.
The correct comment is the one that proposes adding the lint rule, once,
in its own issue; after that the rule reviews for you.

The exception is style the tools cannot see: a misleading name, a
comment that contradicts the code, a public API that reads wrong. Those
are substance wearing style's clothes, and they are fair game.

## Stay inside the PR's scope

Review the change that was made, not the file it was made in. The
legacy mess adjacent to the diff was there yesterday and will be there
tomorrow; demanding its cleanup as a condition of this merge holds the
author hostage for a debt they did not incur. File the follow-up issue
and link it in a non-blocking comment.

The exception: the change actively worsens something (copies a broken
pattern, deepens a wrong abstraction). Making things worse is in scope
even when the surrounding mess is not.

## The verdict

End with an explicit disposition, and make it match the comments:

- **Approve** when nothing blocks, even with suggestions and nits
  outstanding. Trust the author to handle non-blocking feedback; do not
  demand a re-review round to watch them rename a variable.
- **Approve with comments** when the required fixes are ones you do not
  need to see again: mechanical, unambiguous, low-risk.
- **Request changes** only when a blocking comment exists, and say
  exactly what unblocks: "blocking on the missing owner check in
  `get_invoice`; everything else is take-it-or-leave-it."

An ambiguous verdict ("some thoughts inline") leaves the author unsure
whether they may merge, which stalls the change as surely as a block.

## Speed is part of quality

A thorough review tomorrow loses to a good review in two hours. The
author is blocked, context evaporates, and rebases pile up while the
review waits. Review promptly, and post the whole review in one batch
rather than trickling comments as you read; a trickle makes the author
respond to your stream of consciousness, half of which the rest of the
diff answers.

Match depth to risk, the way branch-review scales its fleet: a doc fix
gets a skim and a stamp; an auth change gets line-by-line attention. A
fixed-depth review over-invests in the trivial and under-invests in the
dangerous.

## Bad, then good

The same finding, twice:

> Why are you doing this in a loop?? This should obviously be a bulk
> insert, this will never scale. Also rename `d` to something sensible,
> and this whole file could use a cleanup honestly.

> Blocking: this inserts one row per iteration, so a 10k-item import
> issues 10k round trips; on staging data this path takes ~40s and
> holds the transaction open throughout. `insert_many` (used in
> `import_users` for the same shape) does it in one. nit: `d` could be
> `deposit`. The wider cleanup in this file I've filed as #482 so it
> doesn't block you here.

The first is unanswerable except defensively, and blocks on taste. The
second cites the defect and its cost, points at an existing in-repo
fix, labels the nit, and moves the out-of-scope work where it belongs.
