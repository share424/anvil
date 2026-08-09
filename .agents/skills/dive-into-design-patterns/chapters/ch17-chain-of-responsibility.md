# Chapter 17: Chain of Responsibility

## Core Idea
Turn a sequence of checks/handlers into stand-alone objects linked into a chain. Each handler receives a request, decides whether to process it and whether to pass it along, until one handles it or the chain ends. Decouples the sender of a request from its receivers and lets the chain be reconfigured at runtime. A.k.a. **CoR, Chain of Command**.

## Frameworks Introduced
- **Chain of Responsibility (CoR)** — behavioral pattern.
  - When to use: requests must be processed in varied, unknown-beforehand ways; handlers must run in a particular order; the handler set/ordering changes at runtime.
  - How: declare a Handler interface (usually one `handle(request)` method); an optional Base Handler holds the `next` reference + a default "forward to next" behavior; Concrete Handlers decide to process and/or forward; clients compose the chain (and may start it at any handler).

## Key Concepts
- **Handler**: interface common to all handlers.
- **Base Handler (optional)**: stores `next` reference; default behavior forwards to next if present.
- **Concrete Handler**: real processing; decides (1) whether to process, (2) whether to pass on.
- **Two execution models**: (a) each handler does its part then passes the request on (multi-handler processing — e.g. middleware auth → throttle → cache); (b) a handler that *can* process stops the chain (single-handler — classic GUI event bubbling).
- **Immutable handlers** that take setup via the constructor make chains composable; runtime reordering needs a setter.
- **Chain from an object tree**: a Composite's parent chain *is* a natural CoR (event bubbles up to containers).

## Mental Models
- Real-world analogy: calling tech support — auto-responder → operator → engineer; the call gets handed off until someone actually answers it.
- GUI F1 help: a click's help request starts at the focused component, bubbles through panels up to the dialog; the first element with help text displays it.

## Anti-patterns
- **Stuffing all sequential checks into one method**: changing one check breaks others; reuse across components forces copy-paste of partial checks — the mess CoR cleans up.
- **Handlers coupled to concrete successor types**: must only know the next handler via the interface, or chains can't be reconfigured.
- **Some requests end up unhandled**: a documented con — decide what the chain's end means (silent, default handler, error).

## Code Examples
Contextual help bubbling through a GUI component tree (Composite = CoR chain):
```pseudo
interface ComponentWithContextualHelp is  method showHelp()

abstract class Component implements ComponentWithContextualHelp is
  field tooltipText: string
  protected field container: Container
  method showHelp() is
    if (tooltipText != null)  // show tooltip
    else  container.showHelp()      // default: forward up the tree

abstract class Container extends Component is
  protected field children: array of Component
  method add(child) is  children.add(child); child.container = this

class Panel extends Container is
  field modalHelpText: string
  method showHelp() is
    if (modalHelpText != null)  // show modal window
    else  super.showHelp()

class Dialog extends Container is
  field wikiPageURL: string
  method showHelp() is
    if (wikiPageURL != null)  // open wiki page
    else  super.showHelp()

// client: pressing F1 sends help to the component under the cursor
component = this.getComponentAtMouseCoords()
component.showHelp()    // bubbles up until an element handles it
```
- **What it demonstrates**: the Composite parent chain doubles as the CoR — `showHelp()` falls up through containers until one has help text; no giant `if/else`, no coupling between the focused leaf and whichever ancestor can help.

## Reference Tables
CoR vs. its sibling behavioral connectors (the book's framing):

| Pattern | How sender→receiver connect |
|---|---|
| **Chain of Responsibility** | request travels sequentially along a dynamic chain; first willing handler stops it |
| Command | unidirectional, fixed sender→command→receiver link |
| Mediator | senders/receivers talk only via a mediator (no direct links) |
| Observer | receivers subscribe/unsubscribe dynamically to events |

Handler decision matrix:

| Can process? | Pass it on? |
|---|---|
| yes | multi-model: do, then forward; single-model: handle, then stop |
| no  | forward to next (base default) |

## Worked Example
Ordering-system middleware. Without CoR, a giant method does `authenticate → validate/sanitize → rate-limit (per-IP) → cache-check → handle` with tangled conditionals. With CoR, each becomes a handler: `Throttler.setNext(Authenticator).setNext(Validator).setNext(Cache).setNext(OrderHandler)`. A request walks the chain; `Throttler` can drop brute-force IPs and stop the chain; `Authenticator` can reject bad credentials and stop; otherwise the request advances to the real handler. To protect a different component you build a different chain reusing the same handler classes — no duplication, runtime-reorderable via setters.

## Key Takeaways
1. Decouple request senders from receivers by passing the request along a chain of handlers.
2. All handlers share one interface; each knows only "the next one."
3. A handler may process *and* forward, or process *and stop* — pick the model deliberately.
4. Chains are runtime-composable (constructors for immutability, setters for live reordering).
5. The chain can be a branch of a Composite object tree (parent pointers as next-links).
6. Cost: some requests may reach the end unhandled — handle that case explicitly.

## Connects To
- **ch18 Command / ch20 Mediator / ch22 Observer**: the four ways of connecting senders and receivers (see table).
- **ch12 Composite**: a Composite's parent line *is* a natural CoR; CoR is often used *with* Composite.
- **ch13 Decorator**: recursive-composition twins — but CoR handlers may stop the flow and run arbitrary ops; Decorator never breaks the flow and keeps the base interface.
- **ch18 Command**: CoR handlers can be Commands; or the request *itself* can be a Command object travelling the chain.