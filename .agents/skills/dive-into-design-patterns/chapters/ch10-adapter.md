# Chapter 10: Adapter

## Core Idea
Make objects with incompatible interfaces collaborate. The adapter implements the interface one side expects and translates calls into the format/shape the wrapped service expects. A.k.a. **Wrapper**.

## Frameworks Introduced
- **Adapter (Wrapper)** — structural pattern; two flavors:
  - **Object adapter** (composition, works in any language): adapter implements the client interface and holds a reference to the service, translating calls.
  - **Class adapter** (multiple inheritance, e.g. C++): adapter inherits from both client and service; adaptation happens in overridden methods.
  - When to use: you want to use an existing class whose interface doesn't match your code; or you want to reuse subclasses that lack a common feature.
  - How: declare a client interface; create the adapter implementing it and wrapping the service; delegate real work to the service, doing only format/interface conversion.

## Key Concepts
- **Client**: existing business logic that expects a specific interface.
- **Client Interface**: protocol collaborators must follow.
- **Service**: useful class (often 3rd-party/legacy) with an incompatible interface.
- **Adapter**: implements the client interface, holds the service, translates.
- **Two-way adapter**: converts calls in both directions.
- **Adapter vs. Decorator vs. Proxy vs. Facade** (the book's key distinctions): Adapter = *different* interface to one object; Decorator = *same-or-extended* interface, recursive composition; Proxy = *same* interface with control; Facade = *new* interface to a whole subsystem (usually multiple objects).

## Mental Models
- Real-world analogy: a US→EU power-plug adapter. You can't modify the wall socket or the plug; the adapter presents the right shape to each side.
- The wrapped service is unaware of the adapter; the client is unaware of the service's real interface — only the adapter bridges them.

## Anti-patterns
- **Modifying the 3rd-party/legacy class to fit your interface**: risks breaking its existing dependents and may be impossible (no source).
- **Using Adapter when a direct interface change is cheap**: the book concedes "sometimes it's simpler just to change the service class."
- **Confusing Adapter with Decorator**: Adapter changes the interface; Decorator preserves/enhances it and supports recursive wrapping — Adapter does not.

## Code Examples
Square pegs → round holes (the classic):
```pseudo
class RoundHole is
  method fits(peg: RoundPeg) is  return this.getRadius() >= peg.getRadius()

class RoundPeg is
  method getRadius() is  // ...

class SquarePeg is          // incompatible — no getRadius()
  method getWidth() is  // ...

class SquarePegAdapter extends RoundPeg is
  private field peg: SquarePeg
  constructor SquarePegAdapter(peg) is  this.peg = peg
  method getRadius() is       // pretend to be round
    return peg.getWidth() * Math.sqrt(2) / 2

// client
hole = new RoundHole(5)
hole.fits(new RoundPeg(5))                     // true
hole.fits(new SquarePegAdapter(new SquarePeg(5)))  // true
hole.fits(new SquarePegAdapter(new SquarePeg(10))) // false
```
- **What it demonstrates**: the adapter derives the "radius" the client wants from the square peg's width, letting incompatible types interoperate without modifying either.

## Reference Tables
Adapter vs. its look-alikes (the book's comparison):

| Pattern | Interface vs. original | Wraps | Recursive? |
|---|---|---|---|
| Adapter | *different* | one object | no |
| Decorator | same / extended | one object | yes |
| Proxy | same | one object | no |
| Facade | *new* (simplified) | whole subsystem | no |

Object adapter structure recap: Client → Client Interface ← Adapter → Service.

## Worked Example
Stock-market app produces XML; a 3rd-party analytics library wants JSON. Instead of editing the library (no source, would break its clients), build `XMLToJSONAnalyticsAdapter` for each library class the app calls directly. The adapter implements the app's XML-facing interface, internally converts the XML payload to JSON, and forwards to the wrapped analytics object. App code now talks only to adapters — swap the analytics library later by writing new adapters, no client code touched (OCP).

## Key Takeaways
1. Adapter = a translator object between two incompatible interfaces; usually wraps one object.
2. Prefer the object-adapter form (composition) — portable to any language; class adapter needs multiple inheritance.
3. Put only interface/data conversion in the adapter; delegate the real work to the service.
4. Clients depend on the adapter via the client interface, so new adapters don't break them (OCP).
5. Adapter gives a *different* interface — that's what separates it from Decorator (same+), Proxy (same), and Facade (new, whole subsystem).

## Connects To
- **ch11 Bridge**: Bridge is designed up-front for two independent hierarchies; Adapter retrofits incompatible existing classes.
- **ch13 Decorator / ch16 Proxy / ch14 Facade**: the structural "look-alikes" — distinguished by what they do to the interface (see table).
- **ch11 Bridge, ch23 State, ch24 Strategy**: same composition shape, different intent — a pattern encodes intent, not just structure.