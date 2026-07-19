---
name: git-recovery
description: "Reshape and recover git history safely: interactive rebase to reorder, squash, split, and reword commits; the fixup plus autosquash workflow to amend an earlier commit; reset --soft/--mixed/--hard and when each is right; --force-with-lease instead of --force; the reflog as the undo of last resort; and git revert for undoing an already-shared commit. Use this skill when history is messy and you want to clean it up before review, when you need to undo a commit, reset, merge, rebase, or a bad amend, when you have lost a commit or branch and need it back, when a rebase or force-push is involved, or when you are worried about clobbering a teammate's work. Covers the non-interactive rebase alternatives for agent environments without a terminal editor. Complements atomic-commits, which decides what each commit should contain; this skill reshapes existing history to get there, and rescues you when a rewrite goes wrong."
---

# Git Recovery

History is not read-only, and treating it as if it were produces two failure
modes. The timid one: commits stay messy, WIP chains ship to review, and the
smallest fix means a new commit on top because rewriting feels dangerous. The
reckless one: `git reset --hard` and `git push --force` fired without a second
thought, wiping uncommitted work or overwriting a teammate's push. Both come
from the same gap, not knowing what git actually does under these commands.

The governing fact that makes rewriting safe: **anything you have committed is
almost impossible to truly lose.** A commit is reachable from the reflog for at
least 90 days after nothing points to it, so a botched rebase or a bad reset is
recoverable. What is genuinely lost is what was never committed: uncommitted
changes destroyed by `reset --hard` or `checkout` are gone with no reflog entry.
Commit early, commit often, and rewrites become reversible experiments.

## The golden rule: rewrite only your own unshared history

Rewriting history changes commit hashes. Every commit after the edited one gets
a new hash, so anyone who already pulled the old commits now has a diverged
copy, and their next pull turns into a merge conflict against history that no
longer exists.

- **Safe to rewrite:** commits that live only on your local branch, or on a
  remote feature branch that nobody else has based work on. Your own unmerged
  PR branch is the normal case.
- **Never rewrite:** `main`, `master`, `develop`, release branches, or any
  branch others build on. Once a commit is on a shared branch, undo it with a
  new commit (`git revert`), not by rewriting.

When unsure whether someone pulled your branch, assume they did and use
`revert`. The cost of an unnecessary revert is one extra commit; the cost of a
force-push that clobbers a teammate is their lost work and an afternoon of
recovery.

## Interactive rebase: reorder, squash, split, reword

`git rebase -i <base>` opens an editor listing the commits after `<base>`, one
per line, oldest first. You change history by editing that list. Common `<base>`
choices: `HEAD~5` for the last five commits, `main` for everything on your
branch since it forked.

The command keyword on each line does the work:

- `reword` (`r`) to change a commit message without touching its content.
- `squash` (`s`) folds a commit into the previous one, combining both messages;
  `fixup` (`f`) does the same but discards the squashed commit's message.
- `edit` (`e`) stops the rebase at that commit so you can amend it or split it.
- `drop` (`d`), or just deleting the line, removes the commit entirely.
- Reorder by moving lines; the new order is the new history.

**Splitting one commit into two** with `edit`: mark the commit `edit`, and when
the rebase stops on it, undo the commit but keep its changes staged-then-unstaged:

```
git reset HEAD^          # move HEAD back one, leave changes in the working tree
git add -p               # stage the first logical piece
git commit -m "first piece"
git add -A               # stage the rest
git commit -m "second piece"
git rebase --continue
```

If a rebase hits a conflict, resolve the files, `git add` them, and
`git rebase --continue`. To bail out and return to exactly where you started,
`git rebase --abort`.

### When there is no interactive editor

Some agent and CI environments have no interactive terminal, so `rebase -i`
cannot open its editor. Use the non-interactive equivalents:

- **Reword the latest commit:** `git commit --amend -m "new message"`.
- **Reword an earlier commit or reorder:** drive the rebase with a scripted
  editor. `GIT_SEQUENCE_EDITOR` edits the todo list, `GIT_EDITOR` edits messages.
  For example, to squash the top two commits without a prompt:
  ```
  GIT_SEQUENCE_EDITOR='sed -i "2s/^pick/fixup/"' git rebase -i HEAD~2
  ```
- **Amend an earlier commit:** the fixup + autosquash flow below, run with
  `--autosquash`, needs no interaction at all.
- **Drop or reorder mechanically:** `git rebase --onto` reroots a range onto a
  new base, letting you excise a commit without an editor.

Prefer these scripted forms in automation; they are deterministic and leave a
clear command in the history of what you ran.

## Fixup and autosquash: amend an earlier commit

You are three commits deep and realize commit two needs a one-line correction.
Do not add a "fix typo in commit two" commit that a reviewer has to mentally
apply backward. Instead:

```
git add <the fix>
git commit --fixup <sha-of-commit-two>
git rebase --autosquash -i main
```

