# Chapter 13: Decorator

## Core Idea
Attach new behavior to an object at runtime by wrapping it in a "decorator" that implements the same interface, delegates to the wrapped object, and adds its own behavior before/after. Stack multiple wrappers to combine behaviors — no inheritance, no combinatorial explosion. A.k.a. **Wrapper**.

## Frameworks Introduced
- **Decorator (Wrapper)** — structural pattern.
  - When to use: you need to add behavior to objects at runtime without breaking clients; inheritance is awkward or impossible (e.g. `final` class, behavior varies in multiple combinations).
  - How: define a Component interface; Concrete Component = base behavior; Base Decorator implements the interface and holds a `wrappee: Component`; Concrete Decorators extend the base, run added work before/after delegating to `wrappee`; client composes the stack.

## Key Concepts
- **Wrapper**: same interface as the wrapped object; client can't tell decorated from pure.
- **Base Decorator**: has a component-typed field; delegates everything to the wrappee.
- **Concrete Decorator**: overrides a method and adds behavior before/after calling `super`/`wrappee`.
- **Recursive composition**: a decorator can wrap another decorator, building a stack (e.g. `Encryption > Compression > FileDataSource`).
- **Aggregation/Composition over Inheritance**: the principle Decorator embodies — delegation replaces subclassing so behavior is runtime-swappable and multi-source.
- **Inheritance is static**: you can't change an existing object's behavior via inheritance; decorators can wrap *and* be removed at runtime.

## Mental Models
- Real-world analogy: wearing clothes. Cold → add a sweater; still cold → add a jacket; raining → add a raincoat. Each garment extends you, isn't part of you, and can be taken off independently.
- Decorator changes the **skin** of an object; Strategy changes its **guts** (book's distinction).
- Proxy has the same structure but different intent — Proxy manages its service's lifecycle itself; Decorator's composition is controlled by the client.

## Anti-patterns
- **Subclass per behavior combination**: `SMSNotifier`, `FacebookNotifier`, `SMSFacebookNotifier`, `SlackFacebookNotifier`… — combinatorial explosion of subclasses polluting both library and client code.
- **Adding behavior by editing the base class every time**: bloats the class and forces every client to carry unneeded features.
- **Decorators that break the request flow or depend on stack order**: documented cons — hard to remove a middle wrapper and hard to make behavior order-independent.

## Code Examples
Encryption + compression decorators stacked over a file data source:
```pseudo
interface DataSource is
  method writeData(data)
  method readData():data

class FileDataSource implements DataSource is
  method writeData(data) is  // write to file
  method readData():data is  // read from file

class DataSourceDecorator implements DataSource is
  protected field wrappee: DataSource
  constructor DataSourceDecorator(source) is  wrappee = source
  method writeData(data) is  wrappee.writeData(data)
  method readData():data is  return wrappee.readData()

class EncryptionDecorator extends DataSourceDecorator is
  method writeData(data) is  // encrypt, then  wrappee.writeData(encrypted)
  method readData():data is  //  d = wrappee.readData(); decrypt; return

class CompressionDecorator extends DataSourceDecorator is
  method writeData(data) is  // compress, then  wrappee.writeData(compressed)
  method readData():data is  //  d = wrappee.readData(); decompress; return

// client assembles the stack at runtime
source = new FileDataSource("salary.dat")
if (enabledEncryption)    source = new EncryptionDecorator(source)
if (enabledCompression)  source = new CompressionDecorator(source)
// SalaryManager just sees a DataSource — pure or decorated, identical
```
- **What it demonstrates**: `SalaryManager` is unaware whether it uses a pure file source or an Encryption>Compression>File stack; behavior (encrypt, compress) is layered at runtime via configuration.

## Reference Tables
Decorator vs. its near-relatives (the book's framing):

| Pattern | Interface vs. original | Wraps | Recursive? | Lifecycle control |
|---|---|---|---|---|
| **Decorator** | same / enhanced | the target | yes (stacks) | client controls |
| Adapter | *different* | the service | no | — |
| Proxy | same | the service | no | proxy manages service lifecycle |
| Composite | same | many children | yes | — |

Implementation steps:
1. Identify a primary component plus optional layers.
2. Declare their common methods as a Component interface.
3. Concrete Component = base behavior.
4. Base Decorator holds a `Component wrappee` and delegates everything.
5. Concrete Decorators add behavior before/after delegating.

## Worked Example
Notifier library: a base `Notifier` sends emails. Instead of `SMSNotifier`/`FacebookNotifier`/`SMSFacebookNotifier` subclasses, make SMS and Facebook *decorators* implementing the same `Notifier` interface. The client builds the stack: `notifier = new SlackNotifier(new SMSNotifier(new FacebookNotifier(baseNotifier)))`. When `send(msg)` is called, each decorator does its send then delegates inward, so a single call reaches email, Facebook, SMS, and Slack — combining channels without a single subclass per combination. Channels can be added/removed by editing one wiring line.

## Key Takeaways
1. Decorator wraps an object in a same-interface object delegating + adding behavior; clients can't tell wrapped from pure.
2. Replace "behavior combinations via subclasses" with composable runtime wrappers — no explosion.
3. Stacks are recursive: a decorator can wrap a decorator.
4. Use it when inheritance is impossible (`final`) or just too rigid (static, single-parent).
5. Cons: removing a middle wrapper is hard; behavior may be order-dependent; wiring code looks ugly.
6. Decorator = skin (external behavior), Strategy = guts (internal algorithm); Decorator vs. Proxy = same structure, different intent + lifecycle ownership.

## Connects To
- **ch10 Adapter**: Adapter changes the interface; Decorator preserves/enhances it and is recursive.
- **ch12 Composite**: structural twins — Decorator has one child and adds behavior; Composite has many and sums results.
- **ch16 Proxy**: same structure, but Proxy self-manages the service; Decorator composition is client-driven.
- **ch08 Prototype**: clone heavy Composite/Decorator graphs instead of rebuilding.
- **ch24 Strategy**: "Decorator changes skin, Strategy changes guts."
- **ch17 Chain of Responsibility**: similar recursive structure, but CoR handlers may stop the flow; decorators may not.