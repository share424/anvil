# Glossary — Dive Into Design Patterns

Terms are alphabetized. "(Ch N)" links to the chapter covering the term.

**Abstraction** (Ch 1) — a model of a real-world object limited to a specific context, representing relevant details and omitting the rest; also the high-level control layer in Bridge.
**Abstract Factory** (Ch 6) — creational pattern producing families of related objects (a variant) via a per-variant factory.
**Abstract Product** (Ch 6) — per-type interface every variant of a product family implements.
**AcquireThreadLock** (Ch 9) — the double-checked-locking guard used in thread-safe singletons.
**Adapter (Wrapper)** (Ch 10) — structural pattern that makes an incompatible interface usable by translating calls to a wrapped service.
**Additional Facade** (Ch 14) — a split-off facade to keep one facade from becoming a god object.
**Aggregation** (Ch 1) — "has-a"/whole-part relation where the part can outlive the whole (empty diamond).
**Applicability** (Ch 2) — the "when to use" section of a pattern description.
**Association** (Ch 1) — relation where one object uses/interacts with another via a field or returning method.
**Behavioral patterns** (Ch 2) — family concerned with communication and responsibility assignment between objects.
**Bridge** (Ch 11) — structural pattern splitting a class into two independent hierarchies (abstraction + implementation) to avoid combinatorial explosion.
**Builder** (Ch 7) — creational pattern constructing a complex object step-by-step; swaps builders for different representations.
**Caretaker** (Ch 21) — in Memento, the object that stores snapshots and triggers restoration but can't read the state.
**Chain of Responsibility (CoR, Chain of Command)** (Ch 17) — behavioral pattern passing a request along a handler chain until one handles it.
**Class adapter** (Ch 10) — adapter using multiple inheritance instead of composition.
**Client** ( generic) — the code that uses a pattern's participants via their interfaces.
**Command (Action, Transaction)** (Ch 18) — behavioral pattern turning a request into a stand-alone object (queue, undo, schedule).
**Component** (Ch 12/13/20) — the common interface/composite building block; in Mediator, a participant that notifies the mediator.
**Composite (Object Tree)** (Ch 12) — structural pattern treating leaves and containers uniformly through one interface.
**Composition** (Ch 1) — aggregation where the part exists only as part of the container (filled diamond).
**Concrete Creator/Factory/Builder/State/Strategy/Visitor/etc.** — a specific implementation of a pattern's abstract role.
**Context** (Ch 21/23/24) — the originator/state-holder/strategy-holder; the object whose behavior the pattern varies.
**Creational patterns** (Ch 2) — family concerned with object creation.
**Decorator (Wrapper)** (Ch 13) — structural pattern adding behavior by stacking same-interface wrappers delegating before/after.
**Dependency** (Ch 1) — weakest relation; one class breaks if another changes.
**Dependency Inversion** (Ch 4) — SOLID: depend on abstractions, not concretions.
**Dependency Inversion Principle (DIP)** (Ch 4) — high/low-level classes both depend on abstractions; abstractions don't depend on details.
**Director** (Ch 7) — in Builder, the optional class encoding the step order for reusable configurations.
**Double Dispatch** (Ch 26) — the two-stage call (`accept`→`visitXxx`) that lets Visitor route to the per-element-type method.
**Double-checked locking** (Ch 9) — the lock-then-re-check idiom for lazy thread-safe singleton init.
**Encapsulate What Varies** (Ch 3) — design principle: isolate the parts that change from those that stay stable.
**Encapsulation** (Ch 1/4) — hiding an object's state/behaviors behind a limited interface.
**Event-Subscriber / Listener** (Ch 22) — alternative names for Observer.
**Extrinsic state** (Ch 15) — per-instance context moved out of a flyweight and passed into its methods.
**Facade** (Ch 14) — structural pattern giving a simplified interface to a complex subsystem.
**Factory Method (Virtual Constructor)** (Ch 5) — creational pattern letting subclasses vary the product type via an overridable creation method.
**Favor Composition Over Inheritance** (Ch 3) — design principle preferring "has-a" delegation to "is-a" subclassing.
**Flyweight (Cache)** (Ch 15) — structural optimization sharing immutable intrinsic state across many objects.
**Flyweight Factory** (Ch 15) — pool of flyweights keyed by intrinsic state.
**Front-end / Back-end / Abstraction / Platform** (Ch 11) — the two Bridge dimensions.
**GoF book** (Ch 2) — *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides, 1994).
**God Object** (Ch 14/20) — the over-grown facade/mediator anti-pattern the patterns warn against.
**Handler** (Ch 17) — a link in the Chain of Responsibility.
**Hook** (Ch 25) — in Template Method, an empty optional step serving as an extension point.
**Implementation (Bridge)** (Ch 11) — the platform/low-level hierarchy a Bridge abstraction delegates to.
**Inheritance** (Ch 1) — building a class on an existing one for code reuse; subclass takes the parent's interface.
**Intrinsic state** (Ch 15) — constant shared data stored in a flyweight, immutable.
**Interface (public part)** (Ch 1) — the methods an object exposes; not the same as a language `interface` type.
**Interface Segregation Principle (ISP)** (Ch 4) — SOLID: break fat interfaces so clients aren't forced to depend on unused methods.
**Iterator** (Ch 19) — behavioral pattern extracting traversal into an object that owns its position.
**Liskov Substitution Principle (LSP)** (Ch 4) — SOLID: subclasses must be safe drop-ins for their parents; the substitutability checklist.
**Memento (Snapshot)** (Ch 21) — behavioral pattern saving/restoring state without breaking encapsulation.
**Mediator (Intermediary, Controller)** (Ch 20) — behavioral pattern centralizing component communication through one object.
**Object adapter** (Ch 10) — adapter using composition; portable to any language.
**Observer (Event-Subscriber, Listener)** (Ch 22) — behavioral pattern's dynamic pub/sub mechanism.
**Open/Closed Principle (OCP)** (Ch 4) — SOLID: open for extension, closed for modification.
**Originator** (Ch 21) — in Memento, the object that creates/restores its own snapshots.
**Pattern granularity** (Ch 2) — idioms → design patterns → architectural patterns.
**Polymorphism** (Ch 1) — the runtime calling the overriding subclass method even when the static type is the parent.
**Prototype (Clone)** (Ch 8) — creational pattern copying objects without coupling to their classes.
**Prototype Registry** (Ch 8) — name→prototype map of pre-built prototypes to clone from.
**Proxy** (Ch 16) — structural pattern controlling access via a same-interface substitute (lazy/protection/remote/logging/caching/smart-reference).
**Publisher (Subject)** (Ch 22) — in Observer, the object that maintains the subscriber list and notifies.
**Receiver** (Ch 18) — in Command, the business object that does the actual work.
**Relations Between Objects** (Ch 1) — the six-rung ladder Dependency→Association→Aggregation→Composition→Implementation→Inheritance.
**Sender (Invoker)** (Ch 18) — in Command, the object that triggers `execute()`.
**Singleton** (Ch 9) — creational pattern ensuring one instance with a global access point.
**Single Responsibility Principle (SRP)** (Ch 4) — SOLID: a class should have just one reason to change.
**SOLID** (Ch 4) — mnemonic for SRP, OCP, LSP, ISP, DIP (Robert Martin).
**State** (Ch 23) — behavioral pattern making an object's behavior follow a finite-state machine via per-state classes.
**Strategy (Policy)** (Ch 24) — behavioral pattern making a family of algorithms interchangeable through one interface.
**Structural patterns** (Ch 2) — family concerned with assembling objects/classes into larger structures.
**Subscriber** (Ch 22) — in Observer, an object implementing `update` and registered with a publisher.
**Template Method** (Ch 25) — behavioral pattern defining an algorithm skeleton in a base class; subclasses override steps, not the skeleton.
**Telescoping constructor** (Ch 7) — a monster constructor (or ladder of overloads) Builder replaces.
**Visitor** (Ch 26) — behavioral pattern separating algorithms from the object structure via double dispatch.
**Wrapper** (Ch 10/13) — nickname shared by Adapter (different interface) and Decorator (same/enhanced interface).