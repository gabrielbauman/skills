# skills

[Agent skills](https://agentskills.io) written by Gabriel Bauman and Claude.
Each skill lives in its own directory under `skills/` and can be installed
independently.

## Skills

| Skill | Description |
| --- | --- |
| [adr-workflow](skills/adr-workflow/) | ADR-driven development: atomic, immutable Architecture Decision Records as the sole behavioural spec, strict spec/code commit separation, inline ADR tags in code, and git-hook enforcement tooling (bundled in [scripts/](skills/adr-workflow/scripts/)). |
| [atomic-commits](skills/atomic-commits/) | Decide what each git commit should contain: one self-contained, reviewable change per commit. Covers splitting a mixed working tree into an ordered series with `git add -p`, when a split is artificial, and keeping discovered fixes out of feature commits. Pairs with scoped-commits, which covers the message. |
| [branch-review](skills/branch-review/) | Pre-merge branch review with parallel specialist agents (correctness, security, tests, docs, spec conformance) and an adversarial challenger that must verify before dismissing a finding. Every HIGH cites the defect or written rule it rests on, and depth scales with the branch: small diffs get a single-pass review, large or security-sensitive ones get the full fleet. |
| [bug-reports](skills/bug-reports/) | Write bug reports a stranger can act on without a follow-up question: one bug per report, titles that state symptom plus condition, expected vs actual, numbered repro steps from a clean start, exact error text pasted verbatim, environment and frequency, and speculation labeled separately from observation. Pairs with debugging, which consumes the report and produces the shrunken repro worth filing. |
| [changelog](skills/changelog/) | Update CHANGELOG.md by curating what changed for end users instead of transcribing the git log: [Common Changelog](https://common-changelog.org) format, breaking changes bolded first with migration pointers, and rules for which commits deserve no entry at all. |
| [db-migrations](skills/db-migrations/) | Change database schemas without breaking the running system: every migration compatible with the code deployed before and after it (expand and contract), renames as add-backfill-swap instead of in place, backfills as batched resumable jobs separate from DDL, destructive steps alone in a later deploy, applied migrations never edited, and lock behavior checked before DDL touches a hot table. Pairs with refactoring, the same keep-it-working-at-every-step discipline for code. |
| [debugging](skills/debugging/) | Debug systematically instead of speculatively: reproduce the failure first, read the whole error instead of pattern-matching to a famous fix, test one hypothesis at a time and revert unverified attempts, isolate before changing code, fix the cause rather than the nearest symptom, and verify against the original reproduction. Pairs with test-behavior, which turns the repro into the permanent regression test. |
| [dependencies](skills/dependencies/) | Manage third-party dependencies as long-term liabilities, not free code: decide when a package earns its place versus writing the function yourself, vet before adding (maintenance, transitive weight, license, install scripts, exact name), commit the lockfile, bump one dependency at a time with the upstream changelog read first, keep bumps out of feature branches, and remove packages that stop paying rent. Pairs with small-prs and atomic-commits, which keep each bump its own reviewable change. |
| [error-handling](skills/error-handling/) | Handle errors so failures are loud, actionable, and traceable: fail early instead of limping on bad state, never swallow an exception silently, write messages that name what was attempted with which inputs, preserve the underlying cause when rethrowing, catch at the boundary that can act, choose retry vs propagate vs crash, and never leak secrets or internals to users. Pairs with debugging, whose investigations depend on errors reported well in the first place. |
| [flaky-tests](skills/flaky-tests/) | Treat an intermittently failing test as a bug to fix, not a nuisance to rerun: quarantine visibly with an owner and expiry, reproduce with a counted loop under the conditions that flake, diagnose the usual suspects (sleep-based waits, test order, shared state, unseeded randomness, real clocks, real networks, leaked resources), fix the mechanism instead of widening the timeout, and recognize when the flake is a real race in the product. Pairs with test-behavior and debugging. |
| [git-recovery](skills/git-recovery/) | Reshape and recover git history safely: interactive rebase to reorder, squash, split, and reword commits; `fixup` plus `--autosquash` to amend an earlier commit; `reset --soft/--mixed/--hard` and when each is right; `--force-with-lease` instead of `--force`; the reflog as the undo of last resort; and `git revert` for undoing an already-shared commit. Covers the non-interactive rebase alternatives for agent environments. Pairs with atomic-commits, which decides what each commit should hold. |
| [humanize](skills/humanize/) | Write prose that reads like a person wrote it, and strip AI tells from existing text: em-dash addiction, negative parallelism, inflated vocabulary, bold-first bullets, manufactured drama. Compact checklist by default, full trope catalog on demand. |
| [logging](skills/logging/) | Write logs an operator can act on during an incident: match the level to the reader and the action (ERROR someone must act, WARN handled, INFO milestone, DEBUG diagnostic), prefer structured key-value fields over interpolated strings so logs are queryable, log the ids and inputs and attempt needed to act instead of a bare `failed`, never log secrets or PII, log at boundaries and state transitions rather than every line, and don't log-and-rethrow one error at every layer. Pairs with error-handling and debugging. |
| [naming](skills/naming/) | Name variables, functions, types, and files for intent and role, not implementation or type. Replaces vague fillers (`data`, `temp`, `handle`), drops noise words (`Manager`, `Helper`, `Util`), strips type-restating and Hungarian suffixes, makes booleans read as predicates, scales name length to scope, and matches the codebase's conventions. Pairs with why-comments: a good name deletes the comment that explained a bad one. |
| [performance](skills/performance/) | Optimize measured hotspots against a stated target instead of guessing: profile before changing anything, set a numeric goal so you know when to stop, take structural wins (N+1 queries, missing indexes, quadratic loops) before micro-optimizations, change one thing at a time and re-measure on realistic data, treat caching as a last resort with an invalidation story, and record before/after numbers with the change. Pairs with debugging, the same evidence-first loop aimed at correctness. |
| [pr-description](skills/pr-description/) | Write the PR description for the reviewer, not the machine: lead with what changed and why, give a reading order and the hunks to scrutinize, flag what is risky or uncertain, state what was left out of scope, and link the issue instead of retyping it. Pairs with small-prs (what goes in the branch) and atomic-commits (how the commits are ordered). |
| [refactoring](skills/refactoring/) | Refactor safely: change structure while preserving observable behavior exactly, keep the tests green after every small step, work in reversible moves instead of a big-bang rewrite, and add characterization tests before touching untested code. Pairs with test-behavior (the green safety net), small-prs (refactor-first sequencing), and atomic-commits (the refactor in its own commit). |
| [reviewing-code](skills/reviewing-code/) | Review a pull request the way a good colleague does: understand the intent before judging the diff, separate blocking defects from suggestions and nits, ground every blocker in a defect or written rule rather than taste, ask genuine questions instead of asserting guesses, leave style to the formatter, stay inside the PR's scope, and end with an explicit verdict. Pairs with branch-review (the multi-agent sweep), pr-description (the author's side), and small-prs. |
| [scoped-commits](skills/scoped-commits/) | Write commit messages in the [Scoped Commits](https://scopedcommits.com) style: `scope: description`, the way Linux, Go, Git, FreeBSD, and nixpkgs write their history. Includes a concise, plain-ASCII house style for the message text (no emoji, no em dashes, no filler). |
| [secure-coding](skills/secure-coding/) | Write code that holds at the trust boundary: treat every external input as attacker-controlled until validated server-side, parameterize instead of concatenating SQL, shell, HTML, and paths, check authorization at every resource access rather than at the menu, keep secrets out of code, logs, and URLs, use vetted crypto and password hashing, and fail closed when a check cannot complete. Pairs with error-handling (nothing leaks when things fail) and dependencies (the supply-chain half). |
| [small-prs](skills/small-prs/) | Keep each branch or PR down to one reviewable idea, decided before coding: a scope contract for what the change will and will not touch, parked follow-ups instead of drive-by fixes, and big asks split into a planned series of self-contained steps (refactor first, per Kent Beck). Pairs with atomic-commits, which splits the finished tree into commits. |
| [test-behavior](skills/test-behavior/) | Write tests that verify observable behavior instead of pinning the mechanism: assert on outcomes rather than mock calls and call counts, mock only at boundaries you don't control, name tests as behavior claims, cover boundaries and error paths, and reproduce every bug in a failing test before fixing it. Pairs with adr-workflow, whose tagged tests are the executable spec. |
| [why-comments](skills/why-comments/) | Write code comments that explain why, never what. When a comment is warranted (constraints, workarounds, rejected alternatives) versus noise (narrating the next line, section banners, reviewer-directed remarks), docstrings as contracts, TODO hygiene, and what never to delete. |
| [writing-docs](skills/writing-docs/) | Write documentation for the reader who arrives with a task: lead the README with what the thing is and a copy-pasteable quickstart, keep tutorials, how-to guides, reference, and explanation separate instead of one mixed page, prefer runnable examples over prose, document the sharp edges and failure modes users actually hit, keep docs next to the code so diffs catch them, and fix or delete stale docs on sight. Pairs with humanize (the prose itself) and why-comments (the same judgment inside the code). |

## Installation

**Claude Code (plugin marketplace)** — this repo is a plugin marketplace, so
each skill installs as a plugin and stays updateable:

```
/plugin marketplace add gabrielbauman/skills
/plugin install scoped-commits@gabrielbauman
```

**Claude Code (manual copy)** — copy a skill into your user or project skills
directory:

```sh
git clone https://github.com/gabrielbauman/skills
cp -r skills/skills/scoped-commits ~/.claude/skills/
# or, per-project: cp -r skills/skills/scoped-commits .claude/skills/
```

**Codex, Cursor, Gemini CLI, and other agents** — install with the
[skills.sh](https://skills.sh) CLI, which places skills in the right directory
for whichever agent it detects:

```sh
npx skills add gabrielbauman/skills
```

Or copy a `skills/<name>/` directory anywhere the [Agent Skills
format](https://agentskills.io) is supported.

## Repository layout

```
skills/
└── <skill-name>/
    ├── SKILL.md               # the skill itself
    ├── references/            # docs the skill loads on demand
    ├── scripts/               # executable tooling bundled with the skill
    └── evals/                 # test prompts and fixtures for skill evaluation
```

## License

MIT — see [LICENSE](LICENSE).
