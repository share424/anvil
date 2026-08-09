# Cheatsheet — Five Lines of Code

## The 9 rules (quick)
| Rule | Code | One-line |
|---|---|---|
| FIVE LINES | R3.1.1 | methods ≤ 5 statements (braces excluded) |
| EITHER CALL OR PASS | R3.1.1 | call methods on an object *or* pass it — not both |
| IF ONLY AT THE START | R3.5.1 | an `if` is the first thing in the function |
| NEVER USE IF WITH ELSE | R4.1.1 | `if`-`else` is a decision → use classes |
| NEVER USE SWITCH | R4.3.1 | only allowed switch is on an enum to be eliminated |
| ONLY INHERIT FROM INTERFACES | R4.3.2 | never inherit from classes |
| USE PURE CONDITIONS | R5.3.2 | conditions have no side effects |
| NO INTERFACE WITH ONLY ONE IMPLEMENTATION | R5.4.3 | extract the interface when variance arrives |
| DO NOT USE GETTERS OR SETTERS | R6.1.1 | no getters/setters for non-Boolean fields |
| NEVER HAVE COMMON AFFIXES | R6.2.1 | common affix = a hidden class |

## Decision: which pattern for this duplication?
```
Similar…                  → Pattern
─────────────────────────────────────
statements (in a method)  → EXTRACT METHOD
methods across classes    → ENCAPSULATE DATA (then maybe UNIFY SIMILAR CLASSES)
classes, differ only in
  constant methods        → UNIFY SIMILAR CLASSES
flow, different stmts     → INTRODUCE STRATEGY PATTERN
adjacent ifs, same body   → COMBINE IFS
an enum/Boolean branching → REPLACE TYPE CODE WITH CLASSES
runtime-type inspection   → interface + PUSH CODE INTO CLASSES
```

## Decision: refactor at all?
- Won't change → **don't refactor**.
- Changes unpredictably → refactor **only to avoid fragility**; encapsulate the unrefactored, add no variation points.
- Changes predictably → refactor to accommodate the **past** change types.

## Decision: add an interface?
- Only when a **second implementation** exists (NO INTERFACE WITH ONLY ONE IMPLEMENTATION). Until then: plain class. Extract via EXTRACT INTERFACE FROM IMPLEMENTATION.

## Decision: optimize?
```
Failing perf test?  No  → don't optimize.
                    Yes → refactor first → resource-pool the bottleneck →
                          profile for hot spots → swap data structure /
                          cache by idempotency tier → isolate tuning in `magic` package
```
- Perf test types: benchmark (deadline), load (throughput), performance approval (no >X% regression).
- Big-O lies a little — the profiler doesn't. 80:20: optimize the 20% taking 80% of time.

## Caching safety tiers
| Tier | Safe? | Invariant |
|---|---|---|
| Idempotent fn (external cache) | safe | same args → same result |
| Temporarily idempotent (expiry) | fragile | value stable for `duration` |
| Non-idempotent (internal field) | dangerous | maintain for class lifetime |

## Comments: keep or delete?
```
Outdated / commented-out / trivial      → delete
Documents the code (could be a name)    → EXTRACT METHOD, delete comment
Documents a non-local invariant         → encode in compiler (Ch 7) → else automated test → else keep
TODO/FIXME/HACK (process invariant)     → keep local, drive the count down
```

## Deleting code — the defaults
- Legacy: **strangler fig** (gate + monitor) → migrate most-called, delete least.
- Frozen project: revert to branch, tag, **auto-delete in 6 weeks**.
- Tests: zero tolerance for **optimistic/pessimistic/flaky**; refactor the *code* when a test is complicated; specialize slow tests.
- Branches: **WIP-limit** (≥ #workstations, never break it); delete on merge.
- Config: scope in time — experimental (≤6 wk), transitional (in-code, gated), permanent (must raise usage or be trivial).
- Libraries: enhancing → removable; critical → audit; prefer stable vendors; "if it hurts, do it more."

## Adding code — the safe path
- **Adding > modifying**: new method/endpoint/class can't break existing callers.
- Fear of wrong thing → **spike** (product = knowledge, not code).
- Fear of waste/risk → **fixed 20%** for support tools (reserved Fridays).
- Backward compat → never change a public surface, **add** a new one; version only the outermost layer, in names.
- Unfinished code → **feature toggles** (deploy ≠ release); remove ≤6 wk.
- Multi-site feature → **branch by abstraction** (localize the invariants).

## The invariant ladder (can't → join them)
eliminate → teach the compiler → automated test → document → manual test → pray. **Higher = cheaper long-term.**

## Three rules for safe vandalism (anti-refactoring)
1. Never destroy correct information.
2. Don't make future refactoring harder (prefer easier).
3. The result must be eye-catching.
→ Methods: enums, int/string type codes, magic numbers, comments-as-names, whitespace, naming groups, name context, long methods, many parameters, getters/setters.

## Thresholds & defaults
- **FIVE LINES**: ≤ 5 statements (≈ one pass through the fundamental data structure).
- **6 weeks**: spike-and-stabilize decision point; feature-toggle removal; frozen-project auto-delete; intimacy fade (~Dan North).
- **20%**: cap for nonfunctional/support-tool effort (DevOps Handbook).
- **80:20**: code performance distribution.
- **0**: healthy warning count; tolerance for red/flaky tests.
- **WIP branch limit**: ≥ number of workstations; never break it.

## Tells & smells (fast heuristics)
- If you **can't see a null check**, it's probably null — check one time too many.
- A **common affix** is a class asking to be born.
- A **comment that could be a method name** is an EXTRACT METHOD instruction.
- **Whitespace between statements/fields** = the author's mental grouping (→ EXTRACT METHOD / ENCAPSULATE DATA).
- **`instanceof`/`typeof`/casts** = unexploited structure (→ interface + PUSH CODE INTO CLASSES).
- **A getter returning a private field** = a leak (→ ELIMINATE GETTER OR SETTER).
- **One-implementation interface** = false variance (delete it until a 2nd arrives).
- **"It doesn't hurt to keep it"** = false; every line is drag.
- **Pipeline with no production code** = procrastination, not progress.
