# Chapter 4: Make type codes work

## Core Idea
Replace `else if` chains and `switch`es over type codes by turning enums into interface+classes and pushing the branching into those classes, eliminating `if` and enabling change-by-addition.

## Frameworks Introduced
- **NEVER USE IF WITH ELSE (R4.1.1)**: never use `if` with `else`, unless checking a data type you don't control.
  - When to use: anywhere except I/O edges; map third-party types to your own types at the edge.
- **REPLACE TYPE CODE WITH CLASSES (P4.1.3)**: transform an enum into an interface; values become classes (with temporary `is*` methods).
- **PUSH CODE INTO CLASSES (P4.1.5)**: copy the source method into each class, replace context with `this`, inline constant `is*` methods, drop `if(true)/if(false){}`, rename to permanent name, replace original body with a call.
- **INLINE METHOD (P4.1.7)**: move a method's body to all call sites, then delete it (inverse of EXTRACT METHOD).
- **SPECIALIZE METHOD (P4.2.2)**: duplicate a too-general method, drop/rename a parameter, simplify, switch calls over, delete the general original.
- **NEVER USE SWITCH (R4.2.4)**: never use `switch` unless you have no `default` and `return` in every `case`.
- **ONLY INHERIT FROM INTERFACES (R4.3.2)**: only inherit from interfaces, not classes/abstract classes.
- **TRY DELETE THEN COMPILE (P4.5.1)**: delete a method from an interface, compile; if it errors, undo; else delete from each class — removes unused methods when you know the whole scope.

## Key Concepts
- **Type code** — any `int`/enum/string supporting `===`; enums are the safe form to refactor from.
- **Early binding vs late binding** — `if`-`else` locks the decision at compile time; objects decide at runtime (late binding).
- **Constant method** — a method returning a constant (the differing basis used by UNIFY SIMILAR CLASSES in Ch 5).
- **`assertExhausted(x: never)` trick** — makes TypeScript's switch check exhaustiveness.
- **Code duplication can be good** when the copies should diverge (e.g., per-tile graphics); don't refactor it away blindly.

## Mental Models
- Think of `if`-`else` as a hardcoded decision you wouldn't accept as a hardcoded constant.
- Treat an enum as a smell to be replaced: enum → interface → one class per value → push behavior in.
- Prefer forcing functions over memory: an interface makes the compiler remind you to implement each method in every new class (abstract defaults don't).

## Anti-patterns
- **Abstract classes for shared code**: creates coupling; two subclasses needing only `methodA`/`methodB` force empty overrides; compiler won't remind you on new subclasses.
- **`default` in `switch`**: stops the compiler from revalidating when you add a value (the real reason `switch` is evil).
- **Falling back to inheritance** for the duplicated tile code: the duplication is intentional divergence (rounded keys) — Ch 5 unifies only what should converge.

## Code Examples
```typescript
function handleInput(input: Input) { input.handle(); }
interface Input { handle(): void; }
class Left  implements Input { handle() { moveHorizontal(-1); } }
class Right implements Input { handle() { moveHorizontal(1); } }
```
- **What it demonstrates**: PUSH CODE INTO CLASSES removes the entire `else if` chain by moving each branch into the matching class's method.

## Worked Example
`handleInput` had a 4-way `else if` on `Input` enum. REPLACE TYPE CODE WITH CLASSES: introduce `Input2` interface with `isLeft/isRight/isUp/isDown`, four classes returning their own `true`/`false`s, rename enum to `RawInput` (compile errors show all uses), replace `===` with `is*`, replace `Input.LEFT` with `new Left()`, rename `Input2`→`Input`. PUSH CODE INTO CLASSES: paste `handleInput` into each class as `handle`, replace `input` with `this`, inline the `is*` returning constants, delete `if(false)`/keep `if(true)` body, rename to `handle`, original body becomes `input.handle()`. INLINE METHOD removes the now-trivial wrapper. `drawMap`'s giant `else if` over `Tile` is refactored the same way, with `transformTile`/`assertExhausted` as the only allowed `switch` (edge mapping from integer indices).

## Key Takeaways
1. `else`/`switch` belong only at I/O edges; replace them with REPLACE TYPE CODE WITH CLASSES + PUSH CODE INTO CLASSES.
2. Migrate ints/strings to enums first, then enums to classes — only then is the refactoring safe.
3. SPECIALIZE METHOD removes harmful generality; specialized methods become unused sooner and get deleted.
4. ONLY INHERIT FROM INTERFACES — never abstract classes; share code via composition (Ch 5 strategy).
5. INLINE METHOD and TRY DELETE THEN COMPILE are the deletion tools that clean up after pushing code into classes.

## Connects To
- **Ch 3**: `handleInput` was the leftover that EXTRACT METHOD couldn't shrink; this chapter solves it.
- **Ch 5**: the `||` groupings preserved here (`isEdible`, `isPushable`) and duplicated tile code feed UNIFY SIMILAR CLASSES/INTRODUCE STRATEGY PATTERN.
- **Ch 13**: enums/ints-as-type-codes are revisited as safe vandalism techniques.