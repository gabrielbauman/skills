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
| [changelog](skills/changelog/) | Update CHANGELOG.md by curating what changed for end users instead of transcribing the git log: [Common Changelog](https://common-changelog.org) format, breaking changes bolded first with migration pointers, and rules for which commits deserve no entry at all. |
| [debugging](skills/debugging/) | Debug systematically instead of speculatively: reproduce the failure first, read the whole error instead of pattern-matching to a famous fix, test one hypothesis at a time and revert unverified attempts, isolate before changing code, fix the cause rather than the nearest symptom, and verify against the original reproduction. Pairs with test-behavior, which turns the repro into the permanent regression test. |
| [error-handling](skills/error-handling/) | Handle errors so failures are loud, actionable, and traceable: fail early instead of limping on bad state, never swallow an exception silently, write messages that name what was attempted with which inputs, preserve the underlying cause when rethrowing, catch at the boundary that can act, choose retry vs propagate vs crash, and never leak secrets or internals to users. Pairs with debugging, whose investigations depend on errors reported well in the first place. |
| [humanize](skills/humanize/) | Write prose that reads like a person wrote it, and strip AI tells from existing text: em-dash addiction, negative parallelism, inflated vocabulary, bold-first bullets, manufactured drama. Compact checklist by default, full trope catalog on demand. |
| [logging](skills/logging/) | Write logs an operator can act on during an incident: match the level to the reader and the action (ERROR someone must act, WARN handled, INFO milestone, DEBUG diagnostic), prefer structured key-value fields over interpolated strings so logs are queryable, log the ids and inputs and attempt needed to act instead of a bare `failed`, never log secrets or PII, log at boundaries and state transitions rather than every line, and don't log-and-rethrow one error at every layer. Pairs with error-handling and debugging. |
| [naming](skills/naming/) | Name variables, functions, types, and files for intent and role, not implementation or type. Replaces vague fillers (`data`, `temp`, `handle`), drops noise words (`Manager`, `Helper`, `Util`), strips type-restating and Hungarian suffixes, makes booleans read as predicates, scales name length to scope, and matches the codebase's conventions. Pairs with why-comments: a good name deletes the comment that explained a bad one. |
| [pr-description](skills/pr-description/) | Write the PR description for the reviewer, not the machine: lead with what changed and why, give a reading order and the hunks to scrutinize, flag what is risky or uncertain, state what was left out of scope, and link the issue instead of retyping it. Pairs with small-prs (what goes in the branch) and atomic-commits (how the commits are ordered). |
| [scoped-commits](skills/scoped-commits/) | Write commit messages in the [Scoped Commits](https://scopedcommits.com) style: `scope: description`, the way Linux, Go, Git, FreeBSD, and nixpkgs write their history. Includes a concise, plain-ASCII house style for the message text (no emoji, no em dashes, no filler). |
| [small-prs](skills/small-prs/) | Keep each branch or PR down to one reviewable idea, decided before coding: a scope contract for what the change will and will not touch, parked follow-ups instead of drive-by fixes, and big asks split into a planned series of self-contained steps (refactor first, per Kent Beck). Pairs with atomic-commits, which splits the finished tree into commits. |
| [test-behavior](skills/test-behavior/) | Write tests that verify observable behavior instead of pinning the mechanism: assert on outcomes rather than mock calls and call counts, mock only at boundaries you don't control, name tests as behavior claims, cover boundaries and error paths, and reproduce every bug in a failing test before fixing it. Pairs with adr-workflow, whose tagged tests are the executable spec. |
| [why-comments](skills/why-comments/) | Write code comments that explain why, never what. When a comment is warranted (constraints, workarounds, rejected alternatives) versus noise (narrating the next line, section banners, reviewer-directed remarks), docstrings as contracts, TODO hygiene, and what never to delete. |

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
