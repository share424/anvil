# Chapter 15: Flyweight

## Core Idea
Share common, immutable **intrinsic** state across many objects so thousands of them fit in RAM, keeping the per-object **extrinsic** (context) state outside the shared object (passed into its methods). A.k.a. **Cache**.

## Frameworks Introduced
- **Flyweight (Cache)** — structural pattern (an optimization, not architecture).
  - When to use: *only* when the program must support a huge number of similar objects that barely fit RAM, with duplicate state extractable.
  - How: split each object's state into **intrinsic** (shared, immutable, stored once in flyweights) and **extrinsic** (contextual, passed as method params); a Flyweight Factory pools flyweights by intrinsic state and reuses them; contexts pair with a flyweight to represent a full object.

## Key Concepts
- **Intrinsic state**: constant data duplicated across many objects (e.g. a tree's name, color, texture — the big fields); stored in the flyweight, immutable, set only via constructor.
- **Extrinsic state**: per-instance context (e.g. x, y coordinates); moved out of the object, passed into flyweight methods.
- **Flyweight**: object holding only intrinsic state; shared across contexts.
- **Context**: a small object pairing extrinsic state with a reference to a flyweight; represents one logical object cheaply.
- **Flyweight Factory**: pool keyed by intrinsic state; returns an existing flyweight or creates a new one; clients go through the factory, never build flyweights directly.
- **Immutability**: essential — the same flyweight serves many contexts, so it must expose no setters/public fields.
- **Trade-off**: RAM saved, but you may spend CPU recomputing/passing context every call, and the code becomes more confusing.

## Mental Models
- Real-world scenario: millions of bullets sharing one bullet "type" (color + sprite, the expensive fields); only coordinates/vector differ per bullet. Three flyweights (bullet, missile, shrapnel) replace millions of duplicate heavy objects.
- A flyweight is a *reusable template* the client configures at runtime via method arguments.

## Anti-patterns
- **Applying Flyweight without a proven RAM problem**: it's an optimization — measure first, and confirm no simpler fix exists.
- **Mutable flyweights**: breaks sharing; one context's edit would corrupt all others.
- **Forgetting extrinsic sync in parallel arrays**: if context is stored in arrays indexed alongside a flyweight-reference array, they must stay aligned (a single Context class avoids this footgun).

## Code Examples
Tree rendering — `TreeType` is the flyweight, `Tree` the context, `TreeFactory` the pool:
```pseudo
class TreeType is                       // FLYWEIGHT: intrinsic only (name,color,texture)
  field name; field color; field texture
  constructor TreeType(name, color, texture) { ... }
  method draw(canvas, x, y) is
    // 1. create bitmap of this type/color/texture
    // 2. draw at (x, y)

class TreeFactory is                    // FLYWEIGHT FACTORY: pool
  static field treeTypes: collection of TreeType
  static method getTreeType(name, color, texture) is
    type = treeTypes.find(name, color, texture)
    if (type == null)
      type = new TreeType(name, color, texture)
      treeTypes.add(type)
    return type

class Tree is                           // CONTEXT: extrinsic (x,y) + flyweight ref
  field x, y
  field type: TreeType
  constructor Tree(x, y, type) { ... }
  method draw(canvas) is  type.draw(canvas, this.x, this.y)

class Forest is                         // CLIENT: many tiny Tree contexts reuse few flyweights
  field trees: collection of Tree
  method plantTree(x, y, name, color, texture) is
    type = TreeFactory.getTreeType(name, color, texture)
    trees.add(new Tree(x, y, type))
  method draw(canvas) is  foreach (tree in trees) do  tree.draw(canvas)
```
- **What it demonstrates**: a `Forest` of millions of `Tree`s reuses a handful of `TreeType` flyweights; the heavy texture data lives once per species, each tree carries only two ints + a reference.

## Reference Tables
State split:

| State | Where it lives | Mutability | Examples |
|---|---|---|---|
| Intrinsic | inside the flyweight | immutable (ctor only) | name, color, texture |
| Extrinsic | passed into methods / held by context | varies per instance | x, y coordinates |

Flyweight vs. Singleton:

| | Singleton | Flyweight |
|---|---|---|
| Instances | exactly one | many, differing intrinsic state |
| Mutability | may be mutable | immutable |

## Worked Example
Forest renderer: a million trees are `(x, y, TreeType)`. Before — each `Tree` owned its own color+texture buffers → RAM exhaustion. After — `TreeType("Oak", green, oakTexture)` is created once by `TreeFactory` and referenced by every oak `Tree`; the million `Tree` contexts hold only two ints and a pointer. `draw(canvas)` passes `x,y` into `TreeType.draw`, so the shared intrinsic state is reused while each tree still renders at its unique position.

## Key Takeaways
1. Flyweight is an optimization — verify a real RAM problem and no simpler cure first.
2. Split state into intrinsic (shared, immutable, in the flyweight) vs extrinsic (per-instance, passed in).
3. A factory pools flyweights so clients reuse them by intrinsic-state key.
4. Move extrinsic state into a Context (or parallel arrays) — contexts are cheap because the heavy fields are shared.
5. You trade RAM for CPU (recomputing/passing context) and code clarity.
6. Flyweights are immutable; they differ from a Singleton (many instances, varying intrinsic state).

## Connects To
- **ch12 Composite**: shared leaf nodes of a Composite tree are natural Flyweights.
- **ch14 Facade**: Flyweight = many small objects; Facade = one object for a subsystem (opposite concerns).
- **ch09 Singleton**: same structural idea of shared instance, but Flyweight has many immutable instances.
- **ch13 Decorator**: heavy Composite/Decorator graphs can clone via Prototype cheaply once Flyweight trims their memory.