# Patterns & Techniques — Five Lines of Code

## EXTRACT METHOD (P3.2.1)
**When to use**: a method exceeds FIVE LINES, or a blank line/comment names a group.
**How**: mark grouping → new empty method → put call at top → cut/paste body → compile → add params (and `return p;` for assignments) → pass args → remove obsolete comments.
**Trade-offs**: creates many small methods (a common affix may then seed a class); comments become names and are deleted.

## REPLACE TYPE CODE WITH CLASSES (P4.1.3)
**When to use**: an enum/Boolean drives `if`/`switch` branching.
**How**: make an interface with one `isX()` per value; make each value a class implementing it returning `true` for its own `isX`; replace enum checks with the method calls; remove the enum/switch.
**Trade-offs**: more classes/files; enables PUSH CODE INTO CLASSES and eliminates NEVER USE IF WITH ELSE violations.

## PUSH CODE INTO CLASSES (P4.1.5)
**When to use**: a method primarily uses one object's data (and breaks EITHER CALL OR PASS).
**How**: move the method onto the class; replace field access with `this.`; pass the original `this` as a parameter where needed; simplify the method name.
**Trade-offs**: grows the class interface; the name often simplifies (drops the affix).

## INLINE METHOD (P4.1.7)
**When to use**: a method no longer aids readability (e.g., a one-line wrapper, or a poorly-extracted method to re-assess).
**How**: replace each call with the body; delete the method.
**Trade-offs**: can create long methods; use as a vandalism/anti-refactoring signal (Ch 13).

## SPECIALIZE METHOD (P4.2.2)
**When to use**: a method has generality it doesn't need (a parameter always one value — found by arg-monitoring).
**How**: copy the method per distinct value, drop the parameter and the unused branches.
**Trade-offs**: more methods, less coupling; removes accidental generality.

## TRY DELETE THEN COMPILE (P4.5.1)
**When to use**: finding unused methods/interface methods; cleaning up after refactoring.
**How**: delete a batch of methods; the compiler lists the ones still used (restore those); keep the deletions.
**Trade-offs**: only works when no unrelated errors exist; doesn't find *all* removable generality (pair with arg-monitoring).

## UNIFY SIMILAR CLASSES (P5.1.1)
**When to use**: 2+ classes differ only in a set of constant methods (a basis, ≤ N−1 for N classes).
**How (2 phases)**: (1) make every non-basis method equal — wrap each body in `if(true){}`, replace `true` with `this.basisMethod()===constant`, copy each body into the others as `else if`. (2) add a field per basis method set in the constructor, return the field, make the default a parameter, fix `new`s, delete all but one class.
**Trade-offs**: often exposes a hidden type code (Boolean/enum) → cascade into REPLACE TYPE CODE WITH CLASSES.

## COMBINE IFS (P5.2.1)
**When to use**: adjacent `if`/`else if` with identical bodies (usually engineered during refactoring).
**How**: verify bodies match; delete between the first `)` and `else if` `(`; insert `||`; parenthesize each expression.
**Trade-offs**: simplest pattern; exposes an `||` relation to push into a class as a named method.

## INTRODUCE STRATEGY PATTERN (P5.4.2)
**When to use**: unify behavior across classes, or introduce variance. Postpone the interface until variance is needed.
**How**: EXTRACT METHOD → new class → instantiate in constructor → move method → move dependent fields + accessors → add a `this`-replacing param → INLINE METHOD to reverse step 1.
**Trade-offs**: the most powerful pattern (ultimate late binding); adds a class per variation; prefer it to `if`/`switch`.

## EXTRACT INTERFACE FROM IMPLEMENTATION (P5.4.4)
**When to use**: a second implementation now exists (so an interface is justified — NO INTERFACE WITH ONLY ONE IMPLEMENTATION).
**How**: new interface named like the class → rename the class (`TmpName`) and `implements` it → compile → fix `new`s to the renamed class, add any other errored method to the interface → rename interface fittingly, restore the class name.
**Trade-offs**: lets you postpone interfaces safely; the interface appears exactly when variance does.

## ELIMINATE GETTER OR SETTER (P6.1.3)
**When to use**: a getter/setter exposes a private field (DO NOT USE GETTERS OR SETTERS).
**How**: make it `private` → fix each error with PUSH CODE INTO CLASSES (produces a context-named method, e.g. `drive`→`notifyGreenLight`) → delete the now-unused accessor.
**Trade-offs**: spawns several context-specific methods instead of one getter; stronger encapsulation.

## ENCAPSULATE DATA (P6.2.3)
**When to use**: variables/methods share a common affix (NEVER HAVE COMMON AFFIXES).
**How**: create the class → move variables in (`let`→`private`, simplify names, add temp getters/setters) → fix global-scope errors (pick instance name; replace access; if ≥2 methods error add instance as first param+arg; repeat; instantiate at the old decl site — beware loops) → ELIMINATE GETTER OR SETTER the temp accessors → push affix methods in.
**Trade-offs**: turns global invariants local; more, smaller classes; pass `this`, not private fields.

## ENFORCE SEQUENCE (P6.4.1)
**When to use**: a "call A before B" sequence invariant.
**How (internal variant)**: ENCAPSULATE DATA on the last method → make the constructor call the first method → if the two methods' args connect, make them fields and drop them from the method. The instance *is proof* the precondition ran.
**Trade-offs**: one class per enforced step; removes a whole class of "forgot to init" bugs.

## Strangler fig pattern
**When to use**: legacy code you're afraid to touch.
**How**: encapsulate in a namespace + a `Gate` class; make members package-private; route all access through `Gate`; log success/fail per call. Migrate the most-called, delete the least-called/always-failing (TRY DELETE THEN COMPILE finds dead internals).
**Trade-offs**: gives exact contact points + monitoring; requires waiting in production to gather usage.

## Spike and stabilize
**When to use**: a major change with uncertain usage.
**How**: build as a spike (no tests/refactor, minimal integration, *with* monitoring); after 6 weeks, if used → reimplement properly, if not → delete.
**Trade-offs**: source of the 6-week rule; may throw away the spike; saves refactoring unused code.

## Branch by abstraction
**When to use**: a feature touches multiple code sites (per-site `if`s would spread invariants).
**How**: REPLACE TYPE CODE WITH CLASSES on the flag's Boolean → `Version1`/`Version2` implement an interface → push the `if`s into the classes. Removal: delete one class → delete the interface (NO INTERFACE WITH ONLY ONE IMPLEMENTATION) → inline.
**Trade-offs**: localizes the feature's invariants; more classes during the transition.

## Expand-Contract (DB-style)
**When to use**: safely introducing a breaking change (mirrors duplicate→transform→unify).
**How**: expand (add new, safe) → migrate callers (longest) → contract (delete the old).
**Trade-offs**: temporarily two copies of the behavior.

## Resource pooling
**When to use**: a concurrent system with a bottleneck (theory of constraints).
**How**: convert stages from `Runnable` infinite loops to `Task`s dispatched by a worker pool (or use a load balancer externally); the bottleneck auto-gets max capacity.
**Trade-offs**: higher throughput without complicating domain code; must maintain the pooling code.
