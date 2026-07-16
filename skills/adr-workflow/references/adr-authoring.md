# Authoring ADRs

Read this before drafting an ADR. The format rules are enforced by the
tooling; the judgment rules here are what make the ADR set worth reading.

## Template

```markdown
# ADR-NNNN: Short imperative title

- Date: YYYY-MM-DD
- Supersedes: ADR-NNNN, ADR-NNNN   <- only when superseding

## Context

Why a decision is needed. The forces: requirements, constraints, what goes
wrong without a decision. Written so a reader with no conversation history
understands the problem.

## Decision

The decision itself, stated precisely enough that conformance is checkable.
Exact formats, exact behaviours, exact boundaries. "The CLI prints exactly
`Hello, NAME!` followed by a newline" — not "the CLI greets the user".

## Consequences

What follows: what becomes easier, what becomes harder, what future changes
this constrains, what code must now exist or change.
```

Format rules the linter enforces: filename `NNNN-kebab-slug.md`, contiguous
numbering from 0001, H1 matching `# ADR-NNNN: Title`, a `- Date:` line, the
three sections, and **no Status line** — a written status would have to be
edited when superseded, violating immutability, so status is always computed
from `Supersedes:` references instead.

## Atomicity

One ADR = one independently supersedable decision. The test while drafting:
**"would anyone ever want to replace only part of this?"** If yes, split it.

Why it matters: supersession is total (an ADR is replaced whole or not at
all). If an ADR bundles five decisions and one changes, the superseding ADR
must restate the other four — every bundled decision is duplication you'll
pay for later. Atomic ADRs make supersession cheap and make the live spec
readable decision-by-decision.

**Too coarse:** "ADR-0007: Authentication" deciding token format, expiry,
refresh policy, and storage. Expiry will change independently of format.

**Right:** four ADRs — token format; token lifetime; refresh policy; token
storage. Each supersedable alone.

**Too fine:** "ADR-0009: Access token lifetime is 15 minutes" and
"ADR-0010: Refresh token lifetime is 30 days" *if* these would only ever
change together as one lifetime policy. Aspects of one decision belong
together; the unit is the decision, not the sentence.

A judgment call, not a rule of thumb about length: a one-line decision can be
a whole ADR, and a page can still be atomic.

## Supersession

- Point backwards only: the new ADR's `Supersedes:` line names the old one(s).
  The old file is never touched — its superseded status is computed.
- **Total, with restatement.** If ADR-0012 changes one aspect of ADR-0007,
  ADR-0012 restates everything from ADR-0007 that still stands. After the
  spec commit, ADR-0007 is entirely dead and ADR-0012 is complete on its own.
  Nobody should ever need to read a superseded ADR to know the current spec
  (only to understand history).
- One superseding ADR may supersede several old ones (consolidation), but an
  ADR can only be superseded once — to change a superseded decision again,
  supersede the *live successor*.
- Removing behaviour is also supersession: write an ADR whose decision is
  that the behaviour no longer exists, superseding the ADR that specified
  it. Specified absence is still specification — deleting the code without
  that ADR would leave a dead decision live in the spec.
- Never supersede an ADR that is already superseded; the linter rejects it.
- After the spec commit, `validate` lists every code tag still pointing at
  the superseded ADR. That list is the implementation checklist: migrate the
  code, retag with the successor, commit with `Implements:` the successor.

## Scoping a feature into ADRs

A user-facing feature usually decomposes into a few atomic decisions. "Add
`--shout` flag" might be one ADR (flag behaviour) or two (flag behaviour;
general flag-parsing convention) depending on whether a convention decision
is being made for the first time. During design, name the decisions you're
about to make; each one that could change independently is its own ADR.
Commit them together in one spec commit if they land together — a spec commit
may contain several new ADRs.

## Reverse-engineered ADRs (onboarded repos)

In a repo onboarded with a baseline ADR, some ADRs record decisions that were
made long before the ADR set existed — written when a task touches
grandfathered behaviour, or during an optional survey of load-bearing
decisions. Rules for writing them honestly:

- The Context section must say the decision was reverse-engineered from code
  (name the baseline commit) and mark the rationale as inferred or unknown.
  Never invent a rationale; a record that guesses silently cannot be trusted
  at all, and trustworthiness is the entire point of the set.
- Carve-out ADRs carry no `Supersedes:` line for the baseline — the baseline
  stays live and simply covers less. Supersession works normally between
  explicit ADRs: changing an already-extracted decision supersedes the
  extraction ADR.
- Only the graduation ADR supersedes the baseline, and only when nothing
  meaningful remains grandfathered.
- The user approves each reverse-engineered ADR before it is committed; they
  may know the real rationale where you can only infer it.

## What is NOT an ADR

- Proposals under discussion — those live in the conversation with the user.
  The repo contains only accepted decisions.
- Implementation notes, TODOs, status reports, changelogs.
- Restatements of code structure ("we have a module named X"). ADRs specify
  behaviour and the decisions behind it, not narrate the codebase.
