# Chapter 5: Factory Method

## Core Idea
Define an interface for creating objects in a superclass, but let subclasses decide which concrete class to instantiate. Replacing `new ConcreteProduct()` with a call to an overridable **factory method** decouples the client from concrete products, so new product types are added by subclassing, not editing.

## Frameworks Introduced
- **Factory Method (a.k.a. Virtual Constructor)** — creational pattern.
  - When to use: you don't know upfront which product types your code must work with; you want to give framework users an extension point; you want to reuse (pool) objects instead of always building new ones.
  - How: declare a (often abstract) method in the Creator returning the **Product** interface; Concrete Creators override it to return a Concrete Product; client code depends only on the Creator and Product abstractions.

## Key Concepts
- **Product**: common interface all creatable objects implement (e.g. `Transport` with `deliver()`).
- **Concrete Product**: a specific implementation (`Truck`, `Ship`).
- **Creator**: declares the factory method; its return type *must* be the Product interface. Primary responsibility is usually core logic, *not* creation.
- **Concrete Creator**: overrides the factory method to return a different product.
- **Client code**: works with the Creator/Product via their base interfaces, unaware of the concrete classes.
- **Factory method ≠ constructor**: it can return a cached/pooled/existing object, not just a fresh one.

## Mental Models
- Treat the factory method as a seam: the base class says "give me a product," subclasses say "which one." Adding a product = adding a subclass; existing client code never changes (OCP).
- The Creator is like a software company with a training department — it *can* produce programmers, but its primary job is still writing software.

## Anti-patterns
- **Hardcoding `new ConcreteProduct()` throughout the client**: adding a new product forces changes everywhere — the problem the pattern solves.
- **Forgetting the common Product interface**: subclasses can only vary the product type if all products share a base class/interface, and the factory method's return type is that interface.
- **Many subclasses with a big `switch` in the base factory method**: a smell that the parameter-form (pass a control parameter) or another pattern may fit better.

## Code Examples
Cross-platform dialogs — the base `Dialog.createButton()` factory is overridden per OS:
```pseudo
class Dialog is
  abstract method createButton():Button
  method render() is
    Button okButton = createButton()   // factory call, not `new`
    okButton.onClick(closeDialog)
    okButton.render()

class WindowsDialog extends Dialog is
  method createButton():Button is
    return new WindowsButton()

class WebDialog extends Dialog is
  method createButton():Button is
    return new HTMLButton()

interface Button is
  method render()
  method onClick(f)
```
- **What it demonstrates**: the base `Dialog.render()` business logic is product-agnostic; only `createButton()` varies per subclass. New OS = new subclass, zero edits to `Dialog`.

## Reference Tables
| Role | Responsibility |
|---|---|
| Product | interface common to all producible objects |
| Concrete Product | specific implementation |
| Creator | declares factory method (return type = Product); holds core logic |
| Concrete Creator | overrides factory method → returns a Concrete Product |

Applicability quick rules:
- Don't know product types ahead → use it.
- Let framework users swap components → reduce component creation to a factory method they can override.
- Reuse/pool expensive objects (DB connections, files) → a factory method can return existing instances, a constructor can't.

## Worked Example
Logistics app evolving from trucks-only to land+sea:

| Step | What happens | Client impact |
|---|---|---|
| 1. Define common interface | `Transport { deliver() }`; `Truck`, `Ship` implement it | — |
| 2. Add abstract factory method | ` Logistics { abstract createTransport():Transport }` | client uses `Logistics`, calls `del` |
| 3. Concrete creators | `RoadLogistics.createTransport() → new Truck`; `SeaLogistics → new Ship` | none |
| 4. New transport later | add `AirLogistics → new Plane` | add a subclass only |

Design realization of the core principles: Factory Method = "program to an interface" + "encapsulate what varies" (the `new` calls) + OCP/SRP (creation moved to one place).

## Key Takeaways
1. Replace direct `new` calls with an overridable factory method returning a Product interface.
2. Subclasses vary the product; client code stays product-agnostic (OCP).
3. The factory method can return pooled/cached objects — a constructor never can.
4. A Creator's primary job is usually business logic; creation is secondary, which is why it's factored out.
5. Adding N product types costs N subclasses, not N edits throughout the codebase.

## Connects To
- **ch06 Abstract Factory**: when one creator grows multiple factory methods that blur its responsibility, promote to Abstract Factory.
- **ch08 Prototype**: alternative creation without inheritance's rigidity, but needs complex clone init.
- **ch25 Template Method**: Factory Method is a specialization of Template Method; it can also be a step inside a larger Template Method.