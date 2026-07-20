---
name: pr-description
description: "Write the PR description itself: lead with what changed and why, give the reviewer a reading order and the parts to scrutinize, flag what is risky or uncertain, state what was deliberately left out, and link the issue it closes. Use whenever opening a pull request, merge request, or changelist, or when asked to write or rewrite a PR description or body. Pairs with small-prs (what goes in the branch), atomic-commits (commit order), and scoped-commits (each message); this skill writes the body on top of them."
---

# PR description

The description is the one part of a change written for the reviewer rather
than the machine. The diff says what changed; the commit messages say why each
piece changed. The description does the job neither can: it tells the reviewer
how to spend their attention. Miss that and the review gets slower and worse,
however good the code is.

Three failure modes cover almost every bad description. The first restates the
diff in prose ("Added a `retryUpload` function, updated `s3.go`, added a test")
and tells the reviewer nothing the diff does not already show. The second says
nothing at all: "various changes", a bare ticket link, or the template left
unfilled. The third writes plenty but buries the one hunk that deserves scrutiny
under a flat list that gives a risky migration the same weight as a rename. All
three push the cost of understanding onto the reviewer, who has less context
than the author and is the person the description exists to serve.

Agents hit these defaults because the diff is right there to paraphrase and the
prompt rarely asks for a description at all. Restating the diff feels like
diligence and costs nothing. The fix is to write for someone who will read the
code but has not yet, and does not know which twenty lines matter.

## Lead with what changed and why

The first two or three sentences carry the whole change: what it does, and the
reason it is needed. The reason is the part the diff cannot show. A reviewer who
knows why can evaluate whether the code achieves it; a reviewer who only sees
what is left checking the code against their own guess at the intent.

State the problem before the solution. "Uploads to S3 fail permanently on any
transient network blip, dropping user data; this adds retry with backoff so a
brief outage no longer loses the upload" tells the reviewer what to hold the
code against. "This PR adds retry logic to the S3 client" makes them reverse
engineer the motivation from the implementation.

Do not narrate the diff. Bad: "Changes: added `backoff.go`, modified
`s3.go` to call it, added `s3_retry_test.go`." Every line of that is visible in
the file list. Good: name the behavior change and the constraint that shaped it,
"retries up to 5 times over ~30s, then gives up and surfaces the original error
so the caller still sees the real failure."

## Give the reviewer a reading order

For anything past a couple of files, say where to start and in what order. The
reviewer does not know the load-bearing file from the incidental one, and the
file list is alphabetical or random, not narrative. A reading order is the
single highest-leverage thing a description does for a non-trivial change.

```
Start with backoff.go, the new retry helper, small and self-contained.
Then s3.go, where uploadObject now wraps its PUT in the helper; that is
the only real behavior change. The test file and the error-string tweaks
in errors.go are mechanical, skim them.
```

Point at what to focus on, and just as usefully, what is safe to skim. Telling
the reviewer that 300 of the 400 lines are a generated client or a mechanical
rename lets them spend their budget on the 100 that carry the decision. This
matters most when a change is irreducibly large: a description that separates
the load-bearing hunk from the noise makes a big PR reviewable, and its absence
makes it a rubber stamp. If the commits are already ordered to tell that story
(see atomic-commits), say "reviewable commit by commit" and let the history be
the reading order.

## Flag what is risky or uncertain

Say plainly what could go wrong and where you are unsure. This feels like
confessing a weakness; it is the opposite. Surfacing the risky hunk yourself
directs review to where it pays off and builds the trust that gets your next PR
read faster. Burying it does not make it safer, it just means the reviewer finds
it in production instead.

Name the specific thing, not a ritual disclaimer. Useful: "The cache
invalidation in `purge()` assumes single-writer; if two requests race here the
second could read a stale entry. I think the mutex covers it but I would like a
close look." Useless: "Please review carefully." Call out a migration that
cannot be rolled back, a query whose plan you have not checked under load, an
assumption you made because the ticket was ambiguous, an API you changed that
other services depend on. If a decision could reasonably have gone the other
way, say why it went this way; that is where a reviewer's disagreement is worth
having before merge, not after.

## State what is out of scope

List what a reader might expect this change to include but which it
deliberately leaves out. The reviewer noticing the download path still has no
retries does not know whether you missed it or parked it. One line settles it:
"Download retries are out of scope, filed as #418." Now the gap is a decision,
not an oversight, and the review does not stall on it.

This is where the scope contract from small-prs pays off a second time. The
"will not touch" list you wrote before coding becomes the out-of-scope section
now: the drive-by fixes you parked, the follow-ups you deferred, the tempting
adjacent cleanup you left alone. Link the parked items to their issues so a
reader can see they are tracked, not forgotten.

## Link the issue, do not retype it

Link the issue or ticket the change closes, with the keyword that
auto-closes it where the host supports it (`Closes #123`, `Fixes PROJ-456`).
The link gives the reviewer the full background on demand. But the description
must still stand on its own: a reviewer should understand what the change does
and why without leaving the page, because the issue may be stale, sprawling, or
access-controlled. Link for the audit trail and the deep context; summarize the
part that matters here. A PR body that is only a ticket link is the empty-body
failure with extra steps.

## What to leave out

- The diff as prose. If a sentence only restates a hunk the reviewer will read
  anyway, cut it. The description competes with the code for their attention;
  do not spend it on a worse copy of the code.
- Inflated summaries. "This robustly and comprehensively overhauls the upload
  pipeline" claims quality instead of describing the change. State what it does
  and let the reviewer judge, same house style as scoped-commits.
- A wall of implementation detail that belongs in code comments or commit
  bodies. The description is a map, not the territory.
- Screenshots or repro steps as a substitute for saying what changed. They
  supplement the prose; they do not replace it.

## Before and after

Bad, all three failure modes at once:

```
Add rate limiting

This PR adds rate limiting. Changes:
- Added RateLimiter class
- Added middleware
- Updated 9 handlers
- Added tests
- Also fixed some naming and a pagination bug

Various improvements to make the API more robust.
```

It restates the file list, buries a behavior change (the pagination fix) in a
bullet, claims "robust" without content, and gives no reading order or risk.

Good:

```
Add per-tenant rate limiting to the public API

Tenants can currently exhaust shared capacity with no ceiling, so one
noisy tenant degrades the API for everyone. This adds a per-tenant limit
of 100 req/min enforced in one middleware in front of the mux, returning
429 with a Retry-After header when exceeded.

How to review:
- Start with ratelimit/limiter.go, the token-bucket core, ~60 lines and
  the only place worth a close read.
- Then middleware.go, which wires it in front of the mux; the 9 handler
  files change only to drop their now-dead local checks (mechanical, skim).

Risk: the limiter keeps per-tenant state in memory, so limits reset on
deploy and are not shared across replicas. Acceptable for now (we run one
replica) but it means the ceiling is soft under a rollout. Flagging in
case that is a blocker.

Out of scope: admin visibility into current usage (#421) and limits on
internal endpoints (#422), both parked. The handler-naming cleanup the
ticket mentioned is left alone to keep this diff to one idea.

Closes #418.
```

The reader knows the intent, where to look, what to scrutinize, what was left
out and why, and the one thing that might block merge, all before opening a
single file.
