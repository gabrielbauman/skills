---
name: scoped-commits
description: Write git commit messages in the Scoped Commits style (scopedcommits.com), where the subject line is "scope: description" — the affected subsystem first, then a short summary — as used by Linux, Go, Git, FreeBSD, and nixpkgs. Use this skill every time you are about to commit when any of these hold: (1) the repository's existing log already uses scope-first subjects like "net/http: fix cookie parsing", (2) you are making the first commit in a brand-new repository, or (3) the project's AGENTS.md, CLAUDE.md, or CONTRIBUTING file says to use scoped commits. Also use it when asked to write, rewrite, or review commit messages in this style. Do not use Conventional Commits prefixes (feat:, fix:, chore:) in these repositories.
---

# Scoped Commits

Scoped Commits is a commit message convention where the subject line leads with the
**scope** — the subsystem, area, or module the commit touches — instead of a change
type. It is the style used by Linux, FreeBSD, Git, Go, and nixpkgs.

```
<scope>: <description>

[optional body]

[optional trailer(s)]
```

Real examples:

- `i2c: virtio: mark device ready before registering the adapter` (Linux)
- `net/http/cookiejar: add godoc links` (Go)
- `linuxulator: Return EINVAL for invalid inotify flags` (FreeBSD)
- `gitlab-ci: update macOS image` (Git)
- `xwayland: 24.1.11 -> 24.1.12` (nixpkgs)

The scope comes first because readers scan logs by *where* a change landed:
contributors look for changes relevant to their area, debuggers trace which
component regressed, and incident responders hunt for recent changes to the failing
subsystem. A type prefix (`feat:`, `fix:`) wastes that prime real estate on
information the description already conveys. See
[references/rationale.md](references/rationale.md) for the full justification and
upstream sources.

## When this skill applies

Before committing, check in this order:

1. **Project docs**: if AGENTS.md, CLAUDE.md, or CONTRIBUTING mentions scoped
   commits (or shows `scope: description` examples), follow it.
2. **Existing history**: run `git log --oneline -20`. If subjects follow
   `scope: description` (and are not Conventional Commits types), match them —
   reuse the same scope names, capitalization, and tense you observe.
3. **New repository**: if there is no history yet (first commit), adopt scoped
   commits from the start.

If the history clearly follows some other convention (e.g. Conventional Commits),
follow the project's convention instead — consistency within a repo beats any
global style.

## Choosing the scope

The scope answers "what part of the project does this touch?" Derive it from the
code, not from a fixed list:

- Prefer the directory, package, or module name of the changed files:
  `parser`, `cli`, `docs`, `api`.
- Nest with `/` when the project's layout does, mirroring the path readers would
  grep for: `net/http`, `drivers/gpu`, `skill/references`.
- Reuse scopes already present in `git log` rather than inventing near-duplicates
  (`auth` vs `authentication`).
- A commit spanning a few areas: pick a general umbrella scope, or list scopes
  separated by commas (`parser, cli: unify error output`).
- A sweeping change across the whole tree: use `treewide`, `all`, or `global`
  (match whichever the project already uses).

## Writing the description

The standard itself leaves capitalization, tense, and length to each project — so
match the existing log first. When there is no precedent, use the widely shared
default (Linux/Go house style):

- Imperative mood, completing the sentence "this change modifies the project to
  _______": `add`, `fix`, `remove`, not `added` or `adds`.
- Lowercase first word after the colon, no trailing period.
- Keep the whole subject under ~72 characters. If you can't, your scope may be
  too long or the commit may need splitting.
- Say what the change does, not what you did ("fix nil deref on empty config",
  not "fixed a bug I found").

## Body and trailers

- Add a body when the subject alone can't explain *why* the change is needed or
  *how* it works. Separate it from the subject with a blank line; wrap at ~72
  characters; plain text, no Markdown headings.
- Put metadata in trailers at the end: `Fixes: #123`, `Jira-Ticket: PROJ-123`,
  `Co-Authored-By: ...`. A ticket can alternatively go in parentheses after the
  scope: `auth (PROJ-123): fix token refresh`.

## Special commits

Reverts, merges, and other machinery commits (e.g. `git revert`'s generated
message) may keep their default format — don't force a scope onto them.

## Anti-patterns

- `feat(auth): add login` — Conventional Commits type-first format. Drop the type;
  write `auth: add login`.
- `fix: various fixes` — no scope, vague description.
- `Update code` / `WIP` / `address review comments` — says nothing about where or
  what.
- Inventing a new scope when `git log -- <changed-path>` shows an established one.

## Examples

**Change**: added retry logic to the S3 upload client in `internal/storage/`
**Commit**: `storage: retry S3 uploads on transient errors`

**Change**: bumped a dependency version across the whole repo
**Commit**: `treewide: bump golang.org/x/net to v0.27.0`

**Change**: fixed a crash in the config parser, with context worth recording

```
config: don't crash on empty include list

parseIncludes assumed at least one entry and indexed [0]
unconditionally. An empty `includes:` key in YAML produces a nil
slice, so loading such a config crashed on startup.

Fixes: #482
```
