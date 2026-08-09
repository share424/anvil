# Chapter 6: Abstract Factory

## Core Idea
Produce **families of related objects** without specifying their concrete classes. Provide an interface with one creation method per product type; each concrete factory yields a full, self-consistent variant (e.g. all-Victorian or all-Modern furniture) so mismatched products can never be assembled.

## Frameworks Introduced
- **Abstract Factory (a.k.a. Kit)** — creational pattern.
  - When to use: code must work with several **families of related products** that should stay mutually compatible, but concrete product classes are unknown or should stay extensible.
  - How: declare Abstract Product interfaces per product type; declare an Abstract Factory interface with one creation method per product; implement one Concrete Factory per **variant**; the app picks a concrete factory at startup and passes it around.

## Key Concepts
- **Product family**: a set of distinct-but-related products (Chair + Sofa + CoffeeTable) tied by a high-level theme; products of one family can collaborate.
- **Variant**: a complete rendering of the family (Modern, Victorian, ArtDeco); products of one variant are incompatible with another's.
- **Abstract Product**: per-type interface (`Chair`, `Sofa`); every variant implements it.
- **Concrete Product**: variant-specific implementation (`VictorianChair`).
- **Abstract Factory**: interface declaring `createChair():Chair`, `createSofa():Sofa`, … — returns abstract product types.
- **Concrete Factory**: one per variant; creates only that variant's products; method *signatures* still return the abstract product.
- **Selection at startup**: app reads config/environment, instantiates one concrete factory, injects it into all constructing code.

## Mental Models
- Abstract Factory is Factory Method across a *matrix*: rows = product types, columns = variants. Each concrete factory is one column guaranteed consistent.
- The client only sees abstract `GUIFactory`, `Button`, `Checkbox` — so swapping OS = swapping the factory object, never touching client code.
- It's the pattern for "make sure you don't accidentally build a macOS button into a Windows window."

## Anti-patterns
- **Mixing variants in client code**: a Victorian chair paired with a Modern sofa — the mismatch the pattern exists to prevent.
- **Adding product types after the fact**: adding a new abstract product forces adding a method to the Abstract Factory interface *and* every concrete factory — so the pattern favors closed product-type sets. (The documented con.)
- **Returning concrete products from the factory signatures**: couples the client to one variant; signatures must return abstract products.

## Code Examples
Cross-platform GUI factory — one factory per OS, returns OS-consistent controls:
```pseudo
interface GUIFactory is
  method createButton():Button
  method createCheckbox():Checkbox

class WinFactory implements GUIFactory is
  method createButton():Button is   return new WinButton()
  method createCheckbox():Checkbox is  return new WinCheckbox()

class MacFactory implements GUIFactory is
  method createButton():Button is   return new MacButton()
  method createCheckbox():Checkbox is  return new MacCheckbox()

interface Button is  method paint()
class WinButton implements Button is  method paint() is  // Windows style
class MacButton implements Button is  method paint() is  // macOS style
```
The `Application` holds a `GUIFactory` and calls `factory.createButton()`; a WinButton can never be paired with a MacCheckbox because they come from one factory.

## Reference Tables
Product × variant matrix (the conceptual shape):

| | Modern | Victorian | ArtDeco |
|---|---|---|---|
| Chair | ModernChair | VictorianChair | ArtDecoChair |
| Sofa | ModernSofa | VictorianSofa | ArtDecoSofa |
| CoffeeTable | ModernCoffeeTable | VictorianCoffeeTable | ArtDecoCoffeeTable |

Each column = one Concrete Factory; client picks a column, never mixes columns.

## Worked Example
Furniture shop — guarantee matching sets. The customer orders via the factory, never naming concrete classes:

```
f = new VictorianFurnitureFactory()      // chosen at startup from config
chair   = f.createChair()                  // -> VictorianChair
sofa    = f.createSofa()                   // -> VictorianSofa
table   = f.createCoffeeTable()            // -> VictorianCoffeeTable
chair.sitOn()                             // all Victorian, guaranteed
```
Because every product comes from the same factory object, a mismatch (Victorian chair + Modern sofa) is structurally impossible — the client never sees the variant class names, only `Chair`/`Sofa`.

## Key Takeaways
1. Aimed at **families of related products** and their **variants** — its raison d'être is guaranteeing consistency.
2. One concrete factory per variant; creation methods return abstract products so clients stay decoupled.
3. The factory is chosen once at startup from config/environment and injected.
4. Best when the set of product **types** is stable; adding a new product type is the painful axis (touches every factory).
5. Often composed **from** a set of Factory Methods; can itself be implemented as a Singleton, paired with Bridge, or substitute for a Facade.

## Connects To
- **ch05 Factory Method**: Abstract Factories are commonly a set of Factory Methods; AF is the next step when a creator's many factory methods blur its SRP.
- **ch07 Builder**: AF returns a product immediately; Builder constructs it step-by-step.
- **ch08 Prototype**: AF/Builder can use Prototype instead of Factory Methods to produce variants.
- **ch14 Facade**: AF can serve as an alternative to Facade when you only want to hide how subsystem objects are created.
- **ch11 Bridge**: pair with Bridge when abstractions can only work with specific implementations — AF encapsulates those relations.