`--fixup` creates a specially-marked commit; `--autosquash` reorders it next to
its target and marks it `fixup` automatically, so the rebase folds it in and the
final history looks as if commit two was right all along. `git commit --squash`
is the same but lets you extend the target's message. Set
`git config --global rebase.autosquash true` so `-i` always honors fixups.

For the single most recent commit, skip all of this: `git commit --amend` folds
staged changes into `HEAD` directly.

## reset: --soft, --mixed, --hard

`git reset` moves the current branch pointer to a target commit. The flag
controls what happens to your staged and working changes, and confusing them is
how people lose work:

- `--soft`: move the branch only. Staged and working files untouched, so the
  undone commits' changes sit staged, ready to recommit. Use it to **uncommit
  while keeping the work**, for example to squash the last three commits into
  one: `git reset --soft HEAD~3 && git commit`.
- `--mixed` (the default): move the branch and unstage, but keep working-tree
  changes. Use it to **redo staging from scratch**, for example to unstage
  everything: `git reset HEAD`.
- `--hard`: move the branch and discard both staged and working changes to
  match the target. This is the destructive one. Use it only to **throw work
  away on purpose**, for example `git reset --hard origin/main` to make your
  branch identical to the remote.

Before any `--hard`, ask what uncommitted work it will destroy, because that
work has no reflog entry and cannot be recovered. If you might want it later,
`git stash` first.

## Force-pushing: --force-with-lease, never --force

After rewriting a branch you have already pushed, the remote rejects a normal
push because your history diverged from it. You must force. But plain
`git push --force` overwrites the remote unconditionally: if a teammate pushed
in the meantime, their commit is gone.

Always use `git push --force-with-lease` instead. It force-pushes **only if the
remote is still at the commit you last saw**. If someone else pushed, the lease
fails and git refuses, telling you to fetch and look before you clobber. It
costs nothing over `--force` and it is the difference between rewriting your own
history and destroying someone else's. Make it the only force-push you ever
type.

## The reflog: undo of last resort

`git reflog` records every position `HEAD` has held: every commit, checkout,
reset, rebase, and merge, with an entry like `HEAD@{2}`. When a rewrite goes
wrong and a commit seems gone, the reflog is how you get it back, because the
old commit is still there; only the branch pointer moved off it.

**Undo a bad reset or rebase:** find the entry from just before the mistake and
reset back to it.

```
git reflog                    # read the list; find the good state, say HEAD@{5}
git reset --hard HEAD@{5}     # move the branch back to it
```

**Recover a deleted branch:** its tip commit is still in the reflog (or via
`git fsck --lost-found`). Find the sha and re-point a branch at it:

```
git reflog                          # or: git fsck --no-reflogs --lost-found
git branch recovered <sha>
```

**Recover a commit dropped by a rebase:** same idea, find the sha in the reflog
and either `git cherry-pick <sha>` it back onto your branch or branch from it.

The reflog is local and per-repository; it does not travel with a clone or a
push. It is your safety net, not a teammate's. This is the concrete reason the
opening rule holds: the fix for a mistake is almost always "find the sha in the
reflog and point something at it," not "recreate the lost work."

## revert: undoing what others have already pulled

When a bad commit is already on a shared branch, you cannot rewrite it away
without breaking everyone downstream. `git revert <sha>` creates a **new** commit
that applies the inverse of the bad one, undoing its effect while leaving history
intact and moving forward. Everyone's next pull is a clean fast-forward.

```
git revert <sha>              # one commit
git revert <oldest>..<newest> # a range, newest undone first
git revert -m 1 <merge-sha>   # a merge commit, keeping mainline parent 1
```

Reverting a merge is a known trap: git needs `-m` to know which parent is the
mainline, and a reverted merge cannot simply be re-merged later without also
reverting the revert. Note that in the commit message when you do it.

The rule of thumb: **reset (or rebase) to undo local, unshared history; revert
to undo shared history.** Choosing reset for a commit others have pulled is
exactly the mistake the golden rule warns against.

## Quick reference

- Wrong message on the last commit: `git commit --amend`.
- Wrong message on an earlier commit: `rebase -i` with `reword`, or scripted
  `GIT_EDITOR`.
- Forgot a file in the last commit: `git add <file> && git commit --amend --no-edit`.
- Uncommit but keep the changes: `git reset --soft HEAD~1`.
- Unstage everything: `git reset` (mixed is the default).
- Throw away all uncommitted changes: `git reset --hard` (destroys work, no undo).
- Fold a fix into an earlier commit: `git commit --fixup <sha>` then
  `git rebase --autosquash -i <base>`.
- Undo a shared commit: `git revert <sha>`.
- Recover from a botched rewrite: `git reflog`, then `git reset --hard HEAD@{n}`.
- Push a rewritten branch: `git push --force-with-lease`, never `--force`.
