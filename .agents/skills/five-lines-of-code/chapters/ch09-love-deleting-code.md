# Chapter 9: Love deleting code

## Core Idea
Code is a liability, not an asset (sunk-cost fallacy): "less is better." Delete anything that doesn't pull its weight — dead features, stale branches, rotted docs, bad tests, festering config, excess libraries — and use the strangler fig and spike-and-stabilize patterns to do it safely.

## Frameworks Introduced
- **Four kinds of incidental complexity** (finer than "technical debt"):
  - **Technical ignorance** — bad decisions from not knowing better; cure = continuous technical excellence + practice (incl. communal programming).
  - **Technical waste** — intentional bad decisions under time pressure (skipping tests/refactoring); sabotage; no excuse.
  - **Technical debt** — deliberately suboptimal *temporary* solution for a gain; fine **iff it has an expiry date**; else it's waste.
  - **Technical drag** — slowdown from the codebase existing (docs, tests, all code); a side effect; remove the parts not paying for themselves.
- **Strangler fig pattern** (Fowler): encapsulate legacy in a namespace + a `Gate` class; make members package-private; route all access through `Gate`; add monitoring (log success/fail per call). Then: most-called → migrate; least-called/always-failing → delete from the gate; TRY DELETE THEN COMPILE finds the now-unused internals.
- **Spike and stabilize** (Dan North): build the change as a throwaway spike (no tests/refactor, minimal integration, *with* monitoring); after 6 weeks, if used → reimplement properly, if not → delete. Source of the six-week rule.
- **Make deletion the default**: revert a frozen project to a branch, tag it, schedule deletion in 6 weeks — unless deliberate action is taken, it disappears.
- **Branch limit** (Kanban WIP limit for branches): set to ≥ #workstations; never break it; exposes CI bottlenecks (integration team, async human review).
- **Knowledge-codification algorithm**: (1) changes often → don't document; (2) used rarely → document; (3) can automate → automate; (4) else learn by heart.
- **Test cleanup**: delete optimistic (tautology — can't fail), pessimistic (always red), and flaky tests; refactor the *code* (not the test) when a test is complicated; specialize slow end-to-end tests into faster targeted ones.
- **Configuration scoped in time**: experimental (feature flags/A/B — remove ≤6 weeks), transitional (in-code, centralized, gated by strangler fig; delete the gate when the transition's done), permanent (must raise usage or be trivial to maintain, else remove).
- **Library triage**: make dependencies visible; classify enhancing (break it → remove, replace later) vs critical; prefer high-quality/stable vendors; "if it hurts, do it more" (update frequently); reimplement small in-house uses of big libs (e.g. one jQuery Ajax call).

## Key Concepts
- **Domain vs incidental complexity** — domain = inherent to the problem (tax law); incidental = added by us and removable.
- **Sunk-cost fallacy** — value comes from outcome, not effort spent; expensive-to-write code is still a liability.
- **Less is better** (Hsee) — adding broken pieces to a dinner set *decreased* its value; adding code can too.
- **Circus/bus/lottery factor** — how many people leaving halts development; keep it high; loss of it = legacy code ("code we're afraid to modify").
- **Intimacy categories** (Dan North) — recent (intimate), familiar (often-used libs), unknown (expensive to relearn); author advantage fades ~6 weeks.
- **Frozen project** — finished feature blocked by an external barrier (access/training); invisible in code; risks becoming legacy.
- **Documentation value** = relevant × accurate × discoverable; failing any one wastes time or causes errors.
- **Test desiderata** — tests must inspire confidence; "never trust a test you haven't seen fail"; zero tolerance for red.
- **Enhancing vs critical library** — enhancing can be pulled without breaking the app; critical can't.
- **Deploy vs release** — feature flags separate them; release becomes a business decision.

## Mental Models
- Code is a liability that earns its keep only through usage; "use it or lose it."
- The cheapest deletion is of code you're still intimate with (~6 weeks); after that it's unknown and expensive to delete.
- Make the default action *deletion*: unless someone deliberately acts to keep it, it goes away.
- If a test's behavior doesn't drive an action (fix or investigate), it has no place; alarm fatigue shadows real failures.
- Configuration has a lifetime; permanent flags must buy usage or be trivial, or they're drag.

## Anti-patterns
- **"It doesn't hurt to keep it"**: false — every line is drag and a thing to consider on every change.
- **Skipping tests to hit a deadline**: sabotage; "done" means following all practices (the car-with-untested-brakes analogy).
- **Technical debt without an expiry date**: it's waste, not debt.
- **Long-lived branches / async human review as a gate**: cheap bytes, expensive merge conflicts and mental overhead; breaks continuous integration.
- **Keeping always-red or flaky tests**: alarm fatigue; zero tolerance for red.
- **Refactoring a complicated test**: the code under test has bad architecture — refactor the code, not the test.
- **Promoting enhancing libraries to critical lightly**: raises audit surface and coupling.
- **Letting experimental config leak to permanent**: splits the user base for complexity, not usage.

## Reference Tables

| Thing | Default action | Pattern |
|---|---|---|
| Outdated/inaccurate doc | delete (or generalize) | relevance×accuracy×discoverability |
| Frozen project | revert to branch, tag, delete in 6 weeks | make deletion default |
| Legacy code | gate + monitor → migrate most-used, delete least | strangler fig |
| Bad test | delete (optimistic/pessimistic/flaky) or refactor the code | zero red |
| Branch | delete on merge; WIP-limit the rest | branch limit |
| Config | scope in time (experimental/transitional/permanent) | ≤6 weeks for flags |
| Library | enhancing → removable; critical → audit | "if it hurts, do it more" |
| Working feature | delete if cost > usage | less is better |

## Key Takeaways
1. Code is a liability; less is better — delete anything not paying for itself, even working features.
2. Four incidental complexities: ignorance (learn), waste (no excuse), debt (needs an expiry), drag (remove the unused).
3. Strangler fig: gate legacy, monitor, migrate the most-called, delete the least-called; TRY DELETE THEN COMPILE finds dead internals.
4. Spike and stabilize: spike with monitoring, decide in 6 weeks — reimplement if used, delete if not.
5. Make deletion the default — branches/config frozen projects auto-expire unless deliberately kept.
6. Keep a branch WIP limit and zero red/flaky tests; scope config in time; keep dependencies visible and classified.

## Connects To
- **Ch 4**: TRY DELETE THEN COMPILE is the deletion workhorse throughout.
- **Ch 7**: alarm fatigue / broken-window theory reappear for red tests and warnings.
- **Ch 10**: spike-and-stabilize and the 6-week rule recur; deletion enables safe addition.
