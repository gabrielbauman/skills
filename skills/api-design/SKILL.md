---
name: api-design
description: "Design and evolve APIs without breaking deployed consumers: know what counts as a breaking change (renaming or removing a field, changing a type, tightening validation, changing error semantics), evolve additively with deprecate-then-remove instead of mutating in place, version as a last resort, and design endpoints around the caller's task with pagination and an error contract from day one. Use when adding, changing, or reviewing an HTTP or RPC endpoint, a request or response shape, or a library's exported surface. Pairs with db-migrations, the same expand-and-contract discipline for schemas."
---

# API design

An API change looks like a code change but does not deploy like one.
The server and its consumers never update atomically: the callers are
other teams' services, mobile apps pinned for months by app-store
review, scripts nobody remembers writing. Rename a response field and
your tests stay green, your deploy succeeds, and someone else's
production breaks. So the question for every interface change is not
"does my code still work" but "does every caller I cannot see still
work", and the answer has to hold for callers running last quarter's
assumptions.

## Know what breaks

Breaking is anything that makes a request that used to succeed fail,
or a response that used to parse stop parsing, for an unchanged
consumer. The common ones, some less obvious than others:

- Removing or renaming a field, endpoint, or parameter.
- Changing a field's type or format, including "harmless" ones like
  int to string ids or a new timestamp layout.
- Tightening validation: an input accepted yesterday and rejected
  today is a break, even if rejecting it is more correct. Making an
  optional parameter required is this in its purest form.
- Changing the meaning of an existing field or value while its shape
  stays the same. This is the worst kind, because nothing fails
  loudly; consumers silently compute wrong answers.
- Changing defaults, status codes, error response shape, or ordering
  and pagination behavior consumers have observed.
- Adding a value to an enum that appears in responses: consumers that
  match exhaustively on the old values break. Safe only if the
  contract said "expect unknown values" from the start.

Safe changes are additive: a new endpoint, a new optional request
parameter, a new response field (given consumers were told to ignore
unknown fields, so say that in the contract from day one).

Hyrum's law sets the ceiling: with enough consumers, every observable
behavior gets depended on, documented or not, so the published
contract is the only defense. Be explicit about what is promised
(field presence, ordering, ranges, error codes), because everything
left unstated is a promise consumers will infer for you.

## Evolve additively

The interface version of expand and contract. To change something
that is already published:

1. **Add** the new field, parameter, or endpoint alongside the old.
   Both work; old consumers notice nothing.
2. **Deprecate** the old one visibly: docs, changelog, a
   `Deprecation` header or `@deprecated` marker, with a stated
   removal date. A deprecation nobody can see is not a deprecation.
3. **Migrate** consumers, and watch usage where you can measure it.
   Telemetry showing zero callers is evidence; "they've had six
   months" is a countdown, not evidence.
4. **Remove** in its own change, after the sunset date, announced.
   Per db-migrations, destruction ships alone and last.

A rename is an add plus a later remove, never an in-place edit. And
never repurpose: do not reuse an existing field or value to mean
something new, because old consumers keep reading it with the old
meaning and no error will ever tell them.

## Version as a last resort

Versioning feels like the responsible answer to breaking changes, but
every live version is a surface you support, test, and document until
the last consumer leaves, which is usually years. Exhaust additive
evolution first; most changes that look like they need a v2 are an
add-and-deprecate wearing a costume.

When a break is genuinely unavoidable, batch it: collect the breaking
changes into one rare, planned version bump with a migration guide,
rather than trickling out a new version per change. Keep the old
version running with an announced sunset. For libraries this is
semver's major release, and the same economics apply: majors are
expensive for every user, so frequent majors mean the design is
churning and adoption will stall.

## Design from the caller in

Model the caller's task, not your storage. An endpoint that mirrors
the database table leaks column names, internal ids, and enum values
into the contract, and from then on the schema cannot change without
an API break; the whole point of the interface was to keep those two
free to move independently. Design the response a consumer would
ask for, then map your storage into it.

Consistency is a feature consumers code against: one casing
convention, one id format, one timestamp format (RFC 3339, UTC)
across every endpoint, the same concept under the same name
everywhere. Every inconsistency becomes a special case in every
client.

List endpoints get pagination on day one, even when the data is
small, because bolting it on later changes the response shape, which
is a break. Small data becomes large data on its own schedule.

Errors are part of the contract, not an afterthought. Give each
failure a machine-readable code that is stable across releases, a
human message that is free to change, and the fields needed to act
(which input, what limit). Consumers parse whatever you give them; if
the only signal is prose, they will parse prose, and your reworded
message becomes a breaking change.

## Libraries are APIs too

Everything above applies to a published package's exported functions,
types, and constants; the consumers are downstream builds instead of
HTTP callers, and the break shows up as their compile error or
runtime surprise. Two additions specific to libraries:

- Export the minimum. Every public symbol is a permanent commitment;
  a helper exported "in case someone needs it" can never again be
  renamed, given a new signature, or removed without a major. Private
  is free to change forever.
- Renames follow the same add-deprecate-remove path: add the new
  name, mark the old one deprecated pointing at it, delete it in the
  next major.

## Bad, then good

Requirement: the `name` field in `GET /users/{id}` should be
`full_name`.

```text
One deploy: rename name to full_name in the serializer, update docs.
```

Your tests pass because they were updated in the same commit. Every
deployed consumer reading `name` gets undefined, and the first you
hear of it is their incident channel.

```text
Deploy 1:  response carries both name and full_name (same value);
           changelog and docs mark name deprecated, sunset date set,
           Deprecation header added to the endpoint
Migrate:   announce; watch access logs or client versions for
           remaining name readers
Deploy 2:  (after the sunset, with usage at zero) remove name, in
           its own change
```

Old consumers keep working through the whole window, the break never
happens, and the one destructive step ships alone, after the
evidence is in.
