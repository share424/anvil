# Chapter 11: Bridge

## Core Idea
Split a class (or set of closely related classes) that varies in two independent dimensions into **two separate hierarchies** — *abstraction* and *implementation* — connected by a reference, so each dimension grows linearly instead of multiplicatively, and the implementation can even be swapped at runtime.

## Frameworks Introduced
- **Bridge** — structural pattern.
  - When to use: a monolithic class varies along several axes (e.g. GUI × OS-API, shape × color, remote × device); you want to extend a class in orthogonal dimensions; you need to switch implementations at runtime.
  - How: extract one dimension into its own hierarchy; the abstraction holds a reference to an implementation object and delegates the low-level work to it; client links an abstraction to an implementation (usually via constructor).

## Key Concepts
- **Abstraction (interface layer)**: high-level control logic; does no real work itself — delegates to the implementation. Not the same as a language `interface`/`abstract class`.
- **Implementation (platform layer)**: declares the interface common to all concrete implementations; provides primitive operations the abstraction builds on.
- **Refined Abstraction**: variant of the high-level logic, extending the base abstraction.
- **Concrete Implementation**: platform-specific code following the implementation interface.
- **Orthogonal dimensions**: the independent axes (form vs. color, GUI vs. API, remote vs. device); the cause of combinatorial explosions under single inheritance.
- **Runtime swap**: optional; you can reassign the implementation field to switch platforms without touching the abstraction.

## Mental Models
- A bridge converts "N×M subclasses" (RedCircle, BlueSquare, …) into "N+M": a Shape hierarchy delegating color to a Color hierarchy — the reference field is the *bridge*.
- The abstraction is the front-end/GUI; the implementation is the back-end/platform API. Add a GUI without touching OS code; add an OS without touching GUI code.
- Bridge vs. Strategy look structurally identical — but Bridge's intent is "decouple two hierarchies," Strategy's is "swap a single algorithm."

## Anti-patterns
- **Extending one hierarchy in two dimensions via inheritance**: RedCircle/BlueSquare/BlueTriangle… — exponential subclasses, duplicated code.
- **A monolith with hundreds of conditionals** joining GUI-types to API-types: a change anywhere risks side effects across the whole thing; split into hierarchies.
- **Applying Bridge to a highly cohesive class**: if the class doesn't actually vary in independent dimensions, splitting only adds complexity.

## Code Examples
Devices (implementation) vs. remotes (abstraction):
```pseudo
class RemoteControl is
  protected field device: Device
  constructor RemoteControl(device: Device) is  this.device = device
  method togglePower() is
    if (device.isEnabled()) then  device.disable()  else  device.enable()
  method volumeUp() is  device.setVolume(device.getVolume() + 10)

class AdvancedRemoteControl extends RemoteControl is
  method mute() is  device.setVolume(0)

interface Device is
  method isEnabled(); method enable(); method disable()
  method getVolume(); method setVolume(percent)
  method getChannel(); method setChannel(channel)

class Tv implements Device is  // ...
class Radio implements Device is  // ...

// client links them
remote = new RemoteControl(new Tv());        remote.togglePower()
remote = new AdvancedRemoteControl(new Radio())
```
- **What it demonstrates**: the remote hierarchy (abstraction) and the device hierarchy (implementation) evolve independently — `mute()` is added to remotes with no device change; a new `SmartTv` device works with existing remotes.

## Reference Tables
Combinatorial-explosion collapse:

| Approach | Shape×Color = 2×2 | Adding a 3rd shape | Adding a 3rd color |
|---|---|---|---|
| Single inheritance | RedCircle, BlueCircle, RedSquare, BlueSquare | +RedTriangle, BlueTriangle (+2) | +3 red/blue/triangle of new color (+6 total) |
| Bridge (Color class held by Shape) | Shape←Circle/Square; Color←Red/Blue | +Triangle (+1) | +newColor (+1) |

Two-hierarchy roles:

| Hierarchy | Role | Example |
|---|---|---|
| Abstraction | high-level control, delegates work | RemoteControl / GUI |
| Implementation | primitive platform operations | Device / OS API |

## Worked Example
Shape×color: the naive `BlueCircle`/`RedSquare` explosion becomes a `Shape` abstraction holding a `Color` implementation reference. `Shape` delegates drawing's color step to `color.fill()`; `Circle`/`Square` refine the abstraction, `Red`/`Blue` are concrete implementations. Adding `Triangle` adds one abstraction class; adding `Green` adds one implementation class — no cross-product, no edits to the other hierarchy (OCP both ways). The book notes Shape/Color is a teaching simplification; real apps split GUI-abstraction × OS-implementation.

## Key Takeaways
1. Bridge decouples two independent dimensions into two hierarchies linked by a reference.
2. It turns exponential subclass growth into linear (N+M instead of N×M).
3. The abstraction holds/owns the implementation reference and delegates the real work.
4. Implementations are interchangeable (optionally at runtime) as long as they share the implementation interface.
5. Bridge is designed up-front; Adapter is applied after the fact to incompatible existing classes.
6. Bridge/State/Strategy share a composition shape but signal different *problems* — intent is part of the pattern.

## Connects To
- **ch10 Adapter**: Bridge = up-front decoupling; Adapter = retrofitted compatibility.
- **ch06 Abstract Factory**: pair when abstractions only work with specific implementations — the factory encapsulates the pairing.
- **ch07 Builder**: combine Builder + Bridge — director = abstraction, builders = implementations.
- **ch23 State, ch24 Strategy**: same structure, different intent ("decouple hierarchies" vs. "swap behavior").