---
name: db-migrations
description: "Change database schemas without breaking the running system: every migration stays compatible with the code before and after it (expand and contract), renames happen as add-backfill-swap, backfills run as separate jobs, destruction ships in its own later deploy, and lock behavior is checked before DDL touches a hot table. Use whenever writing or reviewing a schema migration, renaming or dropping a column or table, changing a type or constraint, adding an index in production, or planning a backfill. Pairs with refactoring, the same keep-it-working-at-every-step discipline applied to code."
---

# Database migrations

Schema migrations get written as if deploys were atomic: one migration
renames the column, the same deploy ships the code that uses the new
name, and on paper they land together. In reality they never do. The
migration runs while the old code is still serving traffic, or the new
code reaches one replica while the migration waits, and in the gap
every write fails. Add that migrations run against production data
volumes with production lock contention, and that a dropped column has
no undo, and schema change becomes the riskiest routine change a team
makes.

The discipline that removes the risk: every deployable step must work
with both its neighbors, and destruction always comes last, alone.

## The compatibility rule

At any moment during a rollout, the schema is one version and the
running code may be the version before or after it (deploys overlap,
replicas lag, rollbacks happen). So every migration must satisfy both:
the currently deployed code keeps working after the migration runs,
and the next code version works before any further migration. If a
change cannot satisfy both in one step, split it into steps that each
do; that is expand and contract:

1. **Expand**: add the new thing alongside the old. New nullable
   column, new table, new index. Nothing reads it yet; old code is
   untouched.
2. **Migrate the code**: deploy code that writes to both old and new,
   and reads from the new with fallback to old.
3. **Backfill**: copy existing data into the new shape (rules below).
4. **Cut over**: deploy code that reads and writes only the new shape.
5. **Contract**: after the cutover has held in production, drop the
   old column or table in its own migration, in its own deploy.

Five steps where one rename used to be, and every one of them is
individually boring, deployable, and reversible until the last. That
is the point: the risk did not disappear, it was divided until each
piece is too small to cause an outage.

The corollary: never rename a column or change its type in place on a
system with running traffic. A rename is an add of the new plus a
later drop of the old, with the steps above between them.

## Backfills are jobs, not migrations

Schema DDL and data backfill have opposite needs. DDL wants to run
once, fast, inside the migration framework. A backfill over millions
of rows wants to run in batches, survive interruption, resume where it
stopped, and throttle when the database is busy; wedged into a
migration it holds locks for hours, times out the deploy, and on
failure leaves the migration half-applied.

So: migrations change shape, jobs move data. Write the backfill as a
batched, idempotent job (each batch safe to rerun) keyed by primary
key ranges, run it outside the deploy pipeline, and make step 4's
cutover conditional on the backfill having verifiably finished (count
the rows where new is null).

## Destruction ships alone, later

Dropping a column, dropping a table, deleting rows: these are the only
steps with no undo, so they get maximum isolation. A drop goes in its
own migration, in its own deploy, only after the code that stopped
using the field has been in production long enough to trust (days, not
minutes; long enough that a rollback of the app code is no longer
plausible). Say in the migration's comment what confirmed the field is
unused; "grep found nothing" is a real answer, "should be fine" is
not.

Write the down migration where it is cheap (a dropped index, an added
nullable column) because it makes rollback mechanical. Where the
migration is genuinely irreversible, say so explicitly in the
migration instead of writing a down that pretends (restoring a dropped
column with null data is not a rollback, it is a second incident).
The honest irreversible marker forces the question "then what is the
backout plan?" while there is still time to answer it: usually a
backup or a snapshot taken immediately before.

## Know what locks

DDL that is instant on the laptop's 200-row table can take a full
table lock on production's 200 million rows. Before writing a
migration for a hot table, know what your database does for that
operation, because the answer changes by engine and version:

- Index creation: use the concurrent variant (`CREATE INDEX
  CONCURRENTLY` in Postgres) or the table blocks writes for the
  duration of the build.
- Adding NOT NULL, defaults, foreign keys: check whether your engine
  version validates existing rows under lock, and use the
  add-invalid-then-validate two-step where it offers one.
- Any DDL: set a lock timeout, so a migration that cannot get its lock
  fails fast and loud instead of queueing behind a long transaction
  while every query in the system queues behind it.

Test migrations against production-shaped volume before production. A
staging database with 1% of the rows tests the syntax and none of the
behavior.

## Migration hygiene

An applied migration is history: never edit it, because every
environment that already ran it will silently diverge from every
environment that runs the edited version. Fix a bad migration by
appending a new one. The exception is a migration that has run nowhere
but your branch, which is still a draft.

One migration per concern, per atomic-commits. The migration adding
the orders index and the migration creating the audit table fail,
revert, and get reasoned about independently only if they are
independent files.

## Bad, then good

Requirement: rename `users.name` to `full_name`.

```sql
-- One deploy: migration plus code using the new name.
ALTER TABLE users RENAME COLUMN name TO full_name;
```

Between the migration running and the new code reaching every
instance, all old-code reads and writes of `name` throw. If the deploy
fails halfway, the schema and the code disagree until a human
intervenes.

```text
Deploy 1: ALTER TABLE users ADD COLUMN full_name text;   -- nullable
Deploy 2: code writes name and full_name, reads full_name ?? name
Job:      batched backfill full_name from name; verify no nulls remain
Deploy 3: code reads and writes only full_name
Deploy 4: (days later) ALTER TABLE users DROP COLUMN name;
          -- irreversible; preceded by a snapshot, and by confirming
          -- no live code version references `name`
```

Every step is compatible with its neighbors, every step before the
last can be rolled back by redeploying, and the one irreversible step
happens alone, after the evidence is in.
