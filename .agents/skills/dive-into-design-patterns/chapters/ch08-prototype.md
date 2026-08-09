# Chapter 8: Prototype

## Core Idea
Copy existing objects without coupling your code to their concrete classes. Give objects a `clone()` method (a "prototype" constructor that copies field values); the client clones an object it received via an interface, never knowing its real class. Pre-built prototypes can even replace subclassing for configuration presets.

## Frameworks Introduced
- **Prototype (a.k.a. Clone)** — creational pattern.
  - When to use: your code shouldn't depend on the concrete class of the objects it copies (e.g. 3rd-party objects passed by interface); to cut down subclasses that only differ in how they initialize; as an alternative to inheritance for configuration presets.
  - How: declare a Prototype interface with `clone()`; each class implements a "prototype" constructor (or the clone logic) that copies all fields — calling the parent's cloning constructor so private fields copy too; optionally back it with a Prototype Registry.

## Key Concepts
- **Prototype**: an object that supports cloning; usually via a single `clone()` method.
- **Prototype constructor**: an alternate constructor taking an existing object of the same class and copying its fields into the new instance.
- **Cloning private fields**: legal because an object can access private fields of other objects of the *same* class.
- **Prototype Registry (optional)**: a name→prototype map (or richer search) of pre-configured prototypes; clients look up and `clone()` instead of constructing.
- **Pre-built prototypes vs. subclasses**: configure a set of objects once, then clone the right one instead of defining a subclass per configuration.
- **Deep vs. shallow copy**: cloning objects with circular references/linked objects is the tricky case the pattern flags.

## Mental Models
- Real-world analogy: mitotic cell division — the original cell *actively* participates in producing the identical copy (industrial prototypes are a weaker analogy because they don't self-copy).
- Polymorphism powers the clone: calling `s.clone()` on a heterogeneous `Shape[]` dispatches each to its own class's clone, yielding proper subclasses, not bare `Shape`s.

## Anti-patterns
- **Copying "from the outside"**: walking an object's fields to copy it breaks on private fields and couples you to the class — delegate to the object's own `clone()`.
- **Forgetting to call the parent's cloning constructor**: subclass private fields (from the superclass) won't copy.
- **Not overriding `clone()` in every subclass**: the base clone could produce an object of the parent class.
- **Cloning objects with circular references naively**: the explicitly flagged hard case — needs careful deep-copy handling.

## Code Examples
Shape hierarchy cloning — the prototype constructor copies fields, `clone()` is one line:
```pseudo
abstract class Shape is
  field X:int; field Y:int; field color:string
  constructor Shape(source: Shape) is   // prototype constructor
    this.X = source.X
    this.Y = source.Y
    this.color = source.color
  abstract method clone():Shape

class Rectangle extends Shape is
  field width:int; field height:int
  constructor Rectangle(source: Rectangle) is
    super(source)                 // copy parent's (private) fields
    this.width = source.width
    this.height = source.height
  method clone():Shape is
    return new Rectangle(this)    // one line, own class name

// client clones polymorphically — doesn't know concrete types
foreach (s in shapes) do
  shapesCopy.add(s.clone())       // each dispatches to its real class
```
- **What it demonstrates**: the client copies a `Shape[]` without knowing whether an element is a `Rectangle` or `Circle`; each `clone()` builds the right subclass with all fields copied (including private ones via `super`).

## Reference Tables
Basic structure vs. registry structure:

| Variant | Extra role |
|---|---|
| Basic | Prototype interface (`clone()`) + Concrete Prototype |
| Registry | + Prototype Registry: name→prototype map; lookup + clone |

## Worked Example
A drawing app keeps a `shapes` array of pre-configured prototypes (a `Circle` at (10,10) r=20, a `Rectangle` 10×20). Duplicating the canvas is `for s in shapes: clones.add(s.clone())` — exact copies appear without the client ever naming `Circle`/`Rectangle`, and without re-running each shape's configuration code. A registry could expose `registry.get("blue-circle").clone()` to obtain a configured object in one call, replacing `BlueCircle` subclasses.

## Key Takeaways
1. `clone()` lets the client copy an object it knows only by interface — no coupling to concrete classes.
2. Put copying in a prototype constructor (safer) and keep `clone()` as a one-liner calling `new MyClass(this)`.
3. Always call the parent's cloning constructor; override `clone()` in every subclass with its own class name.
4. Pre-built, pre-configured prototypes can replace "initialize-only" subclasses.
5. Circular references are the well-known hard case.
6. Prototype avoids inheritance's drawbacks but pays with clone-initialization complexity.

## Connects To
- **ch05 Factory Method**: Prototype is an alternative creation route — no inheritance rigidity, but needs clone init; FM needs no init step.
- **ch06 Abstract Factory**: AF methods can be composed with Prototype instead of plain Factory Methods.
- **ch18 Command**: Prototype helps save copies of Commands into history.
- **ch12 Composite / ch13 Decorator**: heavy Composite/Decorator trees are cheap to clone rather than rebuild.
- **ch21 Memento**: a simpler Memento alternative when the object's state is simple and external links are easy to re-establish.