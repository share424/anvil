# Chapter 3: Software Design Principles — Good Design & The Core Principles

## Core Idea
Good design optimizes for **code reuse** and **extensibility** under constant change. Three foundational principles — *Encapsulate What Varies*, *Program to an Interface*, *Favor Composition Over Inheritance* — are the bedrock that nearly every pattern in the catalog builds on.

## Frameworks Introduced
- **Encapsulate What Varies** ("identify the aspects that vary and separate them from what stays the same") — minimize the blast radius of change.
  - When to use: any time a piece of logic is likely to change (tax rules, formatting, strategy) and the surrounding code is stable.
  - How: at the **method level** extract the varying logic into its own method; at the **class level** extract it into its own class and delegate.
- **Program to an Interface, Not an Implementation** ("depend on abstractions, not concrete classes") — make collaboration extensible by inserting an interface between collaborators.
  - When to use: when a class depends on another and you want an extension point for swapping/extending the dependency.
  - How: (1) list what the consumer needs; (2) describe those methods in a new interface; (3) make the dependency implement it; (4) depend on the interface, not the concrete class.
- **Favor Composition Over Inheritance** ("has-a" over "is-a") — avoid inheritance's pitfalls by composing behavior from smaller collaborating objects.
  - When to use: when behavior varies along two or more dimensions (e.g. engine type × transport type × control type), or when you need to swap behavior at runtime.
  - How: extract each dimension into its own class hierarchy and have the main object *delegate* to the right component; replace components at runtime by reassigning references.

## Key Concepts
- **Code reuse (3 levels per Erich Gamma)**: classes (lowest) → design patterns (middle) → frameworks (highest, "don't call us, we'll call you").
- **Extensibility**: designing for future change because the problem, the environment, and the goals all mutate.
- **Method-level encapsulation**: extract varying logic into a single method so changes are localized.
- **Class-level encapsulation**: extract varying responsibilities into a separate class and delegate.
- **Interface as extension point**: depending on an interface lets you add new implementations without touching consumers.
- **Composition vs. aggregation**: composition manages the component's lifecycle; aggregation keeps a looser reference (a car has a driver who may leave).

## Mental Models
- Model the program as a ship with watertight compartments: a change ("mine") should sink one compartment, not the whole ship — that's encapsulation of variation.
- Inheritance is a rigid `is-a`; composition is a swappable `has-a`. When two dimensions vary, inheritance forces *N×M* subclasses; composition needs *N+M* classes.
- Adding an interface makes code more complicated *now* but pays off the first time you add a new implementation without breaking callers.

## Anti-patterns
- **Inheritance for multi-dimensional variation**: produces a combinatorial explosion of subclasses (electric/gas × manual/auto × car/truck…), with duplicated code because a subclass can't extend two parents.
- **Hardcoding varying behavior inline**: e.g. tax rates branching on country inside `getOrderTotal` — every law change touches the wrong method.
- **Depending on concrete classes**: ties the consumer to one implementation; new requirements force edits to the consumer (breaks open/closed).
- **Inheritance breaks the parent's encapsulation**: the subclass sees the parent's internals, coupling them tightly.

## Worked Example
Encapsulate-what-varies on a method: tax logic branches inline vs. extracted.

BEFORE — tax mixed into order total:
```pseudo
method getOrderTotal(order) is
  total = 0
  foreach item in order.lineItems
    total += item.price * item.quantity
  if (order.country == "US")
    total += total * 0.07       // US sales tax
  else if (order.country == "EU"):
    total += total * 0.20      // European VAT
  return total
```

AFTER — tax isolated behind a method:
```pseudo
method getOrderTotal(order) is
  total = 0
  foreach item in order.lineItems
    total += item.price * item.quantity
  total += total * getTaxRate(order.country)
  return total

method getTaxRate(country) is
  if (country == "US") return 0.07
  else if (country == "EU") return 0.20
  else return 0
```

Now a tax-law change touches only `getTaxRate`. When this grows further, it promotes to a class → `TaxCalculator` — which is exactly the seam patterns exploit (Strategy, in ch20).

Composition over inheritance — the multi-dimension problem this book returns to repeatedly:

| Approach | Car types | Subclass count |
|---|---|---|
| Inheritance (cargo × engine × control) | 2×2×2 = 8 | explodes with each new axis |
| Composition (delegate engine / control objects) | compose at runtime | N + M classes, swappable |

## Key Takeaways
1. Good design optimizes two moving targets: reuse and extensibility, because code *will* change.
2. Encapsulate what varies — at method level first, then class level — to localize change.
3. Program to interfaces, not implementations, to create safe extension points.
4. Prefer composition over inheritance whenever behavior varies in more than one dimension or must change at runtime.
5. Adding an interface/indirection has an upfront complexity cost; pay it only where a real extension point is likely.
6. The book's first applied pattern (Factory Method) appears here as a natural consequence of programming to an interface.

## Connects To
- **Ch 1**: composition/aggregation vs. inheritance relations are formalized as a design rule here.
- **Ch 4**: SOLID sharpens these three principles into five testable rules.
- **Most catalog patterns**: Strategy (ch24) = composition+interface; Factory Method (ch05) = program-to-interface; Decorator (ch13) = composition over inheritance.