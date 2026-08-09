# Chapter 12: Composite

## Core Idea
Compose objects into a tree structure and treat individual objects and compositions *uniformly* through a common Component interface. A container delegates a request recursively to its children and "sums up" the results, so the client never distinguishes a leaf from a sub-tree. A.k.a. **Object Tree**.

## Frameworks Introduced
- **Composite (Object Tree)** — structural pattern.
  - When to use: your core model is a tree; you want the client to treat simple and complex elements the same way.
  - How: declare a Component interface of operations common to leaves and containers; Leaf does the real work; Container holds a list of Component children, delegates each request to them, aggregates results; client works only via the interface.

## Key Concepts
- **Component**: common interface for both simple and complex tree elements.
- **Leaf**: end element with no sub-elements; usually does most of the real work.
- **Container / Composite**: element with children (leaves or other containers); doesn't know children's concrete classes; delegates and aggregates.
- **Uniform treatment**: client works with `Component` only — recursion handles the nesting.
- **add/remove on the Component interface?**: puts the operations on the interface so the client can compose uniformly, but leaves get empty/no-op methods — a deliberate ISP trade-off you can choose either way.

## Mental Models
- Real-world analogy: an army hierarchy — orders given at the top flow down through divisions → brigades → platoons → squads → soldiers; each level passes the order along.
- Composite turns "unwrap all boxes and loop, knowing the nesting/classes" into "ask the root for the total and let it recurse."

## Anti-patterns
- **Walk-the-tree in the client with class/nesting checks**: the brittle approach Composite replaces — you must know classes and levels up front.
- **Overgeneralizing the Component interface**: when leaves and containers differ too much, forcing one interface makes it hard to comprehend (the documented con).
- **Container depending on concrete children**: breaks uniformity and OCP; children must be the Component type.

## Code Examples
Graphics editor — `CompoundGraphic` is a composite that recurses:
```pseudo
interface Graphic is
  method move(x, y)
  method draw()

class Dot implements Graphic is
  field x, y
  method move(x, y) is  this.x += x; this.y += y
  method draw() is     // draw a dot

class Circle extends Dot is
  field radius
  method draw() is     // draw a circle

class CompoundGraphic implements Graphic is
  field children: array of Graphic
  method add(child: Graphic) is    // ...
  method remove(child: Graphic) is // ...
  method move(x, y) is
    foreach (child in children) do  child.move(x, y)   // recurse
  method draw() is
    foreach (child in children) do  child.draw()       // recurse, sum bounds

// client groups Selected components into one composite
group = new CompoundGraphic()
foreach (component in components) do  group.add(component)
all.add(group); all.draw()                       // whole tree drawn
```
- **What it demonstrates**: the client "groups" disparate shapes into one compound shape, then `draw()` works identically on a dot, a circle, or a whole compound — recursion walks the tree.

## Reference Tables
| Role | What it does |
|---|---|
| Component | interface common to leaves and containers |
| Leaf | end element, does real work, no children |
| Container (Composite) | holds Component children, delegates+aggregates, recursion |
| Client | talks only to Component |

Composite vs. Decorator (both recursive composition):

| | Decorator | Composite |
|---|---|---|
| Children | exactly one | many |
| Purpose | add responsibility to wrapped object | sum up children's results |
| Cooperate? | Decorator can extend one object inside a Composite tree | — |

## Worked Example
Ordering system: an order holds products *and* boxes of products *and* boxes-of-boxes, with packaging cost. Define `interface Item { getPrice() }`. A `Product.getPrice()` returns its price; a `Box.getPrice()` iterates its `Item` children, sums their prices, adds packaging. The client just calls `order.getPrice()` and recursion descends every nested box and adds packaging at each level — no inspection of nesting or concrete classes.

## Key Takeaways
1. Use Composite only when the core model really is a tree.
2. One interface for leaves and containers → polymorphism + recursion handle the tree.
3. Leaves do the work; containers delegate and aggregate.
4. Clients are decoupled from concrete classes (OCP — add new element types without breaking the tree walker).
5. Putting add/remove on the Component interface violates ISP (empty in leaves) but maximises uniformity — choose deliberately.
6. Composite resembles Decorator but Decorator has one child and adds behavior; Composite sums many.

## Connects To
- **ch07 Builder**: Builder's recursive steps are the natural way to assemble a Composite tree.
- **ch13 Decorator**: structural twins — Decorator = one child + extra responsibility; Composite = many children + aggregation.
- **ch08 Prototype**: cloning beats rebuilding heavy Composite/Decorator trees.
- **ch17 Chain of Responsibility**: a leaf can pass a request through the chain of parent components up to the root.
- **ch19 Iterator**: traverse Composite trees with Iterator.
- **ch26 Visitor**: run an operation over an entire Composite tree.
- **ch15 Flyweight**: shared leaf nodes implemented as Flyweights to save RAM.