---
name: atomic-commits
description: "Decide what each git commit should contain: one self-contained, reviewable change per commit, with a mixed working tree split into an ordered series instead of one everything-commit. Use this skill every time you are about to commit and the working tree holds more than one logical change (a feature plus an unrelated fix, a rename plus behavior changes, the accumulated output of a long session), when asked to split, stage, reorder, or clean up commits, and when planning how to commit as you work. Complements scoped-commits, which covers only the message, and small-prs, which decides what belongs in the branch at all; this skill covers what goes in each commit."
---

# Atomic Commits

An atomic commit is one complete change: it does a single thing, does it fully,
and leaves the tree working. The default failure mode is the opposite, dumping
an entire work session into one commit because that is what `git add -A` does.

Three audiences depend on commits being atomic:

- Reviewers read commits one at a time. A commit that renames a function in
  forty files and also changes its behavior in one of them hides the behavior
  change inside the noise.
- `git bisect` assumes every commit builds and runs. One broken "WIP" commit in
  the range turns bisection from a binary search into archaeology.
- Reverting a bad change should be `git revert <sha>`. If the fix shipped
  tangled with an unrelated feature, reverting the fix rips out the feature too.

## What makes a commit self-contained

- It builds and passes tests on its own, not just in combination with the
  commits after it.
- It is one reviewable idea. Test: describe the commit in one sentence without
  "and" joining unrelated clauses. "add rate limiting to the API and fix a
  typo in the README" is two commits.
- It carries everything the change needs: a new function ships with its call
  site and, where the project has tests, its test; a config key ships with
  the code that reads it. A commit
  that adds dead code so a later commit can wire it up is not atomic either,
  unless the piece is independently useful (a helper, a schema).

Atomic means self-contained, not tiny. A 400-line commit implementing one
feature is atomic; a 5-line commit mixing two fixes is not.

## Splitting a mixed working tree

When the tree already holds several changes, split before committing:

1. Read the full diff (`git status`, `git diff`) and list the logical changes
   in it. Name each one; these become the commit subjects.
2. Order them so every commit stands on its own tree. Dependencies go first:
   the schema or config before the code that reads it, the helper before its
   callers, the mechanical rename or refactor before the feature built on the
   renamed code. Independent changes: smallest or least controversial first.
3. Stage one change at a time. `git add <paths>` when a change owns whole
   files, `git add -p` when one file mixes changes (`s` splits a hunk, `e`
   edits one). When hunks will not separate, or there is no interactive
   terminal, build the intermediate state instead: edit the file to how it
   should look after only the first change, stage it whole, commit, then
   restore the final content and continue. Review `git diff --cached`
   before each commit to confirm the staged diff is exactly the one change.
4. Verify the commit stands alone when the project has a fast check. With
   the intermediate-state technique the tree already matches the commit, so
   just run the check. Otherwise `git stash push --keep-index` hides the
   unstaged rest; build, test, commit, `git stash pop` (the pop can
   conflict when later hunks touch committed lines; resolve toward the
   final content). Skip the dance when the split is trivially safe (docs,
   isolated files), but never knowingly commit a tree that does not build.

If two changes are so interleaved that hunk-level splitting keeps breaking,
that is a sign they are really one change; commit them together rather than
manufacturing a split.

## When to split and when not to

Split:

- Mechanical change plus behavior change. Rename in one commit, behavior in
  the next; the rename commit is huge but skimmable, the behavior commit is
  small but read closely.
- Refactor plus feature. First a commit that only rearranges code with no
  behavior change, then the feature the refactor enabled.
- Anything unrelated that wandered into the tree: a typo fixed in passing, a
  dependency bump, a lint cleanup.

Do not split:

- A function and its test. The test is how the reviewer knows the function
  works; separated, the first commit is unverified and the second is noise.
- One logical change across file boundaries. Committing "the model" and then
  "the handler" for one feature produces two commits that each fail to build.
- By size alone. Splitting a coherent change to make commits look small
  produces a series where no single commit makes sense.

## Fixes discovered along the way

Mid-task you notice something broken: a typo, a latent bug, a missing null
check unrelated to your work. Whether to fix it in this branch at all is a
scope decision, and the small-prs skill owns it: its default is to
park the fix (file an issue, list it as a follow-up) rather than grow the
branch. When the fix does belong here, because it blocks your change or no
scope contract is in play, commit it separately, before or after the main
series, with its own message saying what was wrong. Smuggling it into the
feature commit hides it from review, and six months later `git log` on that
line explains the fix with a commit about something else.

## Anti-patterns

- The everything-commit: `git add -A` at the end of a session, one commit
  titled after whichever change the author remembered.
- WIP chains: `wip`, `more wip`, `fix`, `actually fix`. Fine locally as
  checkpoints, but squash or rewrite (`git rebase -i`, `git commit --fixup`)
  before anyone else sees the branch.
- Tangled refactor and feature: "restructure auth module and add SSO" as one
  commit, where the reviewer cannot tell moved code from new code.
- The smuggled fix: an unrelated one-line bug fix buried in a 400-line
  feature commit.
- Split by file instead of by change, leaving intermediate commits that do
  not build.

## Example

A session's working tree holds: a new `retry` helper in `util/`, retry calls
added to the S3 client, a rename of `Fetch` to `FetchObject` across the
package, and a typo fix in an unrelated README. That is four commits:

1. the README typo fix (unrelated, out first)
2. the rename, mechanical, no behavior change
3. `util`: add the retry helper with its tests
4. the S3 client change that uses it

Each builds alone, each reverts alone, and a reviewer reads four small stories
instead of one tangle.
