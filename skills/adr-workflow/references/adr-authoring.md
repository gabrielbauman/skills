# Authoring ADRs

Read this before drafting an ADR. The format rules are enforced by the
tooling; the judgment rules here are what make the ADR set worth reading.

## Self-contained to the repository

An ADR must be legible from the repository alone. Its only audience is a
future reader who has the repo and nothing else: not this conversation, not
your shell, not the machine you drafted it on. So an ADR may refer only to
things that live in the repository: other ADRs, tracked files, committed
history. It must never refer to anything outside it.

Concretely, never write:

- **Conversation context**: "as we discussed", "per your request", "the
  approach you preferred". The reader wasn't in the conversation; the ADR has
  to make the case on its own.
- **Local environment state**: a path under someone's home directory, a
  branch that isn't merged, output you saw in your terminal, a file that
  exists only in the working tree, "the currently running instance". None of
  it survives for the next reader.
- **Anything transient or external without pinning it**: if a decision turns
  on an external fact (a library's behaviour, a standard, a benchmark),
  restate the fact in the ADR rather than pointing at where you saw it. A
  bare URL or ticket link rots; the reasoning it carried should live in the
  Context.

Rewrite every such reference into the durable fact behind it. "We chose JSON
because you said the consumer is a browser" becomes "The consumer is a
browser extension, which parses JSON natively; hence JSON." When you cannot
state the fact from the repository, that gap is real; resolve it with the
user before committing, don't paper over it with a pointer nobody can follow.

## Prose style

ADRs are prose a human will read, so write them like a human did. If a
`humanize` skill is available, invoke it while drafting or revising an ADR
and apply its checklist: no AI tropes, no inflated vocabulary, specifics
over adjectives, no em-dash-and-reframe filler. A permanent record written in
slop is a permanent liability.

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
`Hello, NAME!` followed by a newline", not "the CLI greets the user".

## Consequences

What follows: what becomes easier, what becomes harder, what future changes
this constrains, what code must now exist or change.
```

Format rules the linter enforces: filename `NNNN-kebab-slug.md`, contiguous
numbering from 0001, H1 matching `# ADR-NNNN: Title`, a `- Date:` line, the
three sections, and **no Status line**: a written status would have to be
edited when superseded, violating immutability, so status is always computed
from `Supersedes:` references instead.

## Decisions and tests

A Decision written checkably usually admits a test: the ADR says the CLI
prints exactly `Hello, NAME!`, a test tagged `ADR-NNNN` asserts it. That
tagged test is the Decision's conformance check made executable; write one
whenever the Decision specifies observable behaviour, in the code commit
that implements it.

When a Decision covers behaviour with several distinct cases, stating it as
given/when/then scenarios (the shape spec-driven tools like OpenSpec use)
can help: each scenario names a precondition, an action, and the observable
outcome, and each translates almost mechanically into a tagged test. This is
an optional shape, not a format rule; a single exact statement like the
greeting example needs no scenario scaffolding around it.

If you cannot imagine a test while drafting, work out which case you are in:

- **The decision is real but unobservable**: a dependency choice, a process
  rule, a structural convention. Fine; it simply has no test, and
  `coverage` reporting it untested is expected, not a problem to fix.
- **The Decision is written too vaguely to check**: "the CLI greets the
  user". Rewrite it until conformance is checkable; the missing test was a
  symptom.

Never write a test that merely restates code structure so an ADR looks
covered. A tautological test is a false conformance claim, the same failure
as an invented rationale: it makes the record claim knowledge it doesn't
have. There is no test-per-ADR rule for exactly this reason.

## Atomicity

One ADR = one independently supersedable decision. The test while drafting:
**"would anyone ever want to replace only part of this?"** If yes, split it.

Why it matters: supersession is total (an ADR is replaced whole or not at
all). If an ADR bundles five decisions and one changes, the superseding ADR
must restate the other four; every bundled decision is duplication you'll
pay for later. Atomic ADRs make supersession cheap and make the live spec
readable decision-by-decision.

**Too coarse:** "ADR-0007: Authentication" deciding token format, expiry,
refresh policy, and storage. Expiry will change independently of format.

**Right:** four ADRs: token format; token lifetime; refresh policy; token
storage. Each supersedable alone.

**Too fine:** "ADR-0009: Access token lifetime is 15 minutes" and
"ADR-0010: Refresh token lifetime is 30 days" *if* these would only ever
change together as one lifetime policy. Aspects of one decision belong
together; the unit is the decision, not the sentence.

A judgment call, not a rule of thumb about length: a one-line decision can be
a whole ADR, and a page can still be atomic.

## Supersession

- Point backwards only: the new ADR's `Supersedes:` line names the old one(s).
  The old file is never touched; its superseded status is computed.
- **Total, with restatement.** If ADR-0012 changes one aspect of ADR-0007,
  ADR-0012 restates everything from ADR-0007 that still stands. After the
  spec commit, ADR-0007 is entirely dead and ADR-0012 is complete on its own.
  Nobody should ever need to read a superseded ADR to know the current spec
  (only to understand history).
- One superseding ADR may supersede several old ones (consolidation), but an
  ADR can only be superseded once: to change a superseded decision again,
  supersede the *live successor*.
- Removing behaviour is also supersession: write an ADR whose decision is
  that the behaviour no longer exists, superseding the ADR that specified
  it. Specified absence is still specification; deleting the code without
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
Commit them together in one spec commit if they land together; a spec commit
may contain several new ADRs.

## Reverse-engineered ADRs (onboarded repos)

In a repo onboarded with a baseline ADR, some ADRs record decisions that were
made long before the ADR set existed: written when a task touches
grandfathered behaviour, or during an optional survey of load-bearing
decisions. Rules for writing them honestly:

- The Context section must say the decision was reverse-engineered from code
  (name the baseline commit) and mark the rationale as inferred or unknown.
  Never invent a rationale; a record that guesses silently cannot be trusted
  at all, and trustworthiness is the entire point of the set.
- Carve-out ADRs carry no `Supersedes:` line for the baseline: the baseline
  stays live and simply covers less. Supersession works normally between
  explicit ADRs: changing an already-extracted decision supersedes the
  extraction ADR.
- Only the graduation ADR supersedes the baseline, and only when nothing
  meaningful remains grandfathered.
- The user approves each reverse-engineered ADR before it is committed; they
  may know the real rationale where you can only infer it.

## What is NOT an ADR

- Proposals under discussion; those live in the conversation with the user.
  The repo contains only accepted decisions.
- Implementation notes, TODOs, status reports, changelogs.
- Restatements of code structure ("we have a module named X"). ADRs specify
  behaviour and the decisions behind it, not narrate the codebase.
