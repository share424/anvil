# Chapter 4: SOLID Principles

## Core Idea
SOLID is a mnemonic for five design principles (introduced by Robert Martin) that make designs more understandable, flexible, and maintainable. They are guidelines, not dogma — applying all five everywhere usually over-complicates a program. Be pragmatic.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)** — "a class should have just one reason to change."
  - When to use: when a class grows until you can't hold its details in your head, or one kind of change keeps dragging in unrelated code.
  - How: give each class one part of the functionality, fully encapsulated; split when a class has more than one reason to change.
- **Open/Closed Principle (OCP)** — "classes should be open for extension but closed for modification."
  - When to use: when you must add a feature without risking already-shipped, tested code.
  - How: extend via subclasses or via Strategy-style composition (new implementation of an interface) instead of editing the class. Fix bugs directly; don't subclass around a parent's bug.
- **Liskov Substitution Principle (LSP)** — "you should be able to pass subclass objects for parent objects without breaking client code."
  - When to use: when designing class hierarchies, especially in libraries/frameworks whose clients you can't edit.
  - How: subclasses must stay behavior-compatible — extend the base behavior, don't replace it; honor the formal checklist (below).
- **Interface Segregation Principle (ISP)** — "clients shouldn't be forced to depend on methods they do not use."
  - When to use: when an interface grows "fat" and some implementers must stub methods they don't support.
  - How: break the fat interface into granular role interfaces; implement several in one class if needed.
- **Dependency Inversion Principle (DIP)** — "high-level classes shouldn't depend on low-level classes; both depend on abstractions. Abstractions shouldn't depend on details."
  - When to use: when high-level business logic is coupled to low-level infrastructure (DB, file, network) so that infra churn destabilizes the logic.
  - How: describe low-level operations in a high-level interface (in business terms), make high-level depend on it, have low-level implement it — the dependency direction inverts.

## Key Concepts
- **Reason to change**: each distinct responsibility is a distinct axis of change; one class, one axis.
- **Open vs. closed**: open = can be extended/subclassed; closed = its interface is stable and won't be modified. A class can be both.
- **Substitutability checklist (LSP)**: parameter types ≥ abstract (contravariant); return types ≤ concrete (covariant); exceptions don't widen; don't strengthen pre-conditions; don't weaken post-conditions; preserve invariants; don't mutate parent's private fields.
- **Fat interface**: an interface with methods that not all implementers can meaningfully provide — the smell ISP addresses.
- **High-level vs. low-level**: high-level = business logic that directs; low-level = primitive operations (disk, network, DB).
- **Abstraction in business terms**: `openReport(file)` rather than `openFile(x) + readBytes(n) + closeFile(x)`.

## Mental Models
- SRP: one class = one reason to change; if editing feature A risks feature B, you have too many responsibilities.
- OCP: subclass to add behavior; edit only to fix a bug in the class itself.
- LSP: a subclass must behave as a *valid* stand-in wherever the parent is expected — "is-a" means *behaves-like*, not just *shaped-like*.
- DIP: invert the arrow — define the interface at the high level, push the dependency downward so low-level detail depends on the abstraction.

## Anti-patterns
- **ReadOnlyDocument extends Document and throws on save()**: breaks LSP (client code expecting `save()` now must branch on type) and violates OCP (client coupled to concrete document types). Fix by making the read-only class the *base* and writable a subclass.
- **Fat cloud-provider interface**: assuming all providers share Amazon's full feature set; other implementers must stub or throw for features they lack.
- **High-level class depending on a concrete low-level DB class**: a DB version bump destabilizes the business logic; invert via a high-level read/write interface.
- **Mindless SOLID everywhere**: applying all five simultaneously usually over-engineers a small program.

## Worked Example
LSP violation and fix (the document hierarchy):

BEFORE — `ReadOnlyDocument extends Document`, overrides `save()` to throw:
```
class Document { method save() { ...write to disk... } }
class ReadOnlyDocument extends Document {
  method save() { throw "can't save read-only doc" }   // breaks client code expecting save()
}
```
The client must check the concrete type before calling `save()` — LSP and OCP both broken.

AFTER — read-only becomes the base, writable extends it:
```
class ReadOnlyDocument { method read() { ... } }
class WritableDocument extends ReadOnlyDocument {
  method save() { ...write to disk... }   // only documents that *can* save expose it
}
```
Now anything that can `save()` is a `WritableDocument`; clients no longer branch on type.

DIP applied to budget reporting:

| Before | After |
|---|---|
| `BudgetReport` → `MySQLDatabase` (low-level) | `BudgetReport` → `Database` (high-level interface declared by the report) |
| DB server upgrade churns the report | `MySQLDatabase` implements `Database`; arrow inverted |

LSP quick checklist before adding a subclass:
- [ ] Parameters same or *more abstract* than the parent's
- [ ] Return type same or *more specific* than the parent's
- [ ] Throws no new exception types the parent doesn't throw
- [ ] No stronger pre-conditions
- [ ] No weaker post-conditions
- [ ] Parent invariants preserved
- [ ] Doesn't fiddle parent's private fields

## Key Takeaways
1. SRP: one class, one reason to change — split responsibilities before a class becomes unmanageable.
2. OCP: add features by extending/composing, not by editing tested code; reserve edits for fixing the class's own bugs.
3. LSP: a subclass must be a safe drop-in — extend behavior, never replace or restrict it (use the checklist).
4. ISP: keep interfaces narrow; break fat ones into role interfaces so no implementer stubs methods it can't honor.
5. DIP: define low-level operations as high-level abstractions; invert the dependency so details depend on abstractions.
6. All five are pragmatic guidelines — over-applying them makes a program more complex than it needs to be.

## Connects To
- **Ch 3**: SRP sharpens "encapsulate what varies"; OCP is achieved via "program to an interface" + composition; DIP generalizes it.
- **Catalog**: Strategy (ch24) realizes OCP; Factory Method (ch05) realizes DIP; many patterns exist to keep LSP/ISP satisfiable.