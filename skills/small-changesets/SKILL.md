---
name: small-changesets
description: "Keep each branch or PR down to one reviewable idea by deciding scope before writing code: state a scope contract (what the change will and will not touch), park everything discovered along the way instead of fixing it in passing, and split big asks into a planned series of self-contained steps (refactor first, then the small behavior change on top). Use this skill when starting any coding task that could grow beyond a few files, when planning a branch or PR, when a prompt bundles extra work ('while you're in there, also...'), when you notice unrelated problems mid-task, when asked to keep PRs small or split work into reviewable pieces, and before opening any PR to check the diff against the declared scope. Complements atomic-commits, which splits a finished tree into commits; this skill decides what goes into the branch at all."
---

# Small Changesets

A changeset is the unit a reviewer approves: the branch, the PR, the patch.
Google's [small-CL
guidance](https://google.github.io/eng-practices/review/developer/small-cls.html)
defines the target: one CL is one self-contained change, and small CLs are
reviewed faster, more thoroughly, and with fewer bugs slipping through. The
SmartBear study of code review at Cisco put a number on the ceiling: defect
detection falls off sharply beyond about 400 changed lines per review.

Agents miss this target by default, because nothing pushes back. A human
author feels review cost and trims; an agent pays nothing to add one more
thing. So it fixes a bug it noticed in passing, renames a confusing variable
while it is in there, scaffolds helpers and tests the task never asked for,
and treats one prompt as one PR no matter how big the prompt was. Each
addition is locally defensible. The sum is a diff no one can review.

Splitting after the fact rarely rescues it. The reviewable unit is a
narrative step ("first make the helper, then use it"), and a finished diff
does not contain the narrative; carving it along file or layer boundaries
produces fragments that only make sense together, which is no better than
the monolith. This is why stacked-diff cultures (Gerrit, Linux kernel patch
series, Graphite) plan the series before the work: splits planned up front
are self-contained by construction. So the rules here apply before and
during coding, not at commit time. For turning a finished tree into commits,
see the atomic-commits skill; for the commit message, scoped-commits.

## The scope contract

Before writing code, state what the change will and will not touch:

```
Scope: add retry with backoff to the S3 upload path.
Will touch: internal/storage/s3.go, its tests, one new util/backoff helper.
Will not touch: other storage backends, the download path, unrelated
lint or naming issues in files I pass through.
```

Two or three lines is enough. The point is to make scope a decision instead
of an accumulation. Everything you then discover along the way, and you will
discover things, gets parked rather than done: file an issue, add it to the
task list, or list it under "follow-ups" for the user. Drive-by work is
where most bloat comes from, so this is the highest-leverage rule in this
skill. The only exception is a discovery that blocks the declared change
itself; that goes in, and the contract gets updated to say so.

Parking is not dropping. A parked item with a file, a line, and one sentence
of context is a five-minute follow-up PR later. Silently fixing it now costs
the reviewer more than that.

## Decomposing a big ask

When the ask cannot fit one reviewable change, plan the series before
writing any code. Kent Beck's ordering: "make the change easy, then make the
easy change." The preparatory refactor lands as its own PR, mechanical and
skimmable; the behavior change lands on top, small and read closely.

Each step in the series must be:

- green: builds and passes tests on its own
- independently valuable: a reader can say what this step improves without
  reading the next one
- independently revertible: backing it out does not strand the steps
  already landed

"Part 1 of 5 that does nothing by itself" fails the second test and is as
bad as the monolith; it just spreads the unreviewable thing across five
PRs. If a step is pure scaffolding, fold it into the step that uses it or
find a cut where it stands alone (a helper with tests and one real call
site does; an unused interface does not).

One prompt is not one PR. A prompt that asks for a refactor plus a feature
plus a fix is asking for a series, even though it arrived as one message.

## Budget review effort, not lines

The 400-line figure is about attention, not arithmetic. A 1500-line
mechanical rename is skimmable in minutes; 300 lines of dense behavior
change in a concurrency path can exhaust a reviewer alone. Budget the
second kind, and never mix the two: a rename or format sweep inside a
behavior change hides the twenty lines that matter inside noise the
reviewer has been trained to skim. Mechanical changes get their own PR
(and, per atomic-commits, their own commit even within a PR).

The working test: one PR is one idea a reviewer can hold in their head. If
describing the PR takes "and" joining unrelated clauses, it is two PRs.

## The checkpoint before opening the PR

Before opening the PR, run `git diff --stat` and read it against the scope
contract. Every file outside the contract is a question: either it was
needed and the contract should have said so, or it is drive-by work. Pull
drive-by work out (`git checkout main -- <path>` for whole files, or move it
to its own branch) and park it. This is the moment the contract earns its
keep; without the checkpoint it is just a comment that scrolled away.

## When the change is irreducibly large

Some changes cannot shrink: a generated-code refresh, a vendored dependency
bump, a migration that must be atomic. Then the PR description becomes a
review map:

- where to start reading, in what order
- which parts are generated or mechanical and safe to skim
- which fifty lines carry the actual decision and deserve the close read

Structure the commits so the PR can be reviewed commit by commit
(atomic-commits covers how), and say in the description that this is the
intended reading. A large PR with a map is reviewable; a large PR that
opens with "various changes" is not.

## Anti-patterns

- The "and also" PR: the asked-for fix, and also a rename, and also a lint
  sweep, and also a drive-by bug fix. Each "and also" is its own changeset.
- Splitting by directory or layer instead of narrative step: "part 1: the
  models, part 2: the handlers" produces fragments that cannot be reviewed
  or reverted alone.
- The part-N-that-does-nothing: dead scaffolding landed so a later PR can
  wire it up.
- The opportunistic sweep: renames or reformatting folded into a behavior
  change because the files were already open.
- One prompt equals one PR: sizing the changeset by how the work arrived
  instead of how it will be reviewed.

## Worked example

The ask: "add per-tenant rate limiting to the API, and while you're in
there the handler naming is a mess, feel free to clean it up."

Bad: one branch with the limiter, a rename of nine handlers, a new
middleware framework "for future limits", and a fix for an off-by-one
noticed in pagination. Four ideas, 2100 lines, one PR titled "add rate
limiting". The reviewer skims all of it, which means reviewing none of it.

Good: a contract and a planned series.

```
Scope: per-tenant rate limiting on the public API.
Will not touch: handler naming (parked), pagination bug (parked, filed
as an issue with the failing case), internal admin endpoints.

PR 1: extract request-context helper so handlers share one place to
      read tenant identity. Refactor only, no behavior change.
PR 2: add the limiter with tests, wired to the helper, enforcing on
      the two highest-traffic endpoints.
PR 3: extend enforcement to the remaining endpoints and document the
      limits.
```

Each PR is green, valuable, and revertible alone. PR 1 is the Beck move:
it makes PR 2 a small diff instead of a nine-handler surgery. The rename
and the pagination fix become their own follow-ups, each a small PR a
reviewer can approve in one pass, instead of stowaways in this one.
