---
name: why-comments
description: "Write code comments that explain why, never what, and strip comment noise from existing code. Use whenever writing code, editing code that has comments, writing docstrings or API docs, or asked to clean up, reduce, or improve comments. Covers when a comment is warranted at all (constraints, invariants, workarounds, rejected alternatives) versus noise (narrating the next line, section banners, restating names), reviewer-directed comments that go stale at merge, matching the codebase's comment density, TODO hygiene, and the rule for comments you don't understand."
---

# Why-comments

Code is the behaviour. A comment that restates it says nothing and rots: the
code gets edited, the comment doesn't, and now the file lies. The only
comments worth writing carry what the code cannot: the reason, the
constraint, the history. Agents fail in both directions at once, narrating
every step ("// increment the counter") while leaving the actual trap (the
API that returns milliseconds where everything else uses seconds)
undocumented. Default to zero comments, then add back only the ones below.

## When a comment is warranted

- A non-obvious constraint or invariant: "callers hold the lock", "must stay
  in sync with the enum in proto/status.proto", "list is sorted, bisect
  depends on it".
- A workaround, with a link to what it works around: the upstream bug, the
  broken client version, the platform quirk. Without the link, the next
  reader can't tell when it's safe to remove.
- Why an obvious-looking alternative was rejected: "regex here backtracks
  catastrophically on real inputs, hence the hand-rolled parser". This is the
  comment that stops the next person from "simplifying" the code back into
  the bug.
- Units, formats, or ranges the type system can't express: "timeout in
  milliseconds", "amount in cents", "0.0 to 1.0 inclusive".

If none of these apply, and the code still seems to need a comment to be
understood, the fix is usually a better name or a smaller function, not
prose.

## What is noise

- Narrating the next line: `// increment the counter` above `counter += 1`.
- Section banners: `// ---- helpers ----`, `// Validation section`.
- Restating a name: `// UserService handles users` on `class UserService`.
- Comments addressed to the reviewer instead of the next reader: "fixed the
  bug here", "per feedback", "new function to handle retries", "changed from
  the old approach". These describe the diff, not the code; they are stale
  the moment the PR merges. If the change history matters, it belongs in the
  commit message.
- Comments explaining why your change is correct. Same problem: that is an
  argument to the reviewer, and it is noise to everyone after.

## Bad, then good

```python
# Loop through the retries and try the request
for attempt in range(5):  # 5 retries
    resp = fetch(url)
    if resp.ok:
        break
    time.sleep(2 ** attempt)  # exponential backoff
```

```python
# Upstream rate-limits bursts; 5 tries with backoff covers their
# longest observed throttle window (issue #482).
for attempt in range(5):
    resp = fetch(url)
    if resp.ok:
        break
    time.sleep(2 ** attempt)
```

Three noise comments deleted, one constraint added. The good version has
fewer comments and more information.

## Docstrings and API docs

A docstring is a contract, not narration: what the function promises
(arguments, return value, errors raised, side effects, thread-safety), never
how the body works. "Uses a dict internally" is implementation detail that
breaks the doc when the implementation changes. Follow the codebase's
existing convention for which symbols get docstrings; a private helper whose
name says everything doesn't need one just because a linter can count.

## Match the codebase

Comment density and idiom are house style like anything else. In a sparsely
commented codebase, a fully narrated function is as out of place as a
reformatted file. Match what surrounds your change: density, tone, doc
comment format, tag conventions (`TODO(name):`, `FIXME:`, `# NOTE:`).

## TODOs

A TODO with no owner and no issue link is a wish. Write `TODO(alice): ...`
or `TODO(#482): ...` so it can be chased, or file the issue and skip the
comment. Never leave a TODO describing work the user asked you to finish
now.

## Editing existing code

- Remove noise comments in code you are already touching; leave the rest of
  the file alone. Comment cleanup across untouched code is its own change.
- Some comments are read by tools, not people: linter and formatter
  directives (`# noqa`, `eslint-disable-next-line`), coverage pragmas,
  process tags like ADR references. They say nothing to a reader and are
  still load-bearing; leave them unless you mean to change what they
  control.
- Update any comment your edit makes wrong. A stale comment is worse than
  none.
- Never delete a comment stating a constraint you don't understand. It may
  be the only record of why the code survives production. If it looks wrong,
  say so to the user instead of removing it.
