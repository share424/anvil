# Chapter 7: Collaborate with the compiler

## Core Idea
Make the compiler a teammate: design around its strengths (reachability, definite assignment, access control, type checking) and avoid its weaknesses (null, arithmetic, bounds, infinite loops, threading) — then trust it instead of fighting it.

## Frameworks Introduced
- **Compiler as todo list**: rename a method/append `_handled` to an enum to make the compiler list every call site; fix each, then revert the rename.
  - When to use: any mechanical, find-all-references change. Only works when no unrelated errors exist.
- **Compiler-enforced invariants**: ENFORCE SEQUENCE (Ch 6) and `private` access control turn invariants into properties the compiler re-checks every build.
  - When to use: when a local invariant can be expressed in the type system or access modifiers.
- **The invariant ladder** (can't → join them): (1) eliminate → (2) teach the compiler → (3) teach the runtime via automated test → (4) document for the team → (5) manual test → (6) pray. Higher = cheaper long-term; lower = more maintenance.
- **Zero warnings policy**: the only healthy warning count is zero; if rampant, set a descending monthly cap, then enable "warnings as errors". Fights alarm fatigue / broken-window effect.
- **Trust the compiler exclusively**: once invariants are encoded and warnings are zero, a successful compile gives more confidence than reading the code.

## Key Concepts
- **Halting problem** — without running a program you can't know its behavior; being subject to it is the *definition* of a programming language. Compilers use *conservative analysis* (prove no failure) and we can rely only on those.
- **Reachability** — compiler proves a method returns on every path; `assertExhausted(x: never)` forces an exhaustiveness check (the `never` param is unreachable only if all enum cases are handled).
- **Definite assignment** — locals/read-only fields must be assigned before use; read-only fields must be set by end of constructor. Use it to prove a value exists (wrap data in a class with a readonly field).
- **Access control** — `private` is per-class, not per-object (you can read another instance's privates of the same class). Protect invariant-sensitive methods with `private`.
- **Type checking** — the strongest analysis; not binary (a spectrum: Rust borrowing < OCaml inference < Haskell type classes < TypeScript unions < Coq/Agda dependent types). Teaching the compiler properties via types ≈ the most sophisticated static analysis.
- **Conservative analysis** — compiler disallows a program if it can't *prove* safety; that's what we can rely on.
- **Compiler weaknesses**: null dereference, division-by-zero/overflow (arithmetic errors), out-of-bounds, infinite loops, race conditions/deadlocks/starvation. Mitigate by null-checks, BigInteger, traversal/definite-assignment, higher-order loops (`forEach`/streams/LINQ), and avoiding shared mutable data across threads.
- **Three offenses** (fighting the compiler): not understanding types (casts, `any`/dynamic, run-time `Map` types), laziness (default args, class inheritance, unchecked exceptions), and architecture ignorance (getters exposing internals, passing private fields as args — pass `this` instead).
- **Micro-architecture** — architecture affecting this team but not others; broken by getters/setters.

## Mental Models
- Programming is communication (with the computer, other devs, and the compiler) — the compiler is the editor enforcing quality. (Fowler: the "construction" metaphor is damaging.)
- "Data structures are algorithms frozen in time" — a program is the team's domain knowledge frozen in time.
- If you can't see a null check, it's probably null — check one time too many rather than too few; ignore IDE "redundant check" strike-throughs only when certain.
- A cast is a painkiller: helps now, fixes nothing; needing one means someone didn't understand the types.
- Run-time types (passing a `Map<string,_>` instead of a typed object) moves a strength (type checking) into a weakness (out-of-bounds). "Tired of laundry? Burn all your clothes."

## Anti-patterns
- **Casts / `any` / dynamic**: disable the type checker exactly where you need it; parse inputs into custom classes instead.
- **Default arguments**: someone adds a value that shouldn't default and forgets to override (Nemo becomes a mammal). Omit defaults so the compiler forces a decision.
- **Class inheritance**: default behavior + coupling; adding `laysEggs` to `Mammal` silently breaks `Platypus`. (Reinforces ONLY INHERIT FROM INTERFACES.)
- **Unchecked exceptions** for things that can happen: the caller can still crash you. Use checked exceptions; reserve one `Impossible` unchecked exception for invariants you can't express.
- **Exposing internals via getter or by passing a private field as an arg**: external code can mutate your state; pass `this` instead.
- **Ignoring warnings**: alarm fatigue shadows the one warning that matters.

## Code Examples
```typescript
// Reachability + exhaustiveness: `never` forces the compiler to check all cases
enum Color { RED, GREEN, BLUE }
function assertExhausted(x: never): never { throw new Error("Unexpected: " + x); }
function handle(t: Color) {
  if (t === Color.RED) return "#ff0000";
  if (t === Color.GREEN) return "#00ff00";
  assertExhausted(t); // compiler error: Color.BLUE not handled
}
```
- **What it demonstrates**: reachability analysis makes the compiler prove a switch/if-chain is exhaustive.

```typescript
// Definite assignment via readonly field: prove the list is never empty
interface NonEmptyList<T> { head: T; }
class Last<T> implements NonEmptyList<T> { constructor(public readonly head: T) {} }
class Cons<T> implements NonEmptyList<T> {
  constructor(public readonly head: T, public readonly tail: NonEmptyList<T>) {}
}
first([]); // type error — can't construct an empty NonEmptyList
```
- **What it demonstrates**: encoding "non-empty" as a type makes the compiler reject the empty case.

## Worked Example
**Teaching the compiler a local invariant** (`CountingSet.randomElement`). The method must return but the compiler can't prove the loop always hits — it doesn't know `total` equals the element count. Ladder step 1 (eliminate) isn't feasible; step 2 (teach the compiler): add `throw new Impossible()` to satisfy reachability. But that only silences the error — a future `remove` that forgets to decrement `total` still breaks the invariant. So push higher on the ladder only when you can encode the invariant; otherwise the `Impossible` throw is a documented, runtime-only guard, and an automated test (step 3) should cover `remove`.

## Reference Tables

| Compiler ability | Use it to | Limitation |
|---|---|---|
| Reachability | exhaustiveness (`never`) | needs all branches checked |
| Definite assignment | prove a value exists (readonly field) | doesn't mean *useful*, just assigned |
| Access control | localize invariants (`private`) | per-class, not per-object |
| Type checking | encode domain properties | strength is a spectrum |
| — | null/bounds/arithmetic/loop/thread | not checked — guard manually |

## Key Takeaways
1. Know the compiler's strengths (reachability, definite assignment, access control, types) and weaknesses (null, arithmetic, bounds, loops, threads); design for the former, guard the latter.
2. Use the compiler as a todo list (rename/`_handled`) and to enforce sequences, encapsulation, and unused-code detection (TRY DELETE THEN COMPILE).
3. Don't fight it: no casts, no `any`, no run-time `Map` types, no default args, no class inheritance, no unchecked exceptions for possible failures; pass `this`, not private fields.
4. The invariant ladder — eliminate → teach compiler → test → document → manual → pray; higher rungs are cheaper long-term.
5. Zero warnings is the only healthy count; a clean compile, with invariants encoded, gives more confidence than reading the code.

## Connects To
- **Ch 6**: ENFORCE SEQUENCE and `private` encapsulation are recast as "teaching the compiler invariants".
- **Ch 4**: ONLY INHERIT FROM INTERFACES and `assertExhausted`/`never` reappear here as compiler-leverage.
- **Ch 9**: the "delete code" ethos extends the compiler-as-todo-list and TRY DELETE THEN COMPILE.
