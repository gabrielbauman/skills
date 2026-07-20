# Why scope-first commit messages

This file collects the justifications behind Scoped Commits, condensed from
[scopedcommits.com](https://scopedcommits.com) and the sources it links. Read it
when you need to explain or defend the convention (e.g. in a PR discussion or when
proposing it in a project's CONTRIBUTING file); it is not needed just to write a
commit message.

## Scope is what readers scan for

People rarely read a git log linearly; they scan it looking for changes to a
particular area:

- **Contributors** scan for changes relevant to the code they work on and to
  understand project momentum.
- **Debuggers** trace a regression by finding which component was recently
  modified.
- **Incident responders** need to locate recent changes to the failing subsystem
  fast.

Leading with the scope makes every one of these scans cheaper. This is why the
highest-traffic projects in the industry (Linux, FreeBSD, Git, Go, nixpkgs)
independently converged on it.

## Why not Conventional Commits

The main critiques (Sumner Evans's ["Stop using Conventional
Commits"](https://sumnerevans.com/posts/software-engineering/stop-using-conventional-commits/),
Rich van der Hoff's ["Conventional commits considered
harmful"](https://richvdh.org/conventional-commits-considered-harmful.html), and
[lr0.org's criticism](https://lr0.org/blog/p/cc/)):

- **Priority is backwards.** Conventional Commits puts the type first and makes
  scope optional. But the scope carries the information readers scan for; the
  type is usually evident from the description itself (`fix cookie parsing`
  obviously fixes something). "A commit without a scope is like a sentence
  without a subject."
- **Type prefixes waste the subject line.** A prefix like
  `chore(dowhacky-controller):` burns ~30 of your ~50-72 characters before the
  message starts.
- **"chore" devalues real work.** Labeling cleanup, tooling, and documentation as
  chores frames essential maintenance as boring or unpleasant.
- **Automated changelogs are a false promise.** Commit messages address
  developers; changelogs address users. Generating one from the other produces
  changelogs that serve neither audience (see [Keep a
  Changelog](https://keepachangelog.com/en/1.0.0/#log-diffs), ["Your git log is
  not a changelog"](https://agateau.com/2022/your-git-log-is-not-a-changelog/),
  ["Conventional changelogs
  suck"](https://sophiabits.com/blog/conventional-changelogs-suck), and [Common
  Changelog](https://common-changelog.org/#41-verbatim-copying-of-content)).
  Changelogs deserve to be written deliberately for users.
- **Type-driven automation is fragile.** Semantic-version bumps inferred from
  types break on reverts and accidental breakages, and type-based build triggers
  can become a security liability.

## Upstream style guides

Project-specific rules worth consulting when working in (or imitating) these
codebases:

- Linux: [Submitting patches](https://www.kernel.org/doc/html/v4.14/process/submitting-patches.html)
- FreeBSD: [Writing commit messages](https://freebsdfoundation.org/wp-content/uploads/2020/11/Writing-Commit-Messages.pdf)
- Git: [SubmittingPatches](https://git-scm.com/docs/SubmittingPatches)
- Go: [Commit messages wiki](https://go.dev/wiki/CommitMessage), the source of
  the "this change modifies Go to ___" imperative-mood test, lowercase-after-
  colon, no trailing period, ~72-character wrap.
- nixpkgs: [CONTRIBUTING.md](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md),
  the source of the `pkg: 1.0 -> 1.1` version-bump form and `treewide:` scope.

## What the standard deliberately leaves open

Scoped Commits specifies only the shape (`scope: description`, optional body and
trailers). Capitalization, tense, punctuation, subject length, and the set of
valid scopes are left to each project, which is why matching the existing log
always takes precedence over any default in this skill.
