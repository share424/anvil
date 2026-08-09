# Chapter 12: Avoid optimizations and generality

## Core Idea
Strive for simplicity: generality and optimization both trade simplicity for coupled/invariant-laden code, so demand hard evidence (performance tests, observed usage) before either, and isolate the inevitable exceptions. "Code is efficient until proven otherwise."

## Frameworks Introduced
- **Simplicity as the theme**: generality increases possible callers (coupling) and the ways code can be called; optimization exploits invariants you must track forever. Both fill limited cognitive capacity.
- **Build minimally** (Kent Beck: "maximize the amount of work not done"): the duplicate→transform→unify workflow yields *exactly* the needed generality only if the functionality itself is minimal. Solve the problem you have, not the one you can imagine.
- **Unify things of similar stability**: don't immediately unify new with old; wait until both are similarly stable (the 2nd instance stabilizes faster than the 1st, the 3rd faster still). Premature unification bakes in generality that's hard to remove.
- **Eliminate unnecessary generality**: monitor runtime args — if a parameter is always the same value, SPECIALIZE METHOD; even a few distinct values may justify specialized copies. TRY DELETE THEN COMPILE finds some; arg-monitoring finds more.
- **Optimization requires evidence**: set up automatic performance tests and optimize only when they fail:
  - **Benchmark test** — "method must finish in 14 ms" (real-time/embedded; environment-coupled, run only in production-like).
  - **Load test** — "1000 req/s" throughput (web/cloud; resilient but needs prod-like hardware).
  - **Performance approval test** — "not >10% slower than last run" (decoupled from external factors; catches main-loop slowdowns and cache-miss regressions).
- **Refactor before optimizing**: refactoring localizes invariants; optimization relies on invariants. Encapsulating `average` behind a `NumberSequence` class (EXTRACT INTERFACE FROM IMPLEMENTATION) makes caching or a data-structure swap a one-class change.
- **Let the compiler handle it**: compilers optimize common idioms; "showing off" (`(n & 1) === 0` vs `n % 2 === 0`, `n >> 1` vs `n / 2`) just makes code unreadable with no gain. Postpone optimization so compiler improvements keep speeding your code for free.
- **Theory of constraints** (Goldratt, *The Goal*): in a sequential system of workstations + buffers, exactly one **bottleneck** exists at any time; optimizing non-bottlenecks only fills buffers (upstream) or can't get input (downstream). Only bottleneck optimization affects throughput; it then creates a new bottleneck.
- **Resource pooling**: put all processing resources in a common pool (load balancers externally, thread pools internally); the bottleneck automatically gets max capacity. Convert stages from `Runnable` infinite loops to `Task`s dispatched by a worker pool — throughput rises (201s → 150s for 100 reqs) *without* complicating the domain code in the stages.
- **Guide optimization with metrics**: profile to find **hot spots** (slow methods inside loops); 80:20 applies — optimize the 20% taking 80% of time. Asymptotic big-O is simplified; a "better" algorithm can be slower in practice (cache misses) — only measurement reveals it (lib sorts use O(n²) insertion sort for small data over O(n log n) quicksort).
- **Choose good algorithms/data structures**: swap one data structure for an equivalent-interface one (safe; perf tests catch regressions). Locally switch structures to suit each use site (linked list → array → sort → back, for cache behavior). Prefer ease of implementation unless in a hot spot.
- **Caching** (safety tiers): (1) **idempotent** functions — cache externally, safe (same args → same result); (2) **temporarily idempotent** (mutable data, e.g. a price) — external cache with expiry, more fragile; (3) **non-idempotent** — cache must be internal (e.g. the `total` field), the most dangerous (maintain for the class's lifetime).
- **Isolate performance tuning** (micro-optimizations / magic bit patterns, e.g. Quake's `Q_rsqrt`): the code is effectively locked. Extract to a well-named, well-documented, thoroughly-tested method/class; put all tuned code in a dedicated `magic` package/namespace so the import line signals "do not drill in." It's an altar, not a trash heap.

## Key Concepts
- **Cognitive load** — coupling + invariants are the two consumers; generality and optimization both feed them.
- **Swiss-Army-knife-to-a-chef** — generality's burden can exceed its help; context is everything.
- **Bottleneck / buffer / workstation** — theory-of-constraints vocabulary.
- **Hot spot** — slow method in a loop; the only place optimization pays.
- **Magic bit pattern** — hex magic number exploiting a runtime nuance; maximally locked code.
- **Performance tuning** — micro-optimizations beyond algorithms/concurrency/caching.
- **Ping-Pong rating story** — built an unrequested "exciting matchups" feature; barely used; the supporting generality was the hard-to-remove cost.

## Mental Models
- Generality and optimization are both debts taken against simplicity; pay them only with evidence (a failing perf test, observed repeated args).
- Optimize the bottleneck, then find the new bottleneck; resource-pool so the bottleneck self-balances.
- Refactor first — localized invariants are what optimization stands on.
- Isolate tuning so its complexity can't leak: a `magic` package is a quality contract with future readers.
- Big-O lies a little; the profiler doesn't.

## Anti-patterns
- **Unrequested features / speculative generality**: the Ping-Pong "exciting matchups" — effort + hard-to-remove generality for near-zero usage.
- **Unifying new with old immediately**: bakes in generality before stability; wait for similar stability.
- **Showing off with bit tricks**: compilers already optimize the idioms; you just lose readability.
- **Optimizing a non-bottleneck**: fills a buffer or starves a downstream worker; zero throughput gain.
- **Optimizing without a perf test**: "code is efficient until proven otherwise"; daily optimization trades team productivity for a cheaper resource.
- **Trusting big-O over measurement**: cache behavior can invert the expected ordering.
- **Letting the `magic` package become a dump**: it's a sanctified region — high quality or nothing.

## Reference Tables

| Perf test type | Checks | Coupling |
|---|---|---|
| Benchmark | absolute deadline (14 ms) | environment (run prod-like) |
| Load | throughput (1000 req/s) | hardware (prod-like) |
| Performance approval | no >10% regression vs last run | none (consistent env only) |

| Caching tier | Safety | Invariant |
|---|---|---|
| Idempotent fn (external cache) | safe | same args → same result |
| Temporarily idempotent (expiry) | fragile | value stable for `duration` |
| Non-idempotent (internal field) | dangerous | maintain for class lifetime |

## Key Takeaways
1. Simplicity first — generality and optimization both cost cognitive load via coupling/invariants; demand evidence before either.
2. Build minimally and unify only things of similar stability; monitor args to SPECIALIZE METHOD and discharge generality.
3. Optimize only on failing performance tests; refactor first (localized invariants), then let the compiler handle idioms.
4. Use the theory of constraints: find the bottleneck, resource-pool to self-balance it, profile to find hot spots (80:20), mistrust big-O.
5. Optimize safely: swap equivalent-interface data structures, cache by idempotency tier, and isolate tuning in a well-named `magic` package.

## Connects To
- **Ch 3**: EITHER CALL OR PASS refactoring (extract `length`/`size`) is the precondition that makes `NumberSequence` caching clean.
- **Ch 5**: the `Cacher` that splits side effects from reads; INTRODUCE STRATEGY PATTERN / EXTRACT INTERFACE FROM IMPLEMENTATION enable data-structure swaps.
- **Ch 7**: work with the compiler (idioms over bit tricks); the `CountingSet.total` invariant example originates there.
- **Ch 13**: the `magic` package is the seed of "segregate pristine vs legacy / make bad code look bad."
