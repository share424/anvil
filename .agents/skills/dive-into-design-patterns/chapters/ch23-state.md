# Chapter 23: State

## Core Idea
Let an object change its behavior when its internal state changes — as if it swapped classes. Extract every state's behavior into its own state class; the **context** holds a reference to the current state and delegates to it. State objects may know each other and trigger transitions. It implements a finite-state machine with objects instead of `switch`es.

## Frameworks Introduced
- **State** — behavioral pattern (a.k.a. Objects-for-States).
  - When to use: an object behaves differently per state, the state set is large, and the state-specific code changes often; a class is polluted with state-driven `if/switch` conditionals; duplicate code spans similar states.
  - How: declare a State interface of state-specific methods; create a Concrete State per state; the Context stores a state reference, delegates, and provides a transition setter; states may hold a back-reference to the context to read fields and call `context.changeState(...)`.

## Key Concepts
- **Context**: owns a state reference; delegates state-specific work; exposes a setter for transitions.
- **State interface**: methods that make sense in *every* state (avoid useless members).
- **Concrete State**: implements one state's behavior; can transition the context to another state.
- **Back-reference to context**: states often hold a reference so they can read context data and initiate transitions.
- **Who transitions?** Either the context, a concrete state (via its back-reference), or the client — wherever it's done, that class depends on the concrete target state.
- **Finite-State Machine**: the underlying model — finite states, finite predetermined transitions; behaviors differ per state.
- **Abstract intermediate states**: to share common behavior across similar states, factor it into intermediate abstract classes (hierarchies reduce duplication).

## Mental Models
- Real-world analogy: your smartphone's buttons behave differently when it's unlocked, locked, or low-battery — the same physical inputs, different reactions.
- Each state class is "a class the object temporarily *becomes*"; swapping the state object is the transition.

## Anti-patterns
- **Giant `switch(state)` inside each method**: adding a state forces editing `switch`es everywhere; the brittle mess State replaces.
- **State objects knowing nothing of each other (over-applying Strategy's rule)**: State *allows* inter-state awareness and self-initiated transitions — that's the Strategy/State distinction.
- **Overkill for a tiny, rarely-changing FSM**: a couple states and few changes → keep the simple conditionals.

## Code Examples
Audio player context delegating to state objects with transitions:
```pseudo
class AudioPlayer is                       // CONTEXT
  field state: State; volume, playlist, currentSong
  constructor AudioPlayer() is  this.state = new ReadyState(this)   // start state
  method changeState(s: State) is  this.state = s
  method clickLock()      is  state.clickLock()
  method clickPlay()      is  state.clickPlay()
  method clickNext()      is  state.clickNext()
  method startPlayback()  is  // ...
  method stopPlayback()   is  // ...

abstract class State is                   // base + back-reference
  protected field player: AudioPlayer
  constructor State(player) is  this.player = player
  abstract method clickLock(); abstract method clickPlay()
  abstract method clickNext(); abstract method clickPrevious()

class LockedState extends State is
  method clickLock() is                                  // transitions self
    if (player.playing)  player.changeState(new PlayingState(player))
    else                 player.changeState(new ReadyState(player))
  method clickPlay() is { }   // locked: no-op
  method clickNext() is { }
  method clickPrevious() is { }

class ReadyState extends State is
  method clickLock() is  player.changeState(new LockedState(player))
  method clickPlay() is  player.startPlayback(); player.changeState(new PlayingState(player))
  method clickNext() is  player.nextSong()

class PlayingState extends State is
  method clickPlay() is  player.stopPlayback(); player.changeState(new ReadyState(player))
  method clickNext() is
    if (event.doubleclick)  player.nextSong()
    else                     player.fastForward(5)
```
- **What it demonstrates**: the player's UI methods stay one-line delegations; the difference between Locked/Ready/Playing lives in three classes that also *trigger the transitions* — no big `switch`, each state swaps behavior cleanly.

## Reference Tables
| Role | Responsibility |
|---|---|
| Context | holds current state; delegates; exposes transition setter |
| State interface | state-specific methods meaningful in every state |
| Concrete State | behavior for one state; may hold back-ref to context; may transition |

State vs. its structural twins (the book's repeated point):

| Pattern | Helper objects aware of each other? | Delegated thing |
|---|---|---|
| **State** | yes — states may initiate transitions | behavior per finite state (FSM) |
| Strategy | no — strategies independent | one algorithm's interchangeable variants |
| Bridge | no | decouple two orthogonal hierarchies |
| Adapter | — | make one incompatible interface usable |

## Worked Example
A `Document` with states Draft/Moderation/Published and a `publish()` whose outcome differs per state. The naïve version is a `switch(state)` in `publish()` — and another in `edit()`, `delete()`, `revoke()`…, with a branch per state nested in every method. With State: `DraftState.publish()` transitions to Moderation; `ModerationState.publish()` publishes only if `context.currentUser.role == "admin"`; `PublishedState.publish()` is a no-op. Each state owns its behavior and calls `context.changeState(next)` to transition. Adding a new state (`ArchivedState`) means a new class the others reference — no edits scattered across every method (OCP), and the context's methods shrink to delegate calls.

## Key Takeaways
1. State implements an FSM as objects: one class per state; the context delegates to the active one.
2. Transitions replace the context's state object reference — instant behavior swap, "as if it changed class."
3. States may know each other and self-transition via a back-reference to the context (the key difference from Strategy).
4. Eliminates giant per-method `switch(state)` ladders; new states don't touch existing methods (OCP).
5. Hoist shared behavior into abstract intermediate state classes to cut duplication.
6. Overkill for a small, stable state machine — keep the conditionals.

## Connects To
- **ch11 Bridge / ch24 Strategy / ch10 Adapter**: same composition-based structure, different *intent* — a pattern communicates the problem, not just the shape.
- **ch24 Strategy**: State is an extension of Strategy; Strategy's helpers are independent and unaware; State's may transition the context.
- **ch25 Template Method**: contrast — Template alters *parts* of an algorithm via inheritance (class level, static); State swaps whole behavior via composition (object level, runtime).