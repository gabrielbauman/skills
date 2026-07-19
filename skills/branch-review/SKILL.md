---
name: branch-review
description: "Run a pre-merge review of a branch with parallel specialist agents and an adversarial challenge round: reviewers with narrow charters (correctness, security, tests, docs, spec conformance) find issues, a verifying challenger dismisses the false positives, and survivors land in a prioritized report where every HIGH cites the defect or the written rule it violates. Depth scales with the branch, so a typo fix gets a single-pass review and a large or security-sensitive branch gets the full fleet. Use when asked to review a branch, PR, or diff before merge, audit a changeset, give a second opinion on a branch, or re-review after fixes. Pairs with test-behavior, which supplies the test charter's criteria; atomic-commits, whose standards the commit-history check applies; adr-workflow, which gives the spec-conformance charter its citations in governed repos; pr-description, whose reading order and risk callouts are the first thing this review reads to scope itself; and reviewing-code, the single-reviewer craft this fleet parallelizes."
---

# Branch Review

A single reviewer reading a whole branch skims. By the twelfth file it is
confirming its first impression, and the review converges on "LGTM with
nits". The obvious correction, throwing several agents at the diff,
replaces skimming with noise: specialists eager to justify their existence
report phantom issues, and after two rounds the author stops reading the
reports. This skill runs the two failure modes against each other.
Reviewers with narrow charters find; an adversarial challenger that must
verify before dismissing filters; a severity rubric that demands citations
keeps the report honest. Review depth scales with the branch, because a
six-agent audit of a typo fix costs real money to find nothing.

You are the review orchestrator. Deliver a report; do not start fixing
findings unless asked.

## Establish context

Resolve the base branch: an explicit argument wins, otherwise the repo
default (`git symbolic-ref refs/remotes/origin/HEAD`, usually main).

Fetch before diffing, and diff against `origin/<base>...HEAD`, not the
local base ref. A cloned-fresh or long-lived session's local base lags the
remote as other PRs merge, and diffing against the stale ref pulls
already-merged code into the "branch diff"; the review then spends its
findings on code that is not on this branch. The fetch is best-effort: if
it fails, say so in the report and use the origin ref you have.

Gather, in your own context:

- `git log origin/<base>...HEAD --oneline --no-merges`
- `git diff --name-only origin/<base>...HEAD` and `--stat`
- The repo's written rules: CLAUDE.md, AGENTS.md, CONTRIBUTING, and any
  spec or ADR directory they point to. The severity rubric hangs on these.

Check the commit history yourself, now, without an agent; you already
hold the log, and a dedicated historian would re-read the same few
hundred tokens. Look for: commits bundling unrelated changes (see
atomic-commits), vague or misleading messages, debug artifacts and
leftover TODOs, a change made then partially reverted, generated files or
IDE config, and a branch whose diff does not match its stated scope.
History findings enter the report like any other.

## Choose the tier

Every specialist reads the branch, so cost grows with each agent, and the
challenger adds one more pass. Spend agents where the uncertainty is, and
say in the report which tier ran and why.

- **Light**: docs-only changes, mechanical renames, or a diff under a few
  hundred lines. No subagents. Review the full diff yourself using every
  charter below as a checklist, then challenge your own findings under
  the Phase 2 rules before writing the report.
- **Standard**: the default. Three specialists: correctness and design,
  security, tests and docs. Challenger runs only if a HIGH or MEDIUM
  finding comes back.
- **Deep**: the change plus the code it can break exceeds what one
  context can hold and verify: over roughly a thousand changed lines or
  twenty files, a release branch, or security-sensitive surface (auth,
  crypto, payments, permissions, deserialization) with blast radius you
  cannot trace directly. Five specialists: split correctness from
  design, split tests from docs, and add spec conformance when the repo
  has written specs. Challenger always runs.

The thresholds are guides, not gates. A 90-line diff that rewrites lock
ordering deserves deep; a 2000-line generated-code bump deserves light.
Sensitive surface demands evidence, not headcount: when the entire
affected codebase is small enough to read and verify directly, light
with full manual attention on the sensitive paths is the better spend.
The override runs the other way too: when the user explicitly asks for
the fleet or a deep review, dispatch it even if the branch looks small.

## Severity rubric

- **HIGH**: a demonstrable defect (correctness bug, security flaw, a test
  that contradicts the behavior it should verify) or a violation of a
  written rule. A HIGH must cite its evidence: the file:line that fails,
  or the doc section, ADR, or rule it violates. No citation, no HIGH.
- **MEDIUM**: drift that has not yet broken anything: a docstring
  describing the old behavior, a name that lies about what the code
  stores, a changed failure path no test reaches, an internal type
  leaking through a public boundary.
- **LOW**: preference: style, structure, simplification.

## Phase 1: dispatch the specialists

Launch all specialists in one message so they run in parallel. Each
prompt must contain: the branch and base names, the commit list, the
changed files in that agent's purview, the findings format and severity
rubric above, relevant excerpts of the repo's written rules, and the
prior round's report verbatim if one exists in this conversation.

Do not paste the full diff into each prompt. Duplicating a large diff
across every specialist is the single biggest token cost of this pattern,
and a pasted diff is a worse view than the repo the agent can already
read. Instead, instruct each agent to pull its own scoped diff
(`git diff origin/<base>...HEAD -- <paths>`) and to read surrounding
code, cited docs, and tests in the working tree as needed.

