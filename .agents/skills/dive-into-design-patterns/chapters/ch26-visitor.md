# Chapter 26: Visitor

## Core Idea
Separate an algorithm from the object structure it operates on. Put each behavior in a **visitor** with one method per concrete element class; elements implement an `accept(visitor)` that calls back the matching `visitXxx(this)` — **double dispatch** routes to the right method without `instanceof` checks. Add behaviors without touching the element classes.

## Frameworks Introduced
- **Visitor** — behavioral pattern.
  - When to use: run an operation over all elements of a complex structure (e.g. a Composite tree); extract auxiliary behaviors out of the main classes; a behavior applies only to some classes of a hierarchy.
  - How: declare a Visitor interface with a `visitXxx` per concrete element; declare an Element interface with `accept(Visitor)`; each Concrete Element's `accept` calls `visitor.visitXxx(this)`; Concrete Visitors implement the behavior per element type; clients `foreach (e in structure) e.accept(visitor)`.

## Key Concepts
- **Visitor interface**: one visiting method per concrete element class (same name allowed with overloading, but distinct parameter types).
- **Concrete Visitor**: implements one behavior (e.g. XML export) with a variant per element type; may accumulate state across the traversal.
- **Element interface**: declares `accept(Visitor)`.
- **Concrete Element**: `accept(v)` redirects to `v.visitXxx(this)` — the element tells the visitor *which* method to run, since the element knows its own class.
- **Double dispatch**: the call is dispatched twice — first on the element (`accept`) and then on the visitor (`visitXxx`), so the correct combination (element type × behavior) runs.
- **Why not method overloading alone?**: the element's runtime class is unknown statically, so the compiler picks the base-`Node` overload; double dispatch solves this.
- **Asymmetry of knowledge**: elements know only the Visitor *interface*; visitors know *all concrete element classes*.

## Mental Models
- Real-world analogy: an insurance agent visits buildings and offers a *policy specialized to the organization* — residential→medical, bank→theft, café→fire/flood. The same agent, different offer per building type.
- Adding a *behavior* (a new export format) is a new visitor — element classes don't change. Adding a *new element class* is painful — every visitor must be updated (the documented con).

## Anti-patterns
- **Adding behavior directly into every element class**: bloats them with alien responsibilities and risks breaking production classes; the problem Visitor avoids.
- **Driving the dispatch with `if (node instanceof City) ...` ladders in the client**: brittle and re-coupling; use `accept` instead.
- **Relying on method overloading to pick the right method**: fails because dynamic element type isn't known at compile time — that's why double dispatch exists.
- **Adding many element classes frequently**: every concrete visitor must grow a new `visitXxx` — Visitor favors *stable element hierarchies, volatile behaviors*.
- **Encapsulation erosion**: visitors may need private fields — make them public (violates encapsulation) or nest the visitor in the element class where supported.

## Code Examples
XML export over a shape hierarchy via double dispatch:
```pseudo
interface Shape is  method move(x,y); method draw(); method accept(v: Visitor)

class Dot implements Shape is
  method accept(v: Visitor) is  v.visitDot(this)
class Circle implements Shape is
  method accept(v: Visitor) is  v.visitCircle(this)
class Rectangle implements Shape is
  method accept(v: Visitor) is  v.visitRectangle(this)
class CompoundShape implements Shape is
  method accept(v: Visitor) is  v.visitCompoundShape(this)

interface Visitor is
  method visitDot(d: Dot)
  method visitCircle(c: Circle)
  method visitRectangle(r: Rectangle)
  method visitCompoundShape(cs: CompoundShape)

class XMLExportVisitor implements Visitor is
  method visitDot(d) is               // export id + center coords
  method visitCircle(c) is            // export id + center + radius
  method visitRectangle(r) is         // export id + top-left + w + h
  method visitCompoundShape(cs) is    // export id + list of child ids

// client — no instanceof, no type tests
exportVisitor = new XMLExportVisitor()
foreach (shape in allShapes) do  shape.accept(exportVisitor)
```
- **What it demonstrates**: the client is one delegation line per shape; each shape's `accept` self-identifies and calls the matching `visitXxx`, so `XMLExportVisitor` gets the exactly-typed element it needs — adding a "HTMLExportVisitor" later is one new class, zero edits to shapes.

## Reference Tables
Stable dimension vs. volatile dimension (when to use Visitor):

| Add frequently | Add rarely | Pattern fit |
|---|---|---|
| new **behaviors** | new **element classes** | Visitor — great |
| new element classes | new behaviors | Visitor — painful (update every visitor) |

| Role | Knows | Responsibility |
|---|---|---|
| Visitor interface | declares `visitXxx` per element | the operations contract |
| Concrete Visitor | all concrete element classes | one behavior, per-type variants |
| Element interface | only Visitor interface | `accept(Visitor)` |
| Concrete Element | its own class | `accept` → `v.visitXxx(this)` |

## Worked Example
A geographic graph with `City`, `Industry`, `SightSeeing`, … node classes must support XML export — but the node classes are in production and can't be risked, and export is an alien responsibility there. Define `ExportVisitor` with `doForCity(City)`, `doForIndustry(Industry)`, `doForSightSeeing(SightSeeing)`. Add a trivial `accept(Visitor v)` to each node that calls the matching `doFor…`. The client loops `foreach (node in graph) node.accept(exportVisitor)` — double dispatch routes each node to its `doFor…`. Later marketing asks for a different format → add `AnotherFormatVisitor`; add an "estimate road maintenance cost" behavior → another visitor. The node classes never change again.

## Key Takeaways
1. Visitor isolates algorithms from the object structure so each can change without forcing the other to bloat.
2. Double dispatch (`accept` → `visitXxx(this)`) replaces `instanceof` ladders and unreliable overloading.
3. Adding a behavior = one new visitor class; the element hierarchy is untouched (OCP for behaviors).
4. Adding an element class = touching *every* concrete visitor; the pattern favors stable element sets, volatile behaviors.
5. A visitor can accumulate state across a traversal — handy for operations over object trees.
6. Cons: visitors may need access to private fields (encapsulation erosion), and every visitor edits on element-class churn.

## Connects To
- **ch18 Command**: Visitor is a "powerful Command" — it executes operations over objects of *many different classes*, whereas a regular command targets receivers of one shape.
- **ch12 Composite**: run a visitor over an entire Composite tree; the visitor can hold intermediate state as it traverses.
- **ch19 Iterator**: pair Iterator + Visitor to traverse a complex structure and apply an operation, even across heterogeneous element classes.