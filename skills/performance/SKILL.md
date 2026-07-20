---
name: performance
description: "Optimize measured hotspots against a stated target instead of guessing: profile before changing anything, set a numeric goal so you know when to stop, take structural wins (N+1 queries, missing indexes, quadratic loops) before micro-optimizations, change one thing at a time and re-measure, and treat caching as a last resort. Use whenever something is slow, when asked to optimize, speed up, or profile code, when reviewing a change justified by performance, when tempted to add a cache, or when a latency, throughput, memory, or cost target is in play."
---

# Performance

Performance work fails by guessing twice: guessing where the time
goes, then guessing that the change helped. The result is a codebase
that accretes clever loops, hand-rolled caches, and unreadable
"optimizations," none measured, while the actual slow thing (a query
per row, a missing index, a synchronous call to another service in a
loop) sits untouched, because intuition about hotspots is reliably
wrong and nobody checked.

Optimization is debugging with a stopwatch: same evidence-first loop,
except the failing behavior is a number. Everything below is that
loop.

## Get a number before touching code

First, make the slowness reproducible and measured: a request you can
replay, a script you can time, a benchmark you can rerun, executed on
data shaped like production. Record the baseline. Without it, "feels
faster" is the performance equivalent of "can't reproduce," and you
will not be able to tell a 40% win from noise, or notice that your
change made things worse.

Define which number, because they trade against each other: p95
latency, throughput, memory ceiling, startup time, cloud cost.
Optimizing average latency can worsen the p99 that users actually
complain about; a memory win can cost latency. Name the metric the
complaint is about.

Beware the benchmark that lies: cold caches on the first run and warm
on the rest, the 100-row dev table standing in for the 10M-row
production one, the laptop with nothing else running standing in for
the contended shared host. Realistic data shape and volume matter more
than measurement precision.

## Set a target so you can stop

"As fast as possible" has no finish line, and past a point every
further win costs clarity, and the complexity is permanent while the
milliseconds may not matter. Set the target from the requirement:
"checkout p95 under 800ms," "import completes inside the nightly
window," "fits in the 512MB container." When the number is met, stop;
unspent optimization budget converts into readable code.

If nobody can say what number is needed, that is the first finding to
report, because it decides whether there is any work to do at all.

## Profile: the hotspot is not where you think

Do not scan the code for slow-looking constructs; run a profiler and
read where the time actually goes. Decades of consistent experience:
the bottleneck is somewhere surprising, and effort spent by intuition
lands on code that costs 2% of the total. The 2x win in string
handling does nothing while 90% of the wall time is one unindexed
query.

Profile the real workload, not a toy: the actual request path, the
actual batch job, with realistic concurrency. Look for time (CPU
profile, flame graph), waiting (I/O, locks, external calls), and
allocation, and notice which one dominates before choosing a fix;
a CPU fix does nothing for a workload that is 95% waiting on the
network.

## Take the structural wins first

Costs come in tiers, and the tiers differ by orders of magnitude. Fix
in tier order:

- **Round trips**: the N+1 query (one query per row of a parent
  query), the API call inside a loop, chatty protocols. Batch them:
  one query with a join or `IN`, one bulk request. A thousand 1ms
  round trips is a second of pure overhead no micro-optimization
  touches.
- **Missing indexes**: a full table scan hiding behind an innocent
  `WHERE`. The query plan (`EXPLAIN`) says so directly; read it
  instead of guessing.
- **Algorithmic complexity**: the quadratic loop (membership tests
  against a list inside a loop, repeated `+` string building, nested
  scans) that was invisible at n=100 and is the whole runtime at
  n=100k. Fix the shape: sets and dicts for membership, joins for
  matching, sorting once.
- **Redundant work**: the same value computed in every iteration, the
  file re-read per call, the config parsed per request. Hoist it.
- Only then, **micro-optimizations**: shaving allocations, tightening
  inner loops. These matter in hot inner loops the profiler has
  named, and almost nowhere else.

Structural wins usually make the code simpler; micro-optimizations
usually make it worse. That asymmetry is another reason for the order.

## One change, then re-measure

Change one thing, rerun the same measurement, record the delta. Two
optimizations applied together cannot be credited separately, and if
the pair helps, you may be keeping a harmful change masked by a good
one. The rule is debugging's revert discipline with a number attached:
an optimization that does not move the metric is not an optimization,
it is complexity, and it gets reverted no matter how clever it is.

Keep the receipts: the before and after numbers go in the commit
message or PR description, with how they were measured. "Speeds up
import" ages into folklore; "import of 500k rows: 190s to 14s,
measured by scripts/bench_import.py" can be rechecked when someone
touches the code next year.

## Caching is the last resort

A cache looks like a free win and is actually a correctness liability
on the payroll: invalidation bugs (the classic hard problem),
staleness windows users see, memory growth, cold-start cliffs, and
one more stateful thing that makes every future bug "unless the cache
is involved." Reach for it after batching, indexing, and algorithmic
fixes are exhausted, and arrive with answers written down: what
invalidates the entry, what staleness is acceptable, what bounds the
size, what happens on a miss storm.

## Bad, then good

Report: "the orders dashboard takes 12 seconds."

```text
Guess-driven: rewrite the currency formatter in a faster style, add
an unbounded module-level cache on get_user(), switch the JSON
library. "Feels snappier." Dashboard: 11.8s.
```

```text
Measure-driven: replay the dashboard request against a
production-sized snapshot: 12.1s baseline. Profile: 93% of wall time
in the queries; log shows 1 query for orders then 1 per order for its
customer: 2,400 queries. Join the customer in the orders query
(one change), re-measure: 1.9s. EXPLAIN shows a scan on
orders.created_at; add the index, re-measure: 0.6s. Target was 1s;
stop. Both numbers and the replay command go in the PR.
```

The first version touched three subsystems and cannot say what any
change did. The second made two changes, can prove both, knew when to
stop, and left the formatter alone because the profiler never
mentioned it.
