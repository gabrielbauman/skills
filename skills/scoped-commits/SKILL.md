---
name: scoped-commits
description: "Write git commit messages in the Scoped Commits style (scopedcommits.com): the subject is \"scope: description\", affected subsystem first, as used by Linux, Go, Git, and nixpkgs, with a house style of concise, plain-ASCII text, no emoji, no filler. Use every time you are about to commit when the repo's log already uses scope-first subjects like \"net/http: fix cookie parsing\", when making the first commit in a new repository, or when AGENTS.md, CLAUDE.md, or CONTRIBUTING says to. Do not use Conventional Commits prefixes (feat:, fix:, chore:) in these repositories. Pairs with atomic-commits, which decides what goes in the commit."
---

# Scoped Commits

Scoped Commits is a commit message convention where the subject line leads with the
**scope** (the subsystem, area, or module the commit touches) instead of a change
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
   `scope: description` (and are not Conventional Commits types), match them.
   Reuse the same scope names, capitalization, and tense you observe.
3. **New repository**: if there is no history yet (first commit), adopt scoped
   commits from the start.

If the history clearly follows some other convention (e.g. Conventional Commits),
follow the project's convention instead; consistency within a repo beats any
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

The Scoped Commits standard leaves capitalization, tense, and length to each
project, so structural conventions in the existing log win. Absent precedent, use
the Linux/Go default:

- Imperative mood, completing the sentence "this change modifies the project to
  _______": `add`, `fix`, `remove`, not `added` or `adds`.
- Lowercase first word after the colon, no trailing period.
- Keep the whole subject under ~72 characters. If you can't, your scope may be
  too long or the commit may need splitting.
- Say what the change does, not what you did ("fix nil deref on empty config",
  not "fixed a bug I found").

## Body and trailers

- Add a body when the subject alone can't explain *why* the change is needed or
  *how* it works. Separate it from the subject with a blank line and wrap at
  ~72 characters.
- Put metadata in trailers at the end: `Fixes: #123`, `Jira-Ticket: PROJ-123`,
  `Co-Authored-By: ...`. A ticket can alternatively go in parentheses after the
  scope: `auth (PROJ-123): fix token refresh`.

## House style for the message text

These defaults govern the prose of the whole message. Written project rules
override them; a merely inconsistent log does not. The goal is text that reads
like a careful human wrote it in a terminal, because that is where it will be
read.

**Plain text only.** `git log` renders raw text, so use ASCII punctuation and no
markup: no emoji, no em or en dashes (use a comma, colon, parentheses, or two
sentences), no smart quotes, no arrows or decorative Unicode, no Markdown bold,
headings, or code fences. Refer to identifiers by their bare names.

**Concise.** Get to the point in the first clause. Never open with filler like
"This commit...", "This change...", or "In order to"; the reader already knows
they are looking at a commit. Cut anything that repeats the subject line.

**Precise.** Name the function, flag, file, or error verbatim and give real
numbers. "cut startup from 4s to 300ms by caching the schema" beats
"significantly improve performance". If you can't be specific, you probably
haven't understood the change; go read the diff again.

**No inflated language.** Words like comprehensive, robust, seamless, enhance,
leverage, streamline, and crucial claim quality instead of describing the
change. So do vague subjects like "various improvements" or "minor tweaks".
State what changed and let the reader judge.

**Prose bodies, not diff narration.** Write the body as short paragraphs
explaining why the change is needed and what the diff can't show (constraints,
rejected alternatives, follow-up needed). Do not restate the diff as a bullet
list of "Added X / Updated Y / Removed Z"; anyone can get that from the diff
itself. A plain `-` list is fine only for genuinely parallel items, like four
renamed flags.

**No rhetorical dressing.** No negative parallelism ("this isn't just a fix,
it's a redesign"), no rhetorical questions, no "Key changes:" section headers,
no summaries of the summary.

**Self-contained to the repository.** The message is read from `git log` by
someone who has the repo and nothing else: not this conversation, not your
shell, not the machine you committed from. Refer only to what lives in the
repo (files, symbols, other commits, tracked history). Never reference chat
context ("as you asked", "the approach we settled on", "the error you
pasted") or local environment state (a path under your home directory, an
unmerged branch, terminal output, "the server I had running", a failing test
that only exists in your working tree). Rewrite any such reference into the
durable fact behind it: "fix the crash you saw" becomes "fix nil deref when
config lacks an includes key". If the fact can't be stated from the repo and
the diff, you don't understand the change yet.

**Human, not slop.** If a `humanize` skill is available, invoke it when
writing a body and apply its checklist; the house-style rules above are the
same tells it hunts for, and a permanent record should read like a person
wrote it.

## Special commits

Reverts, merges, and other machinery commits (e.g. `git revert`'s generated
message) may keep their default format; don't force a scope onto them.

## Anti-patterns

- `feat(auth): add login` is the Conventional Commits type-first format. Drop the
  type; write `auth: add login`.
- `fix: various fixes` has no scope and a vague description.
- `Update code` / `WIP` / `address review comments` say nothing about where or
  what.
- `auth: enhance login robustness ✨` breaks the house style three ways: filler
  verb, quality claim, emoji.
- `parser: fix the bug you hit earlier` and `build: point at
  /Users/me/tmp/out` reference chat context and a local path no future reader
  can resolve. State the durable fact instead.
- Inventing a new scope when `git log -- <changed-path>` shows an established one.

When rewriting an existing vague message (e.g. `fix: bug`), don't invent
specifics. Recover them from the change itself (`git show <sha>` or the diff at
hand), and if the change isn't available, ask what it did rather than guess.

## Examples

**Change**: added retry logic to the S3 upload client in `internal/storage/`
**Commit**: `storage: retry S3 uploads on transient errors`

**Change**: bumped a dependency version across the whole repo
**Commit**: `treewide: bump golang.org/x/net to v0.27.0`

**Change**: fixed a crash in the config parser, with context worth recording

```
config: don't crash on empty include list

parseIncludes assumed at least one entry and indexed [0]
unconditionally. An empty "includes:" key in YAML produces a nil
slice, so loading such a config crashed on startup.

Fixes: #482
```

**Body style, bad then good**, for a change that moves rate limiting into
middleware:

```
api: enhance rate limiting ✨

This commit comprehensively improves our rate limiting:
- Added a new middleware
- Updated the handlers to use it
- Removed the old per-handler checks

Key benefit: more robust and seamless request handling!
```

```
api: move rate limiting into shared middleware

Each handler previously ran its own limiter, so limits drifted as
handlers were added (search had none at all). One middleware in
front of the mux applies the same 100 req/min policy everywhere and
drops the six per-handler copies.
```
