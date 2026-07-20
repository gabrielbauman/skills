---
name: test-behavior
description: "Write tests that verify observable behavior rather than pinning the implementation: assert on outcomes instead of mock calls, mock only at boundaries you do not control, name tests as behavior claims, cover boundaries and error paths, and reproduce a bug in a failing test before fixing it (red before green). Use whenever writing tests, adding coverage, fixing a bug, reviewing code that ships with tests, refactoring tested code, or cleaning up a brittle, mock-heavy suite. Pairs with flaky-tests, for the test that fails intermittently."
---

# Test Behavior

A test earns its keep by being able to fail. The suite's job: when someone
breaks a behavior users rely on, one test goes red and its name says which
behavior died. Agent-written suites tend to fail in both directions at
once. They pass while behavior is broken, because the assertions track
mocks and call counts that only mirror the mechanism. And they break when
nothing is wrong, because renaming a private helper rewires forty tests. A
suite like that is decoration with a maintenance bill.

The question to ask of any test: if this behavior broke in an obvious way
tomorrow, would this test fail? If not, the test asserts nothing.

## Assert on outcomes, not the mechanism

Observable outcomes are the return value, the raised error, state a caller
can read, and the bytes that crossed the wire. The mechanism is everything
in between: which collaborator got called, how many times, with which
intermediate arguments, what a private field now holds.

Pin the outcome and the test survives a full rewrite of the internals. Pin
the mechanism and the test breaks on every behavior-preserving refactor,
which trains whoever maintains the code to update tests without reading
them. Worst of all is asserting a mock received the right call: that proves
the code calls the mock the way the code calls the mock. It cannot catch a
wrong result; it can only catch change.

## Mock at the boundary

Mock what you do not control or what makes tests slow or nondeterministic:
the network, the clock, randomness, the payment processor. Do not mock your
own objects. A test where every collaborator is a mock transcribes the
implementation and asserts the transcription matches.

Where a fake is cheap, prefer it over a record-and-replay mock: an
in-memory repository, a stub HTTP server, a fixed clock. Fakes let you
assert on outcomes (the confirmation email went to the user) instead of
conversations (send was called once with these arguments). When you do
assert across a boundary, assert on what crossed: the request body, the
rows now in the table. Never on how many times an internal method ran.

## Name tests as behavior claims

The name states the claim: `rejects_expired_tokens`, `rounds_half_to_even`.
Read top to bottom, the test list should say what the unit does.
`test_fetch`, `test_success`, and `test_edge_case_1` force the reader to
reverse-engineer the claim from the body.

Keep one behavior per test. A failing test that asserts six unrelated facts
reports only that something in checkout broke, and you read the whole body
to learn what. Table-driven cases running one assertion over many inputs
still count as one behavior.

## Cover the boundaries and the errors

Bugs live at the edges: 0, -1, empty, null, the maximum, the duplicate, the
string with a surrogate pair. The happy path is the least likely place for
the code to be wrong and the most likely place an agent writes its only
test.

Error handling is behavior. When the contract says invalid input raises
`ValidationError`, that promise deserves a test as much as the success path
does.

Skip what cannot fail: getters, pass-throughs, the framework's own
behavior. A test that cannot fail is maintenance cost with no signal.
Coverage measures which lines executed, not which behaviors are checked; a
line run by an assertion-free test is covered and untested at once.

## Bug fixes: red before green

Reproduce the bug in a test before fixing it. Write the test that fails on
the current code, run it, and confirm it fails for the right reason: the
assertion you wrote, not a typo in the test itself. Then fix, and watch it
pass. A test written after the fix, never seen red, may pass on the bug as
well, and nobody notices until the regression comes back.

Keep that test. It is the regression record, named after the behavior and
citing the issue where the codebase's convention does.

Tests written against your own fresh implementation mostly prove the code
matches your reading of the spec twice. Anchor expected values to the spec,
the ticket, or worked examples from the user, never to what the code
currently returns. Do not compute expected values by re-running the same
logic inside the test: one shared misunderstanding and both sides pass.

## Working with an existing suite

Match the codebase: framework, file layout, naming, fixture style. Idiom
matters in tests as much as in the code under test.

Keep setup visible. A reader should see the two or three things a test
depends on. A 200-line shared fixture hides the precondition and couples
every test to every other test's data.

Keep tests independent: no order dependence, no shared mutable state. A
suite that fails in batches and passes one test at a time teaches people to
ignore it, and an ignored suite is worse than none.

Treat flaky tests as bugs in the suite. Fix the cause (wall-clock reads,
real network, unseeded randomness, order dependence) or delete the test.
Retrying CI until green teaches everyone that red means nothing.

When behavior changes deliberately, the tests encoding the old contract
change in the same change; that is the spec being updated. When a test
fails and you did not intend to change that behavior, assume the code is
wrong until proven otherwise. Never loosen an assertion, add a skip, or
delete a test to get CI green without the user confirming the new behavior
is intended.

## Bad, then good

```python
def test_checkout_applies_coupon():
    cart = Mock()
    cart.total_cents.return_value = 2000
    engine = Mock()
    apply_discounts(cart, engine, code="SUMMER10")
    engine.compute.assert_called_once_with(cart, "SUMMER10")
    cart.apply.assert_called_once()
```

```python
def test_coupon_takes_ten_percent_off_total():
    cart = Cart([Item(price_cents=2000)])
    apply_discounts(cart, code="SUMMER10")
    assert cart.total_cents() == 1800
```

The first test breaks if `apply_discounts` delegates to a different
collaborator, passes the code positionally, or inlines the discount;
meanwhile the discount could compute nothing at all and the test still
passes. The second fails exactly when a customer gets the wrong total, and
survives any rewrite of how the discount gets computed.
