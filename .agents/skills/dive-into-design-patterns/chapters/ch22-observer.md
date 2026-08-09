# Chapter 22: Observer

## Core Idea
Define a subscription mechanism so a **publisher** (subject) notifies a dynamic list of **subscribers** whenever its state changes. Subscribers implement one notification interface; the publisher never knows their concrete classes, so observers can join/leave at runtime. A.k.a. **Event-Subscriber, Listener**.

## Frameworks Introduced
- **Observer (Event-Subscriber, Listener)** — behavioral pattern.
  - When to use: one object's state change must update others, and the set of "others" is unknown or changes dynamically; objects must observe others only for limited time/specific cases.
  - How: add a subscription array + `subscribe`/`unsubscribe` to the publisher; declare a Subscriber interface with a single `update(...)`; on an event the publisher iterates subscribers calling `update`; publishers may expose a publisher interface so subscribers aren't coupled to concrete publisher classes.

## Key Concepts
- **Publisher (Subject)**: emits events on state change/behavior; maintains the subscription list and the notify loop. Often delegates this to a dedicated `EventManager`/dispatcher object (composition) when it can't inherit it.
- **Subscriber interface**: usually a single `update(context)` method; the publisher may pass itself so subscribers can pull details directly.
- **Concrete Subscriber**: reacts to `update`; the publisher is coupled only to the interface.
- **Subscription by event type**: a hash map of `eventType → [listeners]` lets one publisher fan out many event kinds.
- **Random notification order**: documented con — subscribers aren't told in a defined order.
- **OCP both ways**: with a publisher interface, new subscriber *and* new publisher classes don't break the other side.

## Mental Models
- Real-world analogy: a magazine subscription — you don't visit the store daily to ask "is the new issue out?"; the publisher ships it when it's ready, and you leave the list whenever you stop caring.
- Replaces "customer polls the store every day" (wasted work) and "store emails every customer regardless of interest" (spam) with *opt-in* push notifications.

## Anti-patterns
- **Polling the subject from every interested object**: wasted CPU; and the store either spams everyone or the customer runs endless trips.
- **Publisher coupled to concrete subscriber classes**: can't add subscribers later / unknown third-party subscribers; force one subscriber interface.
- **Permanent publisher↔subscriber wiring via constructor**: kills the "observe for a limited time" benefit — prefer dynamic subscribe/unsubscribe.
- **Relying on notification order**: it's randomized — don't.

## Code Examples
Editor as publisher with a delegated `EventManager`; logging + email subscribers:
```pseudo
class EventManager is                          // subscription infrastructure
  private field listeners: hash map of event types and listeners
  method subscribe(eventType, listener) is   listeners.add(eventType, listener)
  method unsubscribe(eventType, listener) is listeners.remove(eventType, listener)
  method notify(eventType, data) is
    foreach (listener in listeners.of(eventType)) do  listener.update(data)

class Editor is                                // concrete publisher
  public field events: EventManager
  private field file: File
  constructor Editor() is  events = new EventManager()
  method openFile(path) is  this.file = new File(path);  events.notify("open", file.name)
  method saveFile() is      file.write();                 events.notify("save", file.name)

interface EventListener is  method update(filename)

class LoggingListener implements EventListener is
  private field log: File; message: string
  method update(filename) is  log.write(replace('%s', filename, message))

class EmailAlertsListener implements EventListener is
  private field email, message: string
  method update(filename) is  system.email(email, replace('%s', filename, message))

// client wires subscribers at runtime
editor.events.subscribe("open", new LoggingListener("/path/to/log.txt", "Opened: %s"))
editor.events.subscribe("save", new EmailAlertsListener("admin@example.com", "Changed: %s"))
```
- **What it demonstrates**: `Editor` knows nothing about logging or email — it just fires "open"/"save" through the `EventManager`; new listeners (or removed ones) need no publisher change.

## Reference Tables
| Role | Responsibility |
|---|---|
| Publisher (Subject) | emit events; manage subscribe/unsubscribe; notify loop |
| Subscriber interface | single `update(context)` |
| Concrete Subscriber | reacts to the event; implements the one interface |
| Client | creates publishers + subscribers and wires them at runtime |

The four behavioral connectors (with ch17/18/20):

| Pattern | Link style |
|---|---|
| Chain of Responsibility | sequential dynamic chain |
| Command | fixed unidirectional link |
| Mediator | indirect, via central mediator |
| **Observer** | dynamic, opt-in pub/sub |

Observer vs. Mediator (the book's blurred line):

| | Mediator | Observer |
|---|---|---|
| Goal | eliminate mutual deps → depend on one mediator | dynamic one-way publisher→subscriber |
| Central object? | yes (the mediator) | optional; can be fully distributed |
| Implementation overlap | often implemented *with* Observer (mediator = publisher, components = subscribers) | — |

## Worked Example
A store launches a new iPhone; customers either poll daily (wasted trips) or the store emails everyone (spam). Observer: the `Store` is a publisher with a subscribers list; each `Customer` calls `store.subscribe(this)` to register interest, and `store.notify(...)` calls each `Customer.update(product)` only when the product drops. A customer wanting no more alerts calls `unsubscribe`. Different customer types (email, SMS, push) implement the same `update` interface — the store is blind to their concrete classes and adds them later without edits (OCP).

## Key Takeaways
1. A publisher keeps a list of subscribers and calls their `update` on state change — dynamic subscribe/unsubscribe at runtime.
2. Subscribers share one notification interface, so the publisher stays decoupled (and extensible).
3. Decouple both directions with a publisher interface too: new subscribers and new publishers don't break each other.
4. Subscription logic can be inherited or composed into a dedicated `EventManager` (useful when the publisher can't inherit it).
5. The notification order isn't defined — never depend on it.
6. Observer is the substratum of many Mediator implementations; both are valid choices for "who-talks-to-whom," differing in whether a central object exists.

## Connects To
- **ch17/18/20**: the four sender→receiver connectors; Observer is the dynamic subscribe/unsubscribe one.
- **ch20 Mediator**: overlapping intent — Mediator often uses Observer internally (mediator = publisher, components = subscribers); the difference is a central mediator object vs. a distributed set of observers.