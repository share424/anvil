# Chapter 7: Builder

## Core Idea
Extract the step-by-step construction of a complex object into a separate **Builder**. The same construction code produces different representations (a car vs. its manual) by swapping builders; an optional **Director** encodes reusable construction sequences.

## Frameworks Introduced
- **Builder** — creational pattern.
  - When to use: to kill a "telescoping constructor" (many optional params); to produce different representations of a product with shared steps; to assemble Composite trees or other complex objects whose steps may be deferred/recursive.
  - How: declare a Builder interface of construction steps (`reset`, `setSeats`, `setEngine`, …); one Concrete Builder per representation; (optional) Director calls steps in a known order; the client fetches the result from the builder, not the director.

## Key Concepts
- **Telescoping constructor**: a monster constructor (or a ladder of overloaded ones) with many params, most unused per call — the smell Builder fixes.
- **Builder interface**: declares the construction steps common to all builders.
- **Concrete Builder**: implements steps for one representation; holds the in-progress product; exposes a `getProduct()` (placed on the concrete class, not the interface, since products may have no common interface).
- **Product**: the assembled object; products from different builders need *not* share an interface.
- **Director**: optional; defines step order for popular configurations; hides construction detail from the client.
- **Step-by-step / deferred**: the builder doesn't expose the unfinished product, so clients can't grab a half-built result; steps can run recursively (good for trees).

## Mental Models
- Builder = a recipe with discrete steps; the Director is the chef who knows the recipe order; the Builder is the kitchen that executes each step. Same recipe, different kitchens → different dishes.
- Abstract Factory returns a product *immediately*; Builder hands it over only after the chosen steps ran.
- Reset the builder after `getProduct()` so it's ready to build another — common convention, not mandatory.

## Anti-patterns
- **Cramming every optional parameter into one constructor** (the telescoping constructor) — unreadable calls, mostly-default args.
- **Breeding a subclass per configuration** instead of per representation — combinatorial explosion.
- **Expecting `getProduct()` on the Builder interface** when products share no common interface — statically typed languages can't declare the return type; put it on each concrete builder.

## Code Examples
Same director, two builders → a `Car` and a matching `Manual`:
```pseudo
interface Builder is
  method reset()
  method setSeats(n)
  method setEngine(e)
  method setTripComputer(b)
  method setGPS(b)

class CarBuilder implements Builder is
  private field car:Car
  method reset() is  this.car = new Car()
  method setSeats(n) is  // ...
  method getProduct():Car is
    product = this.car; this.reset(); return product

class CarManualBuilder implements Builder is
  private field manual:Manual
  method reset() is  this.manual = new Manual()
  method setSeats(n) is  // document seats...
  method getProduct():Manual is  // return manual

class Director is
  method constructSportsCar(builder: Builder) is
    builder.reset()
    builder.setSeats(2)
    builder.setEngine(new SportEngine())
    builder.setTripComputer(true)
    builder.setGPS(true)

// client
director.constructSportsCar(new CarBuilder())      // -> Car
director.constructSportsCar(new CarManualBuilder()) // -> Manual
```
- **What it demonstrates**: the *same* `Director` sequence builds two unrelated products (a car and its manual) because both builders implement the same steps differently.

## Reference Tables
| Role | Responsibility |
|---|---|
| Builder interface | declares construction steps common to all builders |
| Concrete Builder | implements steps for one representation; holds + returns the product |
| Product | assembled object; may have no shared interface across builders |
| Director (optional) | defines step ordering for reusable configurations |
| Client | creates builder + director, drives construction, fetches result from builder |

## Worked Example
House-building: instead of a `House(pools, windows, walls, …)` super-constructor or `HouseWithPool`/`HouseWithGarden` subclasses, define `HouseBuilder { buildWalls(); buildDoor(); buildWindows(); buildGarage(); buildPool(); }`. A `WoodBuilder` and `StoneBuilder` implement the same steps differently → a cabin or a castle from the *same* director sequence, calling only the steps each house needs.

## Key Takeaways
1. Use Builder for genuinely complex objects; for simple ones it's overkill (adds classes).
2. The Director is optional — call steps directly from client code when you don't need reusable sequences.
3. Fetch the product from the builder, not the director, unless all products share an interface.
4. The same construction code yields different representations just by swapping builders.
5. Steps can run recursively and be deferred, making Builder a good fit for Composite trees.
6. Builders/Factories/Prototypes can be implemented as Singletons.

## Connects To
- **ch06 Abstract Factory**: AF returns a product immediately; Builder constructs step-by-step.
- **ch08 Prototype**: not inheritance-based; Builder can clone via Prototype; both can be Singletons.
- **ch12 Composite**: Builder is the natural way to assemble a Composite tree recursively.
- **ch11 Bridge**: combine Builder + Bridge — director = abstraction, builders = implementations.