# Chapter 5: Fuse similar code together

## Core Idea
Expose hidden structure in similar code, then unify it: join classes that differ only in constant methods (UNIFY SIMILAR CLASSES), join `if`s with identical bodies (COMBINE IFS), and move variance into its own class (INTRODUCE STRATEGY PATTERN). All without judging what the code does — follow its existing structure.

## Frameworks Introduced
- **UNIFY SIMILAR CLASSES (P5.1.1)**: merge two+ classes that differ only in a set of *constant methods* (methods returning a constant). That differing set is the *basis*; unifying N classes needs at most an (N−1)-point basis.
  - When to use: two+ near-identical classes; want fewer classes + more exposed structure.
  - How (2 phases): (1) make every non-basis method equal — wrap each version's body in `if(true){}`, replace `true` with `this.basisMethod() === constant`, copy each body into the others as `else if`. (2) introduce a field per basis method, set it in the constructor, return the field from the basis method, make the default a parameter, fix compiler errors, then delete all but one class.
- **COMBINE IFS (P5.2.1)**: join consecutive `if`/`else if` with identical bodies by inserting `||` between their conditions.
  - When to use: two adjacent `if`s share a body (usually engineered during refactoring).
  - How: verify bodies match; delete the text between the first `)` and the `else if` `(`, insert `||`, parenthesize each expression.
- **USE PURE CONDITIONS (R5.3.2)**: conditions (after `if`/`while`/middle of `for`) must have no side effects.
  - When to use: always; prerequisite for conditional arithmetic.
  - How: separate query from command — a method either returns or mutates, not both. If you can't change the source, wrap it in a `Cacher` that splits the side-effect (`next()`) from the read (`get()`).
- **INTRODUCE STRATEGY PATTERN (P5.4.2)**: move varying code into its own class so variance becomes instantiation. The most powerful pattern in the book; ultimate late binding.
  - When to use: unify behavior across classes, or introduce variance. Postpone the interface until variance is actually needed.
  - How: EXTRACT METHOD → new class → instantiate in constructor → move method → move dependent fields + add accessors → add a `this`-replacing parameter → INLINE METHOD to reverse step 1.
- **NO INTERFACE WITH ONLY ONE IMPLEMENTATION (R5.4.3)**: never keep an interface with a single implementing class.
  - When to use: always; a lone interface signals variation that doesn't exist and adds boilerplate/mental overhead.
- **EXTRACT INTERFACE FROM IMPLEMENTATION (P5.4.4)**: extract the interface only when variance is needed.
  - How: new interface named like the class → rename the class (e.g. `TmpName`) and make it implement the interface → compile → fix `new`s to the renamed class, add any other errored method to the interface → rename interface fittingly, restore the class name.

## Key Concepts
- **Constant method** — a method that returns a constant; the differing axis that UNIFY SIMILAR CLASSES exploits.
- **Basis** — the set of constant methods that distinguish the classes being unified; a two-method basis is a *two-point basis*. Keep it as small as possible.
- **Conditional arithmetic** — `||`/`|` behave like `+`, `&&`/`&` like `×`; transform a condition to a math equation, simplify, transform back. Mnemonic: the two bars of `||` make a `+`; a `×` hides inside `&`.
- **Pure condition** — no assignment, throw, or I/O in a condition.
- **Strategy vs state pattern** — academic distinction (state = strategy with fields); the book calls all "move code into its own class" a strategy.
- **UML class diagram** — boxes for classes (`interface` above the title); relations: *uses*, *is-a* (inheritance — disallowed by ONLY INHERIT FROM INTERFACES), *has-a* (composition/aggregation). Usually only composition + implementation matter.

## Mental Models
- Refactor without judging: follow the code's existing structure (`||`, identical bodies) to *expose* relations, then push them into classes.
- Joining classes often exposes a hidden type code (e.g. a Boolean `falling`); promote it to an enum, then REPLACE TYPE CODE WITH CLASSES.
- Postpone the interface: introduce a strategy as a plain class, extract the interface only when a second implementation appears.