Each agent reports findings as:

```
[AGENT NAME] FINDINGS
[SEVERITY] <short title> - <file:line> - <one-sentence rationale> - <citation for HIGH>
```

or `[AGENT NAME] FINDINGS\nNone.` if it finds nothing.

### Correctness and design

Logic errors and off-by-ones in changed code; error handling that is
missing, swallows failures, or diverges from the codebase's pattern;
concurrency risks introduced by the change; performance hazards (I/O in
loops, unbounded growth, missing pagination); duplication with existing
code that should be shared; new coupling between previously independent
modules; a change that would surprise a maintainer in six months with no
authorizing design note; an externally visible change (wire field, status
code, error class) presented as a refactor.

### Security

Hardcoded secrets, tokens, or keys anywhere in the diff; injection risks
(shell, SQL, path, template) in new or modified code; missing validation
where external data enters; new endpoints, RPCs, or flags lacking authn
or authz; sensitive data surfacing in logs, errors, or replies; new
dependencies that are unversioned or unmaintained; permission, CORS, or
network changes that widen exposure. When impact depends on a deployment
posture the diff cannot show (single-tenant, internal-only), say so in
the rationale so the challenger can calibrate rather than guess.

### Tests

Apply test-behavior's criteria: new public behavior with no test; changed
branches and failure paths no test reaches; tests asserting
implementation details (call counts, private state) that break on safe
refactors; mocks so aggressive the test cannot fail; missing boundary
cases; a test that passes against the code's intent but contradicts the
documented behavior it cites, which is HIGH because it hides a real
disagreement. If the diff contains no tests, say so and assess whether it
should.

### Docs

For every public function, endpoint, flag, or config the diff touches:
docstrings describing pre-change behavior; new public surface with no
documentation; README, changelog, or reference docs that should mention
the change and do not; examples the change breaks; content restated from
another doc that has now drifted from its source. When the diff renames
or retracts a concept, grep the doc set for surviving mentions; tables
and diagrams go stale silently.

### Spec conformance (deep tier, repos with written specs)

Only when the repo carries specs, ADRs, or design docs meant to govern
behavior. Open the documents the commits or code cite and check the diff
against them line by line: wire shapes, field names, status codes, enums,
constants. Behavior the diff adds that no doc describes, and behavior it
removes that a doc still promises, are findings against the repo's own
rules. Restated spec content is checked against the source doc, not
against plausibility; restatement drift comes in clusters, so one hit
means sweeping the branch for more.

## Phase 2: challenge round

Skip the challenger when Phase 1 produced nothing, and never send it LOW
findings; shipping an unverified style preference is cheap, and an agent
argued down over naming costs more than the nit is worth. Otherwise
dispatch one challenger with the numbered HIGH and MEDIUM findings and
the changed-file list. It reads the repo directly; it does not need the
diff pasted either. The challenger's value is independence from whoever
authored the findings, so when the findings under challenge are not
your own (a prior round's report, a list handed to you), you may run
the challenge yourself under the same rules instead of dispatching an
agent.

The challenger's mission: a senior engineer who has watched review
processes drown authors in phantom issues. For each finding: is this a
problem in this specific code, or a generic concern applied without
reading? Could the code already handle it somewhere outside the diff?
Check the repo rather than hypothesize in either direction. Is the
severity honest about blast radius? Would a reasonable reviewer block
the merge over it?

For each finding, exactly one verdict:

- `SUSTAIN`: valid, severity appropriate.
- `DOWNGRADE [severity]`: valid but overstated, one sentence why.
- `DISMISS`: not a real issue, one sentence why.

Hard rules, because an unattended merge may hang on this output:

- A DISMISS must cite what was checked and found ("handled at
  file:line", "the cited doc permits this"). An unverifiable dismissal
  hypothesis floors at DOWNGRADE.
- A HIGH with no citation drops to MEDIUM, unless the challenger can
  supply the citation itself and sustain.
- With a prior-round report present, tag each survivor `[new]` or
  `[persisting]`.

Preserve finding numbers so verdicts match back.

## Phase 3: report

Drop dismissed findings, apply downgrades, sort HIGH then MEDIUM then
LOW, and group by charter within each tier. Omit empty tiers.

```
## Branch Review: `<branch>` -> `<base>`  (tier: <light|standard|deep>, <why>)

*One sentence on what this branch does.*

### HIGH
**[Charter]** `[new|persisting]` - problem, file:line - violated rule or defect citation - expected fix

### MEDIUM
**[Charter]** `[new|persisting]` - problem, file:line - expected fix

### LOW
**[Charter]** - problem and where - suggestion

### Resolved since last round
(Only with a prior report.) One line per prior finding that no longer applies.

### Challenged and dismissed
N findings dismissed. If any dismissal looks wrong, say so and it will be reinstated.
- **[Charter]** title - *Dismissed: reason*
```

Keep each finding to a sentence or two; the author can ask for more on
any of them. If any agent reported it could not see its whole purview,
say so; a review of a partial view must not read as a review of the
branch. Re-running after fixes is a round: findings carry their
`[persisting]` tags forward, and a third consecutive round with the same
HIGH or MEDIUM persisting means review is not converging. Stop
re-reviewing and raise that directly instead.
