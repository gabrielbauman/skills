---
name: adr-workflow
description: Enforce and operate an ADR-driven, agent-first development workflow where atomic, immutable Architecture Decision Records are the sole specification of behaviour, code carries inline ADR tags, and spec commits never mix with code commits. In any repository containing docs/adr/ together with tools/adr/adr_tools.py, consult this skill FIRST — before reading or editing any file — for EVERY task — feature requests, behaviour changes, bug fixes, refactors, "quick" tweaks, reverts, tooling changes, and architecture/design decisions (any decision made there becomes an ADR), even if the user never mentions ADRs; ungoverned changes break the repo's core guarantee. Also consult it first when an adr_tools pre-commit or commit-msg hook rejects a commit, after cloning a governed repo (hooks must be reinstalled), when the user asks to set up or adopt ADR-driven, spec-first, spec-driven, doc-driven, or agent-first development in a new or existing codebase (if they mean a specific tool like OpenSpec, present the trade-off rather than assuming this workflow), or mentions architecture decision records or superseding a decision.
---

# ADR-Driven Development

## The model

A governed repository makes one guarantee: **every behaviour of the code is
specified by a committed ADR, and every committed ADR is a trustworthy,
never-rewritten record.** Everything below exists to keep that guarantee.

- **ADRs are the spec.** Files under `docs/adr/`, named `NNNN-slug.md`. The
  live specification is the set of ADRs no other ADR supersedes. There is no
  separate docs layer — a hand-maintained "current docs" file would be a
  second spec that can drift; the ADR set can't. When someone wants the
  whole live spec in one readable document, generate it on demand with
  `adr_tools.py spec` — never commit the output, for the same reason.
- **ADRs are atomic and immutable.** One independently supersedable decision
  per ADR. A committed ADR is never edited or deleted, only superseded by a
  later ADR whose `Supersedes:` line points back at it. Status ("live" vs
  "superseded") is *computed* from those lines, never written into a file.
- **Code is a projection of the spec.** Code never implements behaviour that
  no live ADR specifies. Code that implements a decision carries an inline
  `ADR-NNNN` tag in a comment at the implementing unit.
- **Spec and code never share a commit.** A commit touches `docs/adr/` or it
  touches code — never both — and spec commits land first.

Tooling at `tools/adr/adr_tools.py` (installed with git hooks) enforces the
mechanical rules. Your job is the judgment the tooling can't do: designing
decisions with the user, writing good ADRs, and never writing unspecified
behaviour.

### Relation to spec-driven planning tools

Tools like OpenSpec keep a living current-behaviour spec organized by
capability, plus per-change planning folders (proposal, design, tasks) whose
deltas merge into it when the change ships. This workflow makes the opposite
bet: the decision log is the committed spec, the current view is generated on
demand (`adr_tools.py spec`), and hooks plus `validate` enforce
code-to-decision traceability that planning tools don't attempt. The two can
coexist — planning artifacts are working material for a change in flight; the
ADR is the record of the decision once made. In a repo carrying both, commit
planning files as chores, list their directory in `tools/adr/refignore` if
they must name superseded ADRs, and never let a planning document stand in
for a missing ADR.

## First, orient

- **Repo has `docs/adr/` + `tools/adr/adr_tools.py`** → it is governed. Run
  `python3 tools/adr/adr_tools.py status`, read the live ADRs relevant to the
  task, then follow "Making a change". Never start editing code before you
  know what the live spec says.
- **User asks to adopt the workflow in an empty/new repo** → follow "Setting
  up".
- **User asks to adopt it in a repo that already has code** → follow
  "Onboarding an existing codebase". Never try to specify the whole codebase
  up front.

## Setting up a repo

1. Copy `scripts/adr_tools.py` from this skill into the repo at
   `tools/adr/adr_tools.py`, then run `python3 tools/adr/adr_tools.py init`
   from the repo root. This scaffolds `docs/adr/`, generates ADR-0001 (the
   adoption of this workflow — the workflow specifies itself), and installs
   the `pre-commit` and `commit-msg` hooks.
2. Review ADR-0001 with the user; adjust before committing (it is only
   immutable once committed).
3. Commit in the order init prints: ADR-0001 alone as a spec commit, then the
   tooling as a code commit with `Implements: ADR-0001` (the tooling is the
   implementation of the workflow decision).
4. Everything after that follows "Making a change".

## Onboarding an existing codebase

Onboarding must not mean reverse-engineering the code into hundreds of ADRs:
bulk-generated ADRs need invented rationale, and a record with fabricated
context is worse than no record. Instead, existing behaviour is grandfathered
under one **baseline ADR** and extracted into real ADRs as code changes.

1. Make sure the current state is committed, then copy `scripts/adr_tools.py`
   from this skill to `tools/adr/adr_tools.py` and run `python3
   tools/adr/adr_tools.py init --existing`. Besides ADR-0001 this scaffolds
   ADR-0002, the baseline: all behaviour at the pinned commit is provisionally
   accepted, and for each behaviour the code itself is the spec until a live
   ADR specifies it explicitly, from which point the ADR takes precedence.
2. Review both ADRs with the user and commit in the order init prints. From
   then on every change follows "Making a change", with two brownfield
   readings:
   - Changing grandfathered behaviour is a **spec change** — the change is
     the moment the decision first gets made explicitly. The new ADR carves
     the behaviour out of the baseline: no `Supersedes:` line, precedence is
     automatic.
   - A **bugfix** in grandfathered code means restoring its evident intent
     (a crash, an off-by-one); cite the baseline ADR in the commit body, and
     do not tag the code with the baseline id. A fix that chooses between
     plausible behaviours is a spec change.
3. **Extract as you touch.** When a task depends on grandfathered behaviour,
   write the ADR(s) for the decisions it touches as part of that task. Never
   specify code you are not touching — coverage grows along the paths that
   actually change, which is where spec value is highest.
4. Optionally offer a bounded survey: draft ADRs for the few load-bearing,
   clearly deliberate decisions (wire formats, storage schema, authz model),
   each honest about its origin (see "Reverse-engineered ADRs" in
   [references/adr-authoring.md](references/adr-authoring.md)) and approved
   by the user, who may know the real rationale. A dozen honest ADRs beat
   three hundred confabulated ones.
5. `adr_tools.py coverage` reports which files carry ADR tags. It never
   fails; a hard ratchet would just be the specify-everything-first plan in
   disguise.
6. **Graduation.** When nothing meaningful remains grandfathered, write one
   final ADR superseding the baseline, declaring the ADR set complete. The
   repo then carries the full greenfield guarantee.

Until graduation, the guarantee reads: every behaviour is either explicitly
specified or visibly grandfathered at a known commit, and grandfathered
behaviour cannot change without becoming specified. Say this plainly when the
user asks what the ADR set covers.

## Making a change

Every request falls into exactly one class. Classify before touching anything:

| The request needs...                                   | Class    | Path |
|--------------------------------------------------------|----------|------|
| Behaviour no live ADR specifies (new or different)      | **Spec change** | Full loop below |
| Code brought back in line with a live ADR it violates   | Bugfix   | Code-only commit, `Exempt: bugfix`, cite the violated ADR in the message body |
| Internal restructuring, zero specified-behaviour change | Refactor | Code-only commit, `Exempt: refactor` |
| Tooling, deps, formatting, CI                           | Chore    | Code-only commit, `Exempt: chore` |
| Tests for already-specified behaviour                   | Tests    | Code-only commit, `Exempt: tests` |

The distinction that matters: **if code and spec disagree, decide which one is
wrong.** Code wrong → bugfix, no ADR needed (you are restoring conformance,
not deciding anything). Spec wrong or silent → spec change, ADR first. When
genuinely unsure whether behaviour is specified, treat it as unspecified —
that errs toward keeping the guarantee.

A bugfix also exposes a gap in the executable spec: code violated a live ADR
and no test caught it. Add or extend a test tagged with that ADR as part of
the fix, so the same violation fails in CI next time.

Reverts follow the same classification. Reverting shipped behaviour is a
spec change: a new ADR supersedes the regretted one and the code migrates
back. A bare `git revert` of a code commit (the hooks exempt `Revert`
subjects) is only for backing out code that never matched the live spec —
it is a bugfix in revert form. If the revert would change what a live ADR
specifies, it needs an ADR like any other change.

### The spec-change loop

1. **Design in conversation.** Work the problem with the user: options,
   trade-offs, edge cases. Nothing is committed during design — proposals live
   in the conversation, so the repo only ever contains accepted decisions.
2. **Draft the ADR(s).** `python3 tools/adr/adr_tools.py new "Title"
   [--supersedes N]` scaffolds the next number. One decision per ADR — the
   test is *"would anyone ever want to replace only part of this?"* If yes,
   split it. Write the ADR to stand on the repository alone: it may cite other
   ADRs, tracked files, and committed history, and nothing else — never this
   conversation, never local environment state (a working-tree-only file, an
   unmerged branch, terminal output, a home-directory path). Rewrite any such
   reference into the durable fact behind it. If a `humanize` skill is
   available, invoke it while drafting so the record reads like a person wrote
   it. See [references/adr-authoring.md](references/adr-authoring.md) for the
   template, the self-containment and prose rules, atomicity examples, and
   supersession mechanics.
3. **Get explicit approval.** Show the user the full ADR text. Once committed
   it is permanent, so approval happens now, not after.
4. **Spec commit.** Only `docs/adr/` files. If the change supersedes an ADR,
   the old file is untouched — the new ADR's `Supersedes:` line is the only
   record needed.
5. **Implement.** Bring the code into line with the new live spec — no more,
   no less. Tag implementing units with the ADR id. When the Decision
   specifies observable behaviour, also write a test asserting it, tagged
   with the same id — the test is the Decision's conformance check made
   executable, and it lands in the same code commit. A decision with nothing
   observable (a process rule, a structural choice) gets no test; never
   write a tautology to fill the gap. If you superseded an ADR, `validate`
   will list every stale `ADR-NNNN` tag pointing at it; that list
   is your migration checklist.
6. **Code commit** with `Implements: ADR-NNNN`, then run
   `python3 tools/adr/adr_tools.py validate` and fix anything it reports.

If, mid-implementation, you discover the ADR under-specified something (an
edge case forces a decision the ADR doesn't make), do not quietly decide it in
code — that is exactly the unspecified behaviour this workflow exists to
prevent. Go back to step 1 for the missing decision; a small follow-up ADR is
cheap.

## Code rules

- Tag the implementing unit (function, class, module — whichever level the
  decision lands at) with a comment containing `ADR-NNNN`.
- Comments explain **why, never what**. Code *is* the behaviour; a comment
  restating it is noise that rots. The ADR reference belongs in a why-comment
  because the decision is the reason the behaviour exists:

  ```python
  # Consumers parse this output, so the format is load-bearing (ADR-0002).
  print(f"Hello, {name}!")
  ```

  Not: `# print greeting (ADR-0002)`.
- Tests that verify an ADR's decision carry the same `ADR-NNNN` tag as the
  implementing code. The payoff comes at supersession: the stale-tag scan
  then lists those tests alongside the code, so a test asserting dead spec
  gets migrated instead of silently pinning the old behaviour.
- Never write code referencing an ADR that doesn't exist yet ("I'll commit the
  spec later") — spec lands first, and the hooks reject the reversed order.

## Commit rules

| Commit type | Touches | Message |
|-------------|---------|---------|
| Spec | Only `docs/adr/` (new files only — never modify/delete) | Describe the decision; no trailer needed, the ADRs are the authority |
| Code | Anything except `docs/adr/` | Trailer: `Implements: ADR-NNNN[, ADR-NNNN]` or `Exempt: bugfix\|refactor\|chore\|tests` |

The hooks enforce: no mixed commits, no ADR mutation, ADR lint on new ADRs,
no code references to superseded/nonexistent ADRs, the trailer requirement,
and a cited live ADR in every `Exempt: bugfix` body (if no live ADR is
violated, it is not a bugfix). Never use `git commit --no-verify` on your
own initiative; a
hook rejection means the change is wrong, not the hook. If the user
explicitly orders a bypass after you've explained what it breaks, it's their
repository — comply, tell them the every-behaviour-is-specified guarantee is
now broken, and offer to backfill the ADR immediately. (A bypassed commit
also fails `validate`'s history audit permanently — one more reason to
backfill: the record should at least point at its own gap.)

## Branches and merges

Immutability binds shared history, not unpublished branches. When two
branches each add an ADR with the same number, `validate` fails the merged
result on duplicate numbering. The branch that merges second rebases and
renumbers — file, title, and any code tags — before merging; rewriting an
unpublished branch is not a mutation of the record. Once a spec commit is on
the shared branch its number is permanent and every open branch adjusts to
it. Run `validate` on the merge result before pushing (CI covers this if set
up as below).

## When the user wants to skip the process

"Just add it quickly, skip the docs" — don't silently comply and don't
lecture. The honest framing: one unspecified behaviour breaks the repo's
guarantee for every future agent that reads it, and the spec path is fast —
for a small change the ADR is a paragraph you can draft in the same breath.
Draft it, show them, and the "process" costs one extra commit. If they still
explicitly insist on skipping, see the bypass rule above.

## Tooling reference

All subcommands of `python3 tools/adr/adr_tools.py`, runnable from anywhere
in the repo:

| Command | What it does |
|---------|--------------|
| `init` | Scaffold `docs/adr/` + ADR-0001, copy tooling, install hooks. Greenfield by default; `--existing` onboards a codebase by also generating the ADR-0002 baseline (`--force` skips the check and grandfathers nothing) |
| `new "Title" [--supersedes 7]` | Create the next-numbered ADR from the template |
| `status` | Table of every ADR: live/superseded-by, code-ref count |
| `spec` | Render the live spec as one document: every live ADR's Decision section, in number order. A generated view for humans (and agents) — never commit the output; the ADRs are the authority |
| `coverage` | Report which tracked files carry ADR tags and which remain untagged (grandfathered or non-code), plus which live ADRs have no tagged test. Informational, never an error — some decisions are untestable, and a hard test ratchet would only breed tautology tests |
| `validate` | Full audit: lint, numbering, supersession graph, immutability vs git history, commit-history rules (mixed commits, missing trailers), stale/dangling code refs, coverage warnings |
| `check-staged` / `check-msg` | The hook entry points (run automatically on commit) |
| `install-hooks` | (Re)install hooks in an already-governed clone — run this after cloning, since hooks don't travel with the repo |

Hooks are per-clone conveniences, not the enforcement layer: a clone that
never ran `install-hooks` can commit anything. The backstop is CI — run
`python3 tools/adr/adr_tools.py validate` on every push and pull request.
`validate` re-audits the entire post-adoption commit history for mixed
commits and missing trailers, so an ungoverned commit fails CI before it
reaches the shared branch. When setting up a governed repo that has a CI
system, offer to add this check.

Prose that must name a superseded ADR (a changelog, a postmortem) would
fail the stale-reference scan forever. Either keep such history inside a
later ADR's Context, or list the file in `tools/adr/refignore` — one glob
or path prefix per line, committed as a chore — and the reference scan and
coverage skip it. Code never goes in refignore; a stale tag on code is
exactly what the scan exists to catch.
