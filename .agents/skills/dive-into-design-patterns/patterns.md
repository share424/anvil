# Patterns — Dive Into Design Patterns

All 22 catalog patterns, grouped by family, with when/how/trade-offs. Principles and SOLID are covered in chapters 3–4.

## Creational — how objects get made

### Factory Method (Virtual Constructor) — ch05
**When to use**: don't know product types ahead; give framework users an extension point; reuse/pool objects.
**How**: Creator declares an abstract `createX()` returning the Product interface; Concrete Creators override to return their product; clients depend on the abstractions.
**Trade-offs**: + decouples creator from concrete products (OCP, SRP); − many new subclasses.

### Abstract Factory (Kit) — ch06
**When to use**: produce families of related, mutually-compatible products across variants.
**How**: per-type Abstract Product interfaces; an Abstract Factory interface with one creation method per type; one Concrete Factory per variant.
**Trade-offs**: + guaranteed consistency + OCP for new variants; − adding a product *type* touches every factory.

### Builder — ch07
**When to use**: kill a telescoping constructor; produce different representations sharing steps; assemble Composite trees.
**How**: Builder interface of steps; Concrete Builder per representation; optional Director for step order; fetch product from the builder.
**Trade-offs**: + step-by-step, reusable code across representations (SRP); − extra classes; best for genuinely complex products.

### Prototype (Clone) — ch08
**When to use**: copy objects without coupling to their classes; replace "init-only" subclasses with pre-built prototypes.
**How**: Prototype interface with `clone()`; each class implements a prototype constructor copying fields (call parent's); optional Prototype Registry.
**Trade-offs**: + no concrete-class coupling; alternative to inheritance; − circular references are tricky; needs clone init.

### Singleton — ch09
**When to use**: exactly one instance shared across clients; safer than a bare global variable.
**How**: private static instance; private constructor; `getInstance()` lazy-init (double-checked locking) returning the cached instance.
**Trade-offs**: + guaranteed single instance + global access (lazy); − SRP violation; thread-safety burden; hard to mock.

## Structural — how objects/classes compose

### Adapter (Wrapper) — ch10
**When to use**: reuse a class whose interface doesn't fit your code (often 3rd-party/legacy).
**How**: adapter implements the client interface and wraps the service, translating calls. Object form (composition) is universal; class form needs multiple inheritance.
**Trade-offs**: + isolates conversion (SRP, OCP for new adapters); − sometimes just changing the service class is simpler; no recursive composition.

### Bridge — ch11
**When to use**: a class varies in two independent dimensions; switch implementations at runtime.
**How**: split into Abstraction + Implementation hierarchies; the abstraction holds an implementation reference and delegates.
**Trade-offs**: + N+M classes instead of N×M (OCP both ways); − needless split if the class is cohesive.

### Composite (Object Tree) — ch12
**When to use**: your model is a tree; treat leaves and containers uniformly.
**How**: Component interface; Leaf does the work; Container delegates+aggregates recursively; client talks only to Component.
**Trade-offs**: + uniform, OCP for new element types; − over-generalizing the interface can be hard to read; add/remove-on-interface trades ISP for uniformity.

### Decorator (Wrapper) — ch13
**When to use**: add behavior at runtime; inheritance is impossible/awkward (`final`, multi-dimension combinations).
**How**: Component interface; Base Decorator holds a `Component wrappee` and delegates; Concrete Decorators add behavior before/after delegating; stack recursively.
**Trade-offs**: + composable runtime behavior (SRP, OCP); − removing a middle wrapper / order-dependence is painful; wiring looks ugly.

### Facade — ch14
**When to use**: give a complex subsystem a simplified entry point; structure a subsystem into layers.
**How**: facade delegates to the right subsystem objects in the right order; clients talk only to the facade; split into Additional Facades before bloat.
**Trade-offs**: + isolates clients from churn; − can turn into a god object.

### Flyweight (Cache) — ch15
**When to use**: huge numbers of similar objects exhausting RAM, with extractable duplicate state.
**How**: split intrinsic (immutable, shared, in flyweight) vs extrinsic (per-instance, passed in); Flyweight Factory pools by intrinsic state; Context pairs extrinsic state + a flyweight ref.
**Trade-offs**: + RAM saved; − trades CPU (recompute/pass context) and code clarity; only after a measured RAM problem.

### Proxy — ch16
**When to use**: lazy/protection/remote/logging/caching/smart-reference control around a service.
**How**: a same-interface substitute wraps the service, does its own work before/after delegating, and usually owns the service's lifecycle.
**Trade-offs**: + clients unchanged (OCP for new proxies); − more classes; possible delay.

## Behavioral — communication & responsibility

### Chain of Responsibility (CoR, Chain of Command) — ch17
**When to use**: process varied requests in a given order; handlers/order change at runtime.
**How**: Handler interface; optional Base Handler with `next` + default forward; Concrete Handlers decide to process and/or pass on; clients build the chain.
**Trade-offs**: + decouples sender from receivers (OCP, SRP); − some requests end unhandled.

### Command (Action, Transaction) — ch18
**When to use**: parameterize with operations; queue/schedule/remote-execute; implement undo/redo.
**How**: Command interface (`execute`, optional `undo`); Concrete Command holds receiver + args; Sender triggers; history stack for undo.
**Trade-offs**: + decoupling, undo, deferred execution, composable macros (SRP, OCP); − an extra layer; snapshot undo needs Memento and is RAM-heavy.

### Iterator — ch19
**When to use**: hide collection internals; cut traversal duplication; traverse varied/unknown structures.
**How**: Iterator interface (`getNext`/`hasMore`); Collection interface returning the iterator; Concrete Iterator owns its position.
**Trade-offs**: + uniform traversal, parallel/independent iteration, OCP for new iterators (SRP); − overkill/slower for simple collections.

### Mediator (Intermediary, Controller) — ch20
**When to use**: classes are tightly coupled to many others; reuse is blocked by coupling.
**How**: Mediator interface (`notify`); Concrete Mediator holds all components and the rules; components notify only the mediator.
**Trade-offs**: + components reusable/decoupled (OCP for new mediators); − the mediator can become a God Object.

### Memento (Snapshot) — ch21
**When to use**: save/restore state (undo, transaction rollback) without breaking encapsulation.
**How**: Originator creates immutable Memento and restores from it; Caretaker stores snapshots (metadata-only access); nested-class / interface / linked-memento access strategies.
**Trade-offs**: + encapsulation-safe snapshots; − RAM growth; caretakers track originator lifecycle; dynamic languages can't enforce immutability.

### Observer (Event-Subscriber, Listener) — ch22
**When to use**: one object's change must update a dynamic, unknown set of others; observe for limited time.
**How**: Publisher keeps a subscriber list + `subscribe`/`unsubscribe`; Subscriber interface (`update`); publisher iterates and calls `update`; often delegates infra to an `EventManager`.
**Trade-offs**: + OCP both ways, runtime relations; − random notification order.

### State — ch23
**When to use**: FSM with many states whose code changes often; class polluted with state `switch`es.
**How**: State interface of state methods; Context holds the current state and delegates; Concrete States implement behavior and may transition the context via a back-reference.
**Trade-offs**: + kills giant `switch`es (SRP, OCP for new states); − overkill for tiny stable FSMs.

### Strategy (Policy) — ch24
**When to use**: swap algorithm variants at runtime; isolate algorithm internals; replace a giant variant-conditional.
**How**: Strategy interface (one method); Concrete Strategy per variant; Context holds a strategy + setter and delegates; client chooses.
**Trade-offs**: + runtime swap, OCP for new strategies, composition over inheritance; − pointless for a couple of stable algorithms; client must understand strategies; lambdas may suffice.

### Template Method — ch25
**When to use**: let subclasses extend only certain steps; several classes share an algorithm skeleton with minor differences.
**How**: base class's template method (often `final`) calls abstract/optional/hook steps; subclasses override steps, not the skeleton.
**Trade-offs**: + partial extension + hoisted duplication; − skeleton constrains clients; LSP risk if you suppress defaults; harder with many steps.

### Visitor — ch26
**When to use**: run an operation over a complex structure; extract auxiliary behaviors; behavior applies to only some classes.
**How**: Visitor interface with a `visitXxx` per concrete element; Element `accept(v)` calls `v.visitXxx(this)` (double dispatch); Concrete Visitor = one behavior per type.
**Trade-offs**: + new behaviors without touching elements (OCP/SRP), accumulates state over a traversal; − adding an element class edits every visitor; may need private-field access.