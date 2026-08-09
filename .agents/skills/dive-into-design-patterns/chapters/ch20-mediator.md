# Chapter 20: Mediator

## Core Idea
Stop components from talking to each other directly; route all collaboration through a **mediator** object. Each component knows only the mediator; the mediator knows everyone and decides who acts on an event. Replaces an N×N web of dependencies with N+1 links. A.k.a. **Intermediary, Controller**.

## Frameworks Introduced
- **Mediator (Intermediary, Controller)** — behavioral pattern.
  - When to use: classes are tightly coupled to many others, making change/reuse hard; you keep subclassing components just to reuse basic behavior in new contexts.
  - How: declare a Mediator interface (usually one `notify(sender, event)`); Concrete Mediators hold references to all components and encode the collaboration rules; each Component stores a mediator reference and notifies it instead of calling colleagues.

## Key Concepts
- **Component**: business-logic class holding a mediator reference (typed as the Mediator interface, so the real mediator class is invisible — components stay reusable across mediators).
- **Mediator interface**: a single notification method; components pass context (even themselves) so the mediator can identify the sender without coupling components to each other.
- **Concrete Mediator**: owns the tangle of relationships, keeps references to all components, sometimes manages their lifecycle, decides what to trigger on each event.
- **Black-box collaboration**: the sender doesn't know who'll handle a request; the receiver doesn't know who sent it.
- **God-object risk**: the documented con — over time a mediator can absorb all the system's logic.

## Mental Models
- Real-world analogy: aircraft near an airport don't negotiate landing among themselves; everyone talks to the control tower, which sequences them. The tower only enforces order in the busy terminal area — it doesn't control whole flights.
- A checkbox "I have a dog" used to toggle a dog-name textbox directly — now it just notifies the dialog (mediator), which shows/hides the textbox; the checkbox is reusable in any other dialog with a different mediator.

## Anti-patterns
- **Components referencing each other directly**: a checkbox coupled to a dozen other form elements can't be reused without dragging them all along — the problem Mediator solves.
- **Subclassing components per context** to reuse basic behavior: instead, vary the mediator and keep the component class intact.
- **A monolithic mediator**: extracts collaboration and then grows unbounded into a God Object — split (e.g. an "authentication dialog mediator" vs. a "settings dialog mediator") and prefer the Observer-backed implementation when events multiply.

## Code Examples
Authentication dialog as mediator; components only notify it:
```pseudo
interface Mediator is
  method notify(sender: Component, event: string)

class AuthenticationDialog implements Mediator is
  private field loginOrRegisterChkBx: Checkbox
  private field loginUsername, loginPassword, registrationUsername, registrationPassword, registrationEmail: Textbox
  private field okBtn, cancelBtn: Button
  constructor AuthenticationDialog() is
    // create components, passing THIS as the mediator, to wire links

  method notify(sender, event) is
    if (sender == loginOrRegisterChkBx and event == "check")
      if (loginOrRegisterChkBx.checked)  title = "Log in";  // show login, hide registration
      else                                title = "Register"; // show registration, hide login
    if (sender == okBtn && event == "click")
      if (loginOrRegister.checked)  // validate & log in, else show error
      else                          // create account + log in

class Component is
  field dialog: Mediator
  constructor Component(dialog) is  this.dialog = dialog
  method click() is  dialog.notify(this, "click")
  method keypress() is  dialog.notify(this, "keypress")

class Checkbox extends Component is
  method check() is  dialog.notify(this, "check")
```
- **What it demonstrates**: no component references another component — every event becomes a `notify` to the dialog, which orchestrates show/hide/validate; the checkbox/buttons/textboxes reuse cleanly in a different dialog by swapping the mediator.

## Reference Tables
Mediator vs. Facade vs. Observer (the book's distinctions):

| Pattern | Relationship introduced | Subsystem aware? |
|---|---|---|
| **Mediator** | centralizes *new* communication; components know only the mediator | components unaware of each other |
| Facade | new *simplified* interface, no new behavior | subsystem objects talk directly; unaware of facade |
| Observer | dynamic one-way publish/subscribe | subscribe/unsubscribe at runtime |

Connector comparison (with ch17/18/22):

| Pattern | Link style |
|---|---|
| Chain of Responsibility | sequential, dynamic chain |
| Command | fixed unidirectional sender→command→receiver |
| **Mediator** | indirect, via central mediator (eliminates direct links) |
| Observer | dynamic subscribe/unsubscribe |

Mediator is often *implemented with* Observer: the mediator is the publisher, components subscribe to its events.

## Worked Example
A customer-profile dialog has a "I have a dog" checkbox, a dog-name textbox, username/password fields, and submit/cancel buttons. Direct coupling (the checkbox shows the textbox; the button validates every field) makes each element un-reusable. Mediator: the dialog itself implements `Mediator`; components receive the dialog in their ctor and call `dialog.notify(this, ...)` on any event. On a "check" from the checkbox the mediator flips title and shows/hides the relevant form half; on a "click" of OK it validates and logs in/registers. Each component depends only on the mediator interface — link the same `Checkbox`/`Button`/`Textbox` classes to an entirely different `SettingsDialog` mediator to reuse them.

## Key Takeaways
1. Replace an N×N dependency web with components that know only a single mediator.
2. Responding to events becomes the mediator's job, so components stay reusable and testable.
3. Components depend on the *mediator interface*, letting you swap mediators per context (OCP for collaboration).
4. The mediator mediates *new* behavior; Facade merely simplifies existing behavior without changing who-talks-to-whom.
5. Mediator is frequently implemented on top of Observer (mediator = publisher, components = subscribers) — same look, but you can equally wire permanent component→mediator links.
6. Con: a mediator can become a God Object — split by responsibility before that.

## Connects To
- **ch14 Facade**: similar job (organize coupled classes), but Facade adds no behavior and the subsystem stays unaware; Mediator centralizes *new* communication.
- **ch17/18/22**: the four sender→receiver connectors.
- **ch22 Observer**: the common implementation substrate for Mediator; the boundary between them is often blurred — when unsure, remember Mediator can also be implemented with permanent links, not just pub/sub.