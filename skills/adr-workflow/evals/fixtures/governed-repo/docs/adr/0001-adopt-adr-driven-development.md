# ADR-0001: Adopt ADR-driven development

- Date: 2026-07-01

## Context

This repository is agent-first: any agent or human must be able to determine
what the system is supposed to do by reading its Architecture Decision
Records, without reading the code. That guarantee only holds if every
behaviour is specified before it is implemented, and if the record of
decisions can be trusted never to have been rewritten.

## Decision

Adopt the ADR-driven workflow for this repository:

1. ADRs under `docs/adr/` are the sole specification of behaviour. The live
   specification is the set of ADRs that no other ADR supersedes.
2. Each ADR is atomic (one independently supersedable decision) and immutable
   once committed. ADR files are never modified or deleted.
3. Changing a decision means writing a new ADR with a `Supersedes:` line.
   Supersession is total: the new ADR restates any decisions from the old one
   that still stand, so it is complete on its own.
4. An ADR's status is computed from supersession references, never written
   into the file.
5. Code implementing a decision carries an inline `ADR-NNNN` tag in a comment
   at the implementing unit. Comments explain why behaviour exists (including
   the ADR reference), never what the code does.
6. No code may implement behaviour that no live ADR specifies.
7. Every commit is either a spec commit (touching only `docs/adr/`) or a code
   commit (touching nothing in `docs/adr/`), never both. Spec commits land
   before the code commits that implement them.
8. Code commits carry a trailer declaring their authority: either
   `Implements: ADR-NNNN` or `Exempt: bugfix|refactor|chore|tests`.
9. The tooling at `tools/adr/adr_tools.py` and the git hooks it installs
   enforce these rules mechanically.

## Consequences

Every behaviour is traceable to a decision and every decision to its context.
Specifying before implementing adds a step to every behavioural change; in
exchange, the specification can never drift from the code, and superseding an
ADR mechanically surfaces every piece of code that must migrate.