## Anti-patterns
- **Reusing a name because it fits the same relation**: a method name must include its context (`canFall` ≠ `pushable` even if both test stony/boxy — the call context differs).
- **Keeping a one-implementation interface**: signals false variance, doubles files, slows modification.
- **Side effects in conditions**: break conditional arithmetic and surprise readers; conditions are rarely expected to mutate.

## Code Examples
```typescript
// COMBINE IFS: two ifs with identical bodies
if (map[y][x].isFallingStone()) { map[y][x].rest(); }
else if (map[y][x].isFallingBox()) { map[y][x].rest(); }
// becomes
if (map[y][x].isFallingStone() || map[y][x].isFallingBox()) { map[y][x].rest(); }
```
- **What it demonstrates**: joining identical bodies exposes the `isFalling` relation, which is then pushed into a class as `isFalling()`.

```typescript
// Conditional arithmetic: a(b + c) ... simplify, then push into classes
if ((map[y][x].isStony() || map[y][x].isBoxy()) && map[y + 1][x].isAir()) { ... }
```
- **What it demonstrates**: factor the common `&& map[y+1][x].isAir()` out by treating `||` as `+` and `&&` as `×`.

## Worked Example
**Unifying `Stone` + `FallingStone`** (differ only in `isFallingStone` and an empty `moveHorizontal`). Phase 1: wrap each `moveHorizontal` body in `if(true){}`, replace `true` with `this.isFallingStone()===false`/`===true`, copy the other's body in as `else if`. Phase 2: add `private falling: boolean`, set it in the constructor, make `isFallingStone()` return `this.falling`, make the default a constructor parameter, fix `new`s. Delete `FallingStone`; `new Stone(true)`/`new Stone(false)`. The exposed Boolean is a type code → `enum FallingState` → REPLACE TYPE CODE WITH CLASSES (`Falling`/`Resting` implement `FallingState`) → PUSH CODE INTO CLASSES so `moveHorizontal` lives on the state. `Stone.moveHorizontal` shrinks to `this.falling.moveHorizontal(this, dx)`.

## Reference Tables

| Pattern | Unifies | Trigger |
|---|---|---|
| UNIFY SIMILAR CLASSES | classes | differ only in constant methods (a basis) |
| COMBINE IFS | `if`s | adjacent, identical bodies |
| INTRODUCE STRATEGY PATTERN | methods/classes | variance, or shared behavior to pull out |
| EXTRACT INTERFACE FROM IMPLEMENTATION | (enables the above) | a second implementation now exists |

## Key Takeaways
1. Follow structure, not meaning — refactor similar code without understanding what it does.
2. UNIFY SIMILAR CLASSES merges classes that differ only in constant methods; the differing set is the basis (≤ N−1 methods for N classes).
3. COMBINE IFS turns two identical-bodied `if`s into one `||`-condition, exposing a relation to push into a class.
4. USE PURE CONDITIONS is the prerequisite for conditional arithmetic (`||`=+, `&&`=×); separate query from command.
5. INTRODUCE STRATEGY PATTERN is the book's most powerful tool — variance by instantiation, the ultimate late binding.
6. Postpone interfaces; extract them with EXTRACT INTERFACE FROM IMPLEMENTATION only when variance arrives (NO INTERFACE WITH ONLY ONE IMPLEMENTATION).

## Connects To
- **Ch 4**: builds on REPLACE TYPE CODE WITH CLASSES, PUSH CODE INTO CLASSES, INLINE METHOD, ONLY INHERIT FROM INTERFACES.
- **Ch 6**: the `KeyConfiguration`/`getRemoveStrategy` getters produced here are eliminated next by ELIMINATE GETTER OR SETTER.
- **Gang of Four *Design Patterns***: strategy pattern origin; Martin Fowler *Refactoring*: post-imposing the strategy.
