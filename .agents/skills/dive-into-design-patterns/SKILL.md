---
name: dive-into-design-patterns
description: "Knowledge base from \"Dive Into Design Patterns\" by Alexander Shvets (Refactoring.Guru). Use when applying design patterns for creational, structural, or behavioral problems, choosing between look-alike patterns (Adapter/Decorator/Proxy/Facade, Bridge/State/Strategy, Command/Memento/undo), or referencing a specific GoF pattern's intent, structure, applicability, and trade-offs."
---

<!-- argument-hint: [pattern name, topic, or chapter number] -->

# Dive Into Design Patterns
**Author**: Alexander Shvets (Refactoring.Guru, illus. Dmitry Zhart) | **Pages**: ~411 | **Chapters**: 26 | **Generated**: 2026-07-30

## How to Use This Skill

- **Without arguments** — load core frameworks and the decision rules below for reference.
- **With a pattern/topic** — ask about `Factory Method`, `undo`, `Flyweight`, or "what pattern for X"; I read the relevant chapter file and answer.
- **With a chapter** — ask for `ch11` (Bridge) to dive into a specific chapter.
- **Browse** — ask "what chapters do you have?" or "compare Facade and Proxy."

When you ask about a topic not covered in Core Frameworks, I read the relevant chapter file before answering. The cheatsheet (`cheatsheet.md`) is the fastest path from a *symptom* to a *pattern*.

---

## Core Frameworks & Mental Models

### The three intent families (ch02)
- **Creational** — *how objects get made* (Factory Method, Abstract Factory, Builder, Prototype, Singleton).
- **Structural** — *how objects/classes compose* (Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy).
- **Behavioral** — *how objects talk & divide work* (Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor).

### The bedrock principles (ch03–ch04)
- **Encapsulate What Varies** — isolate the parts that change; method-level first, then class-level.
- **Program to an Interface, Not an Implementation** — depend on abstractions to gain extension points.
- **Favor Composition Over Inheritance** — `has-a` over `is-a`; avoid the N×M subclass explosion.
- **SOLID** — SRP (one reason to change), OCP (extend, don't edit), LSP (substitutability checklist), ISP (narrow interfaces), DIP (depend on abstractions; invert the arrow).
> Apply these pragmatically — forcing all of SOLID everywhere over-engineers small programs.

### The recurring decision: inheritance vs. composition
Default to **composition** (Strategy/State/Bridge/Decorator) unless you need the parent's full interface and a real `is-a`. Two or more dimensions of variation ⇒ composition (Bridge/Strategy); single inheritance ⇒ N×M blow-up.
> "Decorator changes the **skin**; Strategy/State change the **guts**." Bridge/State/Strategy/Adapter share a composition shape but signal different *problems* — a pattern encodes intent, not just structure.

### Pick-by-symptom (see cheatsheet for the full table)
- giant `switch(state)` ⇒ **State**; giant `switch` on algorithm variant ⇒ **Strategy**.
- subclass explosion in two dimensions ⇒ **Bridge**; per behavior combination ⇒ **Decorator**.
- telescoping constructor ⇒ **Builder**; `new ConcreteProduct()` everywhere ⇒ **Factory Method**.
- mismatched product variants mixing ⇒ **Abstract Factory**; config presets ⇒ **Prototype**.
- one instance + global access ⇒ **Singleton**; RAM blown by millions of similar objects ⇒ **Flyweight**.
- closed/`final` class needs new behavior, same interface ⇒ **Decorator**; different interface ⇒ **Adapter**.
- can't edit production classes but need new behavior ⇒ **Visitor**; `instanceof` ladders in traversal ⇒ **Visitor**.
- every class knows every other ⇒ **Mediator** (or **Observer**); routing requests along handlers ⇒ **Chain of Responsibility**.
- request as object (queue/defer/undo) ⇒ **Command**; safe private-state snapshots ⇒ **Memento**.

### Look-alikes cheat (interface vs. original)
| Pattern | Interface | Wraps |
|---|---|---|
| Adapter | different | one object |
| Decorator | same / enhanced (recursive stacks, client-driven) | one object |
| Proxy | same (self-manages service lifecycle) | one object |
| Facade | new (simplified) | whole subsystem |
| Composite | same (uniform leaves+containers) | many children |
| Bridge | (two hierarchies) | an implementation ref |

| Connector | Link style |
|---|---|
| Chain of Responsibility | sequential dynamic chain, first-willing stops |
| Command | fixed unidirectional sender→command→receiver |
| Mediator | indirect, via central mediator (no direct links) |
| Observer | dynamic opt-in pub/sub |

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-introduction-to-oop.md) | Introduction to OOP | 4 pillars; relations ladder (Dependency→Inheritance) |
| [ch02](chapters/ch02-introduction-to-design-patterns.md) | Introduction to Design Patterns | pattern anatomy; 3 intent families; pattern granularity; GoF book |
| [ch03](chapters/ch03-design-principles.md) | Software Design Principles | Encapsulate What Varies; Program to an Interface; Favor Composition Over Inheritance |
| [ch04](chapters/ch04-solid-principles.md) | SOLID Principles | SRP, OCP, LSP (substitutability checklist), ISP, DIP |
| [ch05](chapters/ch05-factory-method.md) | Factory Method | Virtual Constructor; Creator/Concrete Creator; Product interface |
| [ch06](chapters/ch06-abstract-factory.md) | Abstract Factory | product families × variants; per-variant factory; consistency guarantee |
| [ch07](chapters/ch07-builder.md) | Builder | step-by-step; Concrete Builder; Director; telescoping constructor fix |
| [ch08](chapters/ch08-prototype.md) | Prototype | clone(); prototype constructor; Prototype Registry; deep-copy |
| [ch09](chapters/ch09-singleton.md) | Singleton | private ctor; getInstance(); lazy init; double-checked locking |
| [ch10](chapters/ch10-adapter.md) | Adapter (Wrapper) | object adapter (composition); class adapter (MI); translation |
| [ch11](chapters/ch11-bridge.md) | Bridge | abstraction + implementation; orthogonal dimensions; runtime swap |
| [ch12](chapters/ch12-composite.md) | Composite (Object Tree) | Component; Leaf; Container; uniform recursion |
| [ch13](chapters/ch13-decorator.md) | Decorator (Wrapper) | base decorator + wrappee; recursive stacking; skin vs guts |
| [ch14](chapters/ch14-facade.md) | Facade | simplified subsystem entry; Additional Facade; isolation |
| [ch15](chapters/ch15-flyweight.md) | Flyweight (Cache) | intrinsic/extrinsic state; immutability; Flyweight Factory; Context |
| [ch16](chapters/ch16-proxy.md) | Proxy | virtual/protection/remote/logging/caching/smart-reference; same interface |
| [ch17](chapters/ch17-chain-of-responsibility.md) | Chain of Responsibility (CoR) | handler + next; multi vs single-stop models; Composite parent chain |
| [ch18](chapters/ch18-command.md) | Command (Action, Transaction) | sender→command→receiver; execute/undo; history stack; composition of commands |
| [ch19](chapters/ch19-iterator.md) | Iterator | getNext/hasMore; per-iterator state; Collection interface; lazy fetch |
| [ch20](chapters/ch20-mediator.md) | Mediator (Intermediary) | components notify mediator only; eliminates N×N deps; God-object risk |
| [ch21](chapters/ch21-memento.md) | Memento (Snapshot) | originator/memento/caretaker; private-state snapshots; nested-class/interface/linked |
| [ch22](chapters/ch22-observer.md) | Observer (Event-Subscriber) | publisher/subscriber; subscribe/unsubscribe; EventManager; random order |
| [ch23](chapters/ch23-state.md) | State | FSM as state objects; context delegates; states self-transition vs Strategy |
| [ch24](chapters/ch24-strategy.md) | Strategy (Policy) | interchangeable algorithms; context + setter; client picks; runtime swap |
| [ch25](chapters/ch25-template-method.md) | Template Method | frozen skeleton; abstract/optional/hook steps; inheritance/static |
| [ch26](chapters/ch26-visitor.md) | Visitor | double dispatch (accept→visitXxx); behavior across many element classes; stable elements vs volatile behaviors |

