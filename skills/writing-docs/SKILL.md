---
name: writing-docs
description: "Write documentation for the reader who arrives with a task: lead the README with what the thing is and a copy-pasteable quickstart, keep tutorials, how-to guides, reference, and explanation separate, prefer runnable examples over prose, document the sharp edges users actually hit, keep docs next to the code they describe, and fix or delete stale docs on sight. Use whenever writing or updating a README, getting-started guide, how-to, API reference, runbook, or onboarding doc, or when auditing docs for rot. Pairs with humanize, which governs the prose itself."
---

# Writing docs

Documentation gets written from the author's seat: organized by how
the code is structured, complete where the author found the work
interesting, silent where the author forgot anything needed
explaining. The reader arrives from the opposite direction, holding a
task ("make it run," "call this API," "fix this error") and no
context, hits the gap between the doc's assumed knowledge and their
own on step one, and leaves. The doc is technically accurate,
genuinely effortful, and useless.

Write from the reader's seat: what do they know when they arrive, and
what are they trying to do? Every rule below is that question applied
somewhere.

## The README earns the next minute

A README's first screen answers, in order: what this is (one or two
sentences, concrete: "a CLI that converts Figma exports to CSS
tokens," not "a modern flexible toolkit"), and how to get to first
success, meaning install, minimal run, and what output to expect:

    npm install -g figtok
    figtok export.json -o tokens.css
    # writes tokens.css with one custom property per Figma style

That block does more work than any amount of feature prose, because
running the thing successfully is the moment a reader converts to a
user. Badges, philosophy, architecture, and history all live below
that fold or in other files. Prerequisites go before the commands
that need them, stated exactly ("requires Node 20+ and a Figma
personal access token"), because the reader missing a prerequisite
experiences your quickstart as broken.

## Know which document you are writing

Four kinds of documentation serve four different readers, and mixing
them ruins each (this split is the Diataxis framework, worth reading
in full):

- **Tutorial**: a guided first lesson for a beginner. Optimized for
  guaranteed success, one blessed path, no choices.
- **How-to guide**: steps for a specific goal ("rotate the signing
  key") for someone who already knows the basics. Optimized for
  getting done.
- **Reference**: complete, accurate description of the machinery
  (every flag, every field). Optimized for looking things up, so
  structure mirrors the code and entries stay uniform.
- **Explanation**: why it works this way, tradeoffs, background.
  Optimized for understanding, read in an armchair.

The failure mode is one page doing all four: a tutorial that detours
into design rationale loses the beginner; a reference that chats
loses the looker-upper. Notice which one the reader in front of the
gap needs, write that, and link to the others.

## Show, then tell

A runnable example is the highest-density documentation there is: it
states the required imports, the argument order, the return shape,
and the happy path all at once, and unlike prose, the reader can
verify it. For any API or command, lead with the example and let the
prose annotate it.

Examples earn their keep only while they run, so make them honest:
copy-pasteable as written (no `<your-value-here>` where a working
default could be, no elided imports the snippet needs), and executed
by CI where the ecosystem supports it (doctests, mdBook tests,
cookbook scripts in the suite). An example that errors on paste
teaches the reader to distrust the entire document.

## Document the sharp edges

The docs the author omits are the ones about the system misbehaving,
and they are the docs readers need most desperately, because they
arrive at them mid-failure. Write down: the known failure modes and
their symptoms ("if you see `ECONNREFUSED` here, the daemon is not
running; start it with..."), the prerequisites and environment
assumptions, the limits (rate, size, concurrency), and the "gotcha"
every teammate learns the hard way. One "if you see X, it means Y, do
Z" paragraph placed at the step where X happens can retire a
recurring support thread.

This is code-comments at document scale: the valuable content is
constraints, consequences, and reasons, not restated mechanics.

## Wrong beats missing, so tend or delete

A missing doc sends the reader to the code, which costs time. A wrong
doc sends the reader confidently down a dead path, then teaches them
to stop trusting docs entirely, which costs every future doc too. So
stale documentation is not a lesser artifact but an active defect:

- Fix or delete on sight. Deleting a wrong doc is an improvement, not
  a loss; do not let "someone might need it" preserve misinformation.
- Keep docs where diffs catch them: next to the code they describe,
  in the same repo, so the PR that changes the flag is naturally the
  PR that updates the flag's doc, and reviewers can see the mismatch.
- Documentation that restates the code line by line ("`timeout`: the
  timeout") is stale the day the code moves and informationless
  before that. Document the contract and the constraint, not the
  mechanism visible in the source.

## Prose rules still apply

Docs are prose; the humanize checklist governs them fully. The doc
failure modes are specific dialects of it: marketing adjectives where
specifics belong ("blazingly fast" instead of "parses 1GB in ~4s"),
announcing structure instead of having it, and hedged non-claims
("this may potentially cause issues in some cases" instead of "this
breaks if two workers share a state directory"). A reader mid-task
wants short declarative sentences, exact names, and real numbers.

## Bad, then good

The same feature, documented twice:

> **Configuration.** The system provides a robust and flexible
> configuration mechanism. Various options can be specified to
> customize behavior according to your needs. See the source for
> details.

> **Configuration.** Config is read from `./sync.toml`, then
> `~/.config/sync.toml`; the first file found wins (they do not
> merge). Two settings matter for most setups:
>
>     interval = 300    # seconds between syncs; min 60
>     on_conflict = "newest"   # or "local", "remote", "ask"
>
> If sync exits immediately with `no config found`, neither file
> exists; start from `sync.toml.example` in this repo.

The first paragraph is true of every configurable program ever
shipped, which is another way of saying it contains nothing. The
second names the files, the precedence rule (a sharp edge), the two
settings that matter with working values, and the failure a new user
hits first, with its fix.
