---
name: dependencies
description: "Manage third-party dependencies as long-term liabilities, not free code: decide when a package earns its place versus writing the function yourself, vet it before adding (maintenance, transitive tree, license, install scripts, name spelled exactly right), commit the lockfile, bump one dependency at a time with the upstream changelog read first, keep bumps out of feature branches, and remove packages that no longer pay rent. Use whenever adding, upgrading, auditing, or removing a package, editing package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod, Gemfile, or any lockfile, handling a security advisory or a Dependabot/Renovate PR, or choosing between a library and hand-rolling. Pairs with small-prs and atomic-commits, which keep each bump its own reviewable change, and secure-coding, which covers the code you write around the packages."
---

# Dependencies

The default treatment of dependencies is asymmetric: adding one takes a
single install command and no thought, while living with it lasts
years. Each package arrives with its transitive tree, its release
cadence, its security advisories, its maintainer's attention span, and
its install scripts, and all of it now ships inside your product. The
cost is real but deferred, which is why nobody weighs it at install
time, and why mature projects carry dozens of packages nobody can
justify.

The corrective is to treat every dependency operation, add, bump, or
remove, as a decision with a reason someone could review.

## Adding: make the package earn its place

A dependency is justified when it encapsulates real expertise you
should not rebuild: crypto, parsers for gnarly formats, protocol
clients, timezone handling. It is not justified when it wraps twenty
lines you could write and own: left-pad, is-odd, a `chunk()` function.
For the small case, write the function; the whole cost of maintaining
twenty lines you understand is less than the cost of tracking one
package you don't. The middle ground, a few hundred lines of
non-expert code, is a judgment call; make it consciously, not by
install-command reflex.

Before adding, spend the five minutes of vetting the install command
skips:

- **Maintenance**: last release date, open issue response, whether it
  is one person's abandoned weekend. You are choosing a maintainer,
  not just code.
- **Transitive weight**: what comes with it. A helper that drags in
  forty packages costs forty packages.
- **License**: compatible with how you ship. A GPL library in a
  proprietary binary is a legal defect you installed on purpose.
- **The exact name**: typosquats live one transposition from popular
  packages, and `requets` will happily install. Copy the name from the
  project's own docs, never from memory.
- **Install scripts**: a postinstall hook runs arbitrary code on every
  developer machine and CI runner at install time. Know that it exists
  before it does.

State the reason in the commit that adds it: what it is for and why it
beat writing it. That sentence is what lets a future audit answer "can
this go?"

## Version discipline

Commit the lockfile, always. Without it, "works on my machine" and CI
are running different code, and every fresh install is an unreviewed
upgrade. The manifest says what you want; the lockfile says what you
got; both are source.

Applications pin exactly (via the lockfile); libraries declare
compatible ranges, because a library that pins exact versions forces
its version conflicts onto every consumer. Do not copy an
application's pinning habit into a published package or vice versa.

## Updating: one bump, eyes open

Read the release notes before bumping, not after the breakage. You are
looking for three things: breaking changes and their migration steps,
behavior changes that will not throw but will differ, and whether the
jump crosses a major version. For a major bump, grep your code for the
APIs the migration guide names before touching the manifest; the
compiler will not catch a renamed config key.

Bump one dependency (or one deliberate group, like a framework and its
plugins) per commit, and keep bumps out of feature branches. The
reason is bisection: when something breaks a week later, `git bisect`
lands on "bump lib X 3.1 -> 4.0" and the suspect list has one name. A
feature commit that also bumps four packages destroys that, and the
reviewer of the feature cannot see your logic through 3,000 lines of
lockfile churn.

Update on a cadence you choose, not only under duress. Small regular
bumps are each easy to verify and revert; the five-major-versions leap
forced by a security patch on an abandoned branch of your dependency
tree is neither. Automated update PRs (Dependabot, Renovate) set the
cadence for you, but they are proposals, not merges: the changelog
still gets read and the suite still gets run per bump.

Security advisories jump the queue but skip no steps: same changelog
read, same test run, same isolated commit. An urgent bump that breaks
production converts one incident into two.

## Removing: dependencies must keep paying rent

Unused and barely-used dependencies do not advertise themselves; they
sit in the manifest accruing advisories. When you notice one, act:

- Used nowhere: remove it in its own commit.
- Used once, for something trivial: inline the twenty lines and remove
  it. The package earned its place once; it no longer does.
- Abandoned upstream but load-bearing: this is a project risk to
  surface and plan around (fork, replace, vendor), not a fact to
  quietly know.

Deprecating and removing is also part of the update path: when a bump
reveals you use none of the parts that changed, ask whether you use
enough of it to keep it at all.

## Bad, then good

The same change, twice:

```
commit: "add user export feature"
  src/export.py            | 120 +++++
  package.json             |   6 +-    (adds csv-writer, bumps lodash,
  package-lock.json        | 2100 +--   axios, and moment "while in there")
```

```
commit 1: "deps: bump axios 1.6 to 1.7 for redirect handling fix"
  (changelog read; no breaking changes; suite green)
commit 2: "export: add user CSV export"
  (uses the stdlib csv module; csv-writer would wrap it in 15 lines
   we can own)
```

The first version cannot be bisected, cannot be reviewed, and added a
package to avoid writing fifteen lines. The second leaves a history
where every dependency change has one name, one reason, and one revert
handle, and one fewer package exists at all.
