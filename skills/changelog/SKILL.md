---
name: changelog
description: "Write and update CHANGELOG.md by curating what changed for end users, never by transcribing the git log. Follows the Common Changelog format (common-changelog.org): releases newest first with linked versions and ISO dates, changes grouped under Changed/Added/Removed/Fixed, one-line imperative entries, breaking changes bolded and sorted first with migration pointers. Use whenever asked to update a changelog, add a changelog entry, write release notes, cut or prepare a release, or generate a changelog from commits or git history. Treats git log and git diff as raw input only: commit messages address developers, changelogs address users, and many commits deserve no entry at all."
---

# Changelog

A changelog answers two questions for someone who runs your software: "what do I
get if I upgrade?" and "is it safe?" A git log answers a different question for
a different reader: "why is this line of code the way it is?" Generating one
from the other produces a document that serves neither, which is why
[Keep a Changelog](https://keepachangelog.com), [Common
Changelog](https://common-changelog.org), and every critique of conventional
changelogs say the same thing: commit messages are for developers, changelog
entries are for users.

So the rule this whole skill hangs on: **the git log is raw input, never
output.** Read it to learn what happened; write the changelog from scratch for
the person upgrading.

## Gather the raw material

1. Find the last release: `git describe --tags --abbrev=0`, or the top version
   heading in `CHANGELOG.md`. If they disagree, trust the tags and flag the gap.
2. Read what actually changed since then:
   `git log --reverse --stat <last-tag>..HEAD` for the story,
   `git diff <last-tag>..HEAD` (or `git show <sha>`) wherever a message is
   vague. The diff is the ground truth; commit messages tell you what the
   author thought mattered, which is not the same as what a user will notice.
3. Check the released artifacts if relevant: a flag added to the CLI matters, a
   helper added to an internal package does not.

## Decide what a user would notice

Include a change only if someone running released versions could observe it:

- new features, commands, flags, API endpoints, config options
- changed behavior of anything documented or already relied on
- bug fixes for bugs that shipped in a previous release
- breaking changes, always
- deprecations and removals, including dropped runtimes (Node 18, Python 3.9)
- security fixes and performance changes big enough to feel

Leave out what only contributors can see:

- refactors and internal renames that change no behavior
- CI, build tooling, and test changes
- dev-dependency bumps (a runtime dependency bump can matter; say what it
  fixes or requires, not just the version arithmetic)
- formatting, lint, and typo fixes in code comments
- fixes for regressions introduced after the last release: users never saw the
  bug, so there is nothing to tell them. If the regression was in a new
  feature, fold the fix into that feature's entry.

One commit can produce zero entries; five commits can produce one. Merge
related commits into a single entry and skip pairs that cancel out.

## Format

Use Common Changelog unless the file in front of you already follows something
else (an existing Keep a Changelog file with `Unreleased`, `Deprecated`, or
`Security` sections stays in that style; consistency within a file wins).

- `CHANGELOG.md`, starting with `# Changelog`.
- One `## [VERSION] - YYYY-MM-DD` heading per release, newest first, the
  version linked (reference-style) to the release or tag comparison.
- Changes grouped under `### Changed`, `### Added`, `### Removed`, `### Fixed`,
  in that order, omitting empty groups. Common Changelog has no Deprecated
  group; announce deprecations as entries under Changed.
- Each entry one line, imperative present tense ("Add", "Fix", "Remove"),
  self-describing without its heading, naming the user-visible thing verbatim:
  the flag, command, endpoint, config key, or error message. References go in
  parentheses at the end: `(#123)`.
- Longer explanation belongs in the commit body or linked issue, not here. A
  changelog is for scanning.

Entry prose follows the same rules as good commit prose: plain ASCII, no
emoji, no marketing adjectives ("various improvements", "enhanced robustness"),
no restating the category ("Fixed: fixed a bug where...").

## Breaking changes

Never bury a breaking change mid-list. Prefix it with `**Breaking:**`, sort it
first within its group, and say in the same line what breaks and what to do
instead:

```markdown
### Removed

- **Breaking:** drop support for Node.js 16; upgrade to Node.js 18 or later
```

When a release has several breaking changes or a nontrivial migration, add a
one-line notice directly under the version heading pointing at the upgrade
guide:

```markdown
## [3.0.0] - 2026-07-16

_See [UPGRADING.md](UPGRADING.md) before upgrading from 2.x._
```

## When not to add an entry

Sometimes the honest answer is nothing:

- The diff since the last release is entirely internal (CI, refactors, tests).
  Say so instead of padding the release with noise; a release cut for internal
  reasons can carry a one-line notice ("Maintenance release, no user-facing
  changes") rather than invented entries.
- The change is a fix for something that never shipped. No entry.
- You are asked to "add everything to the changelog": push back with this
  skill's include/exclude test rather than complying literally.

Padding is worse than brevity. Every noise entry costs trust in the entries
that matter.

## Worked example

The log since `v1.3.0`:

```
a1f09b2 ci: cache Go modules in test workflow
4c2d7e8 parser: split tokenizer into internal/token package
7be51c0 cli: add --format json flag to report command
d8811fe config: fix crash on empty includes list
90aa413 cli: fix --format json panic on nil metadata
2f6cc31 deps: bump testify to 1.9.0
e77b0a5 server: drop TLS 1.0 and 1.1 support
```

Bad: the log transcribed. Internal noise gets equal billing, the breaking
change hides in the middle, and two commits describe one feature:

```markdown
## [1.4.0] - 2026-07-16

### Changed

- ci: cache Go modules in test workflow
- parser: split tokenizer into internal/token package
- cli: add --format json flag to report command
- config: fix crash on empty includes list
- cli: fix --format json panic on nil metadata
- deps: bump testify to 1.9.0
- server: drop TLS 1.0 and 1.1 support
```

Good: seven commits become three entries. CI, the refactor, and the test
dependency disappear; the panic fix folds into the feature it patched, because
no released version ever had the panic:

```markdown
## [1.4.0] - 2026-07-16

### Added

- Add `--format json` to the `report` command for machine-readable output ([#211](https://github.com/example/proj/issues/211))

### Removed

- **Breaking:** drop TLS 1.0 and 1.1 support; clients must connect with TLS 1.2 or later

### Fixed

- Fix crash on startup when the `includes:` config list is empty ([#208](https://github.com/example/proj/issues/208))

[1.4.0]: https://github.com/example/proj/releases/tag/v1.4.0
```
