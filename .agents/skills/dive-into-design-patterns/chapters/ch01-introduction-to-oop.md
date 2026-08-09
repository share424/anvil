# Chapter 1: Introduction to OOP

## Core Idea
Object-oriented programming wraps data and the behavior that acts on it into **objects** built from **classes**. Mastering OOP means understanding the four pillars (abstraction, encapsulation, inheritance, polymorphism) and the spectrum of **relations** between objects — from the weakest (dependency) to the strongest (inheritance).

## Frameworks Introduced
- **Four Pillars of OOP**: Abstraction, Encapsulation, Inheritance, Polymorphism — the concepts that distinguish OOP from other paradigms.
  - When to use: whenever you model a domain as interacting objects.
  - How: model real-world entities in a specific context (abstraction), hide internals behind an interface (encapsulation), reuse via superclasses (inheritance), let the runtime pick the right overriding method (polymorphism).
- **Relations Between Objects**: a six-rung ladder from weakest to strongest — Dependency → Association → Aggregation → Composition → Implementation → Inheritance.
  - When to use: to communicate design intent in UML and to judge how tightly two classes are coupled.
  - How: pick the weakest relation that satisfies the requirement; promote to a stronger one only when the stronger guarantee is needed.

## Key Concepts
- **Class / Object**: a class is a blueprint; an object is a concrete instance. Fields hold state, methods define behavior; together they are the class's *members*.
- **Superclass / Subclass**: a subclass inherits and may override state and behavior from its superclass.
- **Abstraction**: a model of a real-world object limited to a specific context, representing relevant details and omitting the rest.
- **Encapsulation**: hiding state/behavior; expose only a limited **interface** (`private`, `protected`).
- **Interface (type)**: a contract of behavior — methods with no implementation; lets a class restrict collaborators to "anything that fulfills this contract."
- **Inheritance**: building new classes on existing ones for code reuse; subclass gets the superclass's interface (can't shrink it).
- **Polymorphism**: the runtime detecting an object's real class and calling its overriding implementation even when the static type is the superclass/interface.
- **Dependency**: one class breaks if another changes (weakest).
- **Association**: one object *knows* another, usually via a field or a returning method.
- **Aggregation**: a "has-a" / whole-part relation where the part can outlive the whole (empty diamond).
- **Composition**: a stronger aggregation where the part exists only as part of the container; the container manages the part's lifecycle (filled diamond).

## Mental Models
- Think of an object's **interface** like a car's dashboard: a few controls hiding the engine underneath. Program other objects to the controls, not the crankshaft.
- Use polymorphism as "animals in a bag": you don't know the concrete type, but calling `makeSound()` gets the right meow or woof.
- Order relations weakest→strongest to decide coupling: prefer Dependency and Association over Composition; prefer Composition/Aggregation over Inheritance (previews ch03).

## Anti-patterns
- **Modeling a real object with 100% fidelity**: an `Airplane` for a flight simulator and for a booking app share a name but almost nothing else — over-modeling couples you to irrelevant details.
- **Strengthening relations unnecessarily**: using inheritance where association/aggregation would do creates tight coupling and a combinatorial-explosion risk (see ch03).
- **Polluting UML with every dependency**: dependencies are everywhere; show only the ones that matter to what you're communicating.

## Worked Example
Polymorphism with a bag of animals (from the book):

```
1  bag = [new Cat(), new Dog()];
3  foreach (Animal a : bag)
4    a.makeSound()
6  // Meow!
7  // Woof!
```

The loop holds `Animal` references, but the runtime dispatches to the concrete subclass's `makeSound`. This is polymorphism: call without knowing the real type.

Relations ladder, weakest → strongest:

| Relation | Object A… | Class A… |
|---|---|---|
| Dependency | can be affected by changes in B | depends on B |
| Association | knows B | depends on B |
| Aggregation | knows B and *consists of* B | depends on B |
| Composition | knows B, consists of B, **manages B's lifecycle** | depends on B |
| Implementation | defines B's interface methods; A can be treated as B | depends on B |
| Inheritance | gets B's interface+impl, may extend; A can be treated as B | depends on B |

## Key Takeaways
1. A class is a blueprint; an object is an instance. Fields = state, methods = behavior.
2. The four pillars — abstraction, encapsulation, inheritance, polymorphism — are what make OOP *OOP*.
3. Encapsulate by making members `private`/`protected`; expose a minimal interface.
4. Inheritance reuses code but forces the subclass to accept the parent's full interface — it can't shrink it.
5. Polymorphism lets code call `a.method()` and get the right subclass behavior without knowing the concrete type.
6. There are six relation types, ordered weakest→strongest; pick the weakest that works.

## Connects To
- **Ch 3**: "Favor Composition Over Inheritance" turns the relations ladder into a design rule.
- **Ch 2**: patterns are applied OOP — the pillars and relations are the vocabulary every pattern builds on.