## Topic Index

<!-- Alphabetical; term → chapters. -->
- **Abstract Factory** → ch06
- **Abstraction (Bridge)** → ch11
- **Access control (proxy)** → ch16
- **Adapter** → ch10
- **Aggregation** → ch01
- **Bridge** → ch11
- **Builder** → ch07
- **Caching proxy** → ch16
- **Chain of Responsibility** → ch17
- **Class relations** → ch01
- **Command** → ch18
- **Composition over inheritance** → ch03
- **Composite** → ch12
- **Creational patterns** → ch05, ch06, ch07, ch08, ch09
- **Decorator** → ch13
- **Dependency Inversion (DIP)** → ch04
- **Double dispatch** → ch26
- **Double-checked locking** → ch09
- **Encapsulate What Varies** → ch03
- **Encapsulation** → ch01, ch04
- **Extrinsic/intrinsic state** → ch15
- **Facade** → ch14
- **Factory Method** → ch05
- **Favor Composition Over Inheritance** → ch03
- **Finite-State Machine** → ch23
- **Flyweight** → ch15
- **GoF book** → ch02
- **Hook (Template Method)** → ch25
- **Inheritance** → ch01
- **Interface Segregation (ISP)** → ch04
- **Iterator** → ch19
- **Liskov Substitution (LSP)** → ch04
- **Mediator** → ch20
- **Memento** → ch21
- **Open/Closed (OCP)** → ch04
- **Observer** → ch22
- **OOP pillars** → ch01
- **Pattern anatomy/families/granularity** → ch02
- **Polymorphism** → ch01
- **Program to an Interface** → ch03
- **Prototype** → ch08
- **Proxy** → ch16
- **Pub/sub** → ch22
- **Relations between objects** → ch01
- **Repository/Registry (Prototype)** → ch08
- **Single Responsibility (SRP)** → ch04
- **Singleton** → ch09
- **SOLID** → ch04
- **State** → ch23
- **Strategy** → ch24
- **Structural patterns** → ch10, ch11, ch12, ch13, ch14, ch15, ch16
- **Telescoping constructor** → ch07
- **Template Method** → ch25
- **Undo/redo** → ch18, ch21
- **Visitor** → ch26

## Supporting Files

- [glossary.md](glossary.md) — every key term alphabetically, with chapter refs
- [patterns.md](patterns.md) — all 22 patterns: when / how / trade-offs
- [cheatsheet.md](cheatsheet.md) — decision rules, look-alike matrices, symptom→pattern table

---

## Scope & Limits

This skill covers the book's content only: 4 conceptual chapters and 22 GoF patterns. For hands-on implementation in *your* codebase, combine with project-specific tools. Many code snippets in the chapters are the book's pseudocode (extracted via a text fallback; tables/diagrams may be approximate) — adapt them to your language's idioms and your SOLID constraints.