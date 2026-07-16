# ADR-0002: Greeting output format

- Date: 2026-07-01

## Context

`greet` is consumed by shell scripts that parse its output, so the exact
output format is a contract, not a presentation detail.

## Decision

`greet NAME` writes exactly `Hello, NAME!` followed by a single newline to
stdout and exits 0. NAME is interpolated verbatim.

## Consequences

Any change to the greeting wording, punctuation, or destination stream
requires superseding this ADR. Consumers may safely match on the exact
string.
