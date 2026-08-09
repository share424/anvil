# Chapter 2: Looking under the hood of refactoring

## Core Idea
Refactoring's three pillars: improve readability by communicating intent, improve maintainability by localizing invariants, and do both without affecting code outside scope — enabled by favoring composition over inheritance.

## Frameworks Introduced
- **Favor composition over inheritance (Gang of Four)**: objects hold references to other objects rather than extending classes.
  - When to use: sharing behavior; want change-by-addition.
- **Change by addition (open-closed principle)**: add/change functionality without modifying existing code.
  - Yields programming speed, flexibility, stability (+ easy rollback to old behavior).

## Key Concepts
- **Readability** — code's aptitude for communicating its intent (conventions, naming, whitespace, comments).
- **Maintainability** — how much investigation a change requires; tied to change risk.
- **Fragile system** — changing one place breaks an unrelated place.
- **Global state** — state outside the scope considered (trick: look outside the `{ }`).
- **Invariant** — a property we assume about data but don't always check in code.
- **Nonlocal invariants** — invariants spanning scopes; root of fragility (grocery `daysUntilExpiry` story).
- **Localizing invariants** — things that change together should be together.
- **Technical debt** — cost of unrefactored code, accruing "interest".
- **Domain** — the real-world counterpart software models (users, experts, language, culture).

## Mental Models
- Use braces `{ }` to find global state: everything outside the braces is global to what's inside.
- Think of composition as LEGO: parts built to fit together let you swap/combine quickly.
- Think of inheritance as silent assumptions: adding a method to a parent silently applies to all children (penguin `canSwim` example) — composition forces an explicit decision per class.

## Anti-patterns
- **Inheritance for code sharing**: introduces nonlocal invariants and silent defaults; the compiler won't remind you to override per subclass.
- **Delivering unrefactored code**: borrowing time from the next programmer at interest.

## Code Examples
```typescript
class Penguin implements Bird {
  private bird = new CommonBird();
  hasBeak() { return bird.hasBeak(); }
  canFly() { return false; }   // explicit decision, must add canSwim manually
}
```
- **What it demonstrates**: composition forces per-class decisions (compiler errors remind you), avoiding silent inheritance assumptions.

## Worked Example
Bird library: adding `canSwim` to `CommonBird` — under inheritance, `Penguin` silently inherits `canSwim=false` (human memory is the dependency); under composition, `Penguin` fails to compile until you explicitly add `canSwim`. The compile error is the desired forcing function.

## Key Takeaways
1. Refactor to communicate intent + localize invariants without changing behavior (performance may change; optimize separately).
2. Composition enables change by addition → speed, flexibility, stability.
3. Refactor daily to stop accruing technical debt (Boy Scout rule: leave it better than you found it).
4. Keep refactoring scope small to avoid merge conflicts; reserve the code you refactor.
5. Programming is primarily learning and communicating the domain.

## Connects To
- **Ch 1**: defines the workflow; this chapter defines the why.
- **Nonlocal invariants / composition over inheritance**: recur throughout Part 1 (ch4 inheritance, ch6 encapsulation).