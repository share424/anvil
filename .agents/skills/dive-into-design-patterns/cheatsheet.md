# Cheatsheet — Dive Into Design Patterns

Decision rules for picking and applying patterns. Every line helps you *decide* something.

## Pick the family by what's wrong
| Your problem is about… | Family |
|---|---|
| *how objects get made* | Creational |
| *how objects/classes compose* | Structural |
| *how objects talk & divide work* | Behavioral |

## Creational — pick the right one
| Situation | Pattern |
|---|---|
| Subclasses should choose the product; one factory method | **Factory Method** |
| Families of products that must stay consistent per variant | **Abstract Factory** |
| Complex object, many optional steps / representations | **Builder** |
| Clone existing objects without knowing their class; config presets | **Prototype** |
| Exactly one instance + global access | **Singleton** |
| These factories/builders/prototypes themselves should be single | implement any as **Singleton** |

> Evolve rule: start with Factory Method → grow to Abstract Factory / Prototype / Builder when flexibility demands it.

## Structural — pick the right one (and don't confuse them)
| You want to… | Pattern | Interface vs. original |
|---|---|---|
| Make an incompatible interface usable (one object) | **Adapter** | different |
| Split two independent dimensions / swap platform at runtime | **Bridge** | (two hierarchies) |
| Treat a tree's leaves and containers uniformly | **Composite** | same |
| Add behavior by stacking runtime wrappers | **Decorator** | same / enhanced |
| Give a complex subsystem one simple entry point | **Facade** | new (simplified) |
| Share intrinsic state across many objects to save RAM | **Flyweight** | (optimization) |
| Control access (lazy/protect/remote/log/cache) to one service | **Proxy** | same — interchangeable |

> "Wrap one or many?" Adapter=**one different** | Decorator=**one enhanced** | Proxy=**one same** | Facade=**subsystem new** | Composite=**many uniform**.

## Behavioral — pick the right sender→receiver connector
| You want… | Pattern |
|---|---|
| Sequential, multi-step checks; handlers stop the chain | **Chain of Responsibility** |
| A request as an object — queue, defer, undo | **Command** |
| Traverse a collection without exposing its internals | **Iterator** |
| Kill direct component↔component coupling, route via one object | **Mediator** |
| Save/restore private state (undo, rollback) safely | **Memento** |
| Dynamic opt-in event subscription | **Observer** |
| Finite-state machine: behavior per state, states transition | **State** |
| Swap one algorithm's interchangeable variants at runtime | **Strategy** |
| Fixed algorithm skeleton; override only steps | **Template Method** |
| Add a behavior across many element classes without editing them | **Visitor** |

## The look-alikes (same shape, different intent)
| Structural shape | When it's THIS one |
|---|---|
| composition + delegation | **Bridge** (decouple two hierarchies) vs **State** (FSM, states transition) vs **Strategy** (swap one algorithm) vs **Adapter** (retrofit incompatible) |
| recursive wrapping | **Decorator** (enhances, never breaks flow) vs **Chain of Responsibility** (handlers may stop / run arbitrary ops) vs **Composite** (Decorator=one child; Composite=many + sums) |
| same-interface substitute | **Proxy** (owns service lifecycle) vs **Decorator** (client composes the stack) |
| buffer a complex entity | **Facade** (different interface, subsystem) vs **Proxy** (same interface, one service) |
| centralize collaboration | **Mediator** (new behavior, components unaware of each other) vs **Facade** (no new behavior, subsystem unaware) |
| many vs. one object | **Flyweight** (many shared, immutable) vs **Singleton** (one, mutable vs. immutable flyweight) |

## Tell: which pattern the smell points at
| You see… | Reach for… |
|---|---|
| giant `switch(state)` per method | **State** |
| giant `if/switch` on algorithm variant | **Strategy** |
| subclass explosion in two dimensions | **Bridge** (or **Strategy**) |
| subclass explosion per behavior combination | **Decorator** |
| telescoping constructor | **Builder** |
| hard-coded `new ConcreteProduct()` everywhere | **Factory Method** |
| mismatched product variants mixing | **Abstract Factory** |
| private-state snapshots needed but encapsulation matters | **Memento** |
| one button/menu/shortcut need the same op; undo needed | **Command** |
| every class knows every other class | **Mediator** (or **Observer**) |
| RAM blown by millions of similar objects | **Flyweight** (after measuring) |
| closed/`final` class needs new behavior; same interface | **Decorator**; different interface → **Adapter** |
| can't edit production element classes but need new behavior | **Visitor** |
| `if (node instanceof X)` ladders in a traversal | **Visitor** (double dispatch) |

## "When X, do Y, because Z" rules
- **When you can change only some steps** → Template Method, because the skeleton stays frozen in the base class.
- **When behavior must change at runtime per object** → State/Strategy, not Template Method (Template is static, class-level).
- **When states must initiate transitions** → State, not Strategy (strategies don't know each other).
- **When you add behaviors often but element classes rarely** → Visitor; reverse — don't.
- **When you add product *types* often** → avoid Abstract Factory; when you add *variants* often → Abstract Factory.
- **When theSnapshot must include private fields** → Memento (originator makes it), never copy from outside.
- **When wiring one button to toolbar + menu + shortcut** → bind them all to one **Command** object, not subclasses per trigger.
- **When a class's deps are concrete classes** → insert an interface → that's the seed of Factory Method / DI / Strategy.
- **When you'd subclass for every configuration** → consider pre-built **Prototypes** to clone instead.

## SOLID quick guardrails (ch04)
| Principle | One-line check |
|---|---|
| SRP | one reason to change — split a class that has more |
| OCP | add features by extending/composing, not editing tested code |
| LSP | a subclass is a safe drop-in — use the substitutability checklist (params ≥ abstract, return ≤ concrete, no new exceptions, no stronger pre-conditions, no weaker post-conditions, invariants preserved, don't touch parent privates) |
| ISP | narrow interfaces — no implementer stubs methods it can't honor |
| DIP | depend on abstractions in business terms; invert the arrow so details depend on abstractions |

## Inheritance vs. composition — the recurring decision
- Default to **composition** unless you genuinely need the parent's full interface and a stable `is-a`.
- Two+ dimensions of variation? composition (Bridge/Strategy); single inheritance blows up N×M.
- "Decorator changes the **skin**; Strategy/State change the **guts**."

## Visibility / access conventions to remember
- Flyweights & Mementos: **immutable**.
- Singleton: **private constructor** + private static instance + `getInstance()`.
- Prototype: copy in a **prototype constructor**, `clone()` = one line `new MyClass(this)`, always `super(source)`.
- Visitor: elements know only the Visitor *interface*; visitors know **all concrete element classes**.

## Cost/benefit thresholds (don't over-engineer)
- < 3 rarely-changing states → keep the conditionals, skip State.
- 1–2 stable algorithms → skip Strategy (or use lambdas).
- Simple collection → skip Iterator.
- No measured RAM problem → skip Flyweight.
- Tiny program → don't apply all SOLID at once.