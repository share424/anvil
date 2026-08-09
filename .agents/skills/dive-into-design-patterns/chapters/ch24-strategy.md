# Chapter 24: Strategy

## Core Idea
Define a family of algorithms, put each in its own class behind a common interface, and make them interchangeable. The **context** delegates to the linked strategy and is blind to which one it holds — so an algorithm can be swapped at runtime without touching the context or other strategies.

## Frameworks Introduced
- **Strategy** — behavioral pattern (a.k.a. Policy).
  - When to use: swap algorithm variants at runtime; you have many similar classes differing only in *how* they do one behavior; isolate algorithm internals from business logic; replace a giant conditional selecting algorithm variants.
  - How: declare a Strategy interface with the algorithm's trigger method; one Concrete Strategy per variant; the Context stores a strategy reference + a setter and delegates execution; the client picks a concrete strategy and assigns it.

## Key Concepts
- **Context**: holds one strategy; delegates; exposes a setter to switch it; knows only the Strategy interface; may expose data the strategy needs.
- **Strategy interface**: the single method the context calls.
- **Concrete Strategy**: one algorithmic variant.
- **Client selects the strategy**: the context doesn't pick — the client must know the differences to choose well.
- **Composition over inheritance**: instead of subclassing the context per behavior, vary behavior by swapping a referenced object.
- **Functional alternative**: in languages with first-class functions, a set of anonymous functions can replace strategy classes — same effect, fewer classes.
- **Swappable at runtime**: pass a new strategy to the setter anytime.

## Mental Models
- Real-world analogy: getting to the airport — bus, cab, or bicycle are interchangeable transportation strategies; you pick by budget/time.
- Strategy changes the **guts** (internal algorithm); Decorator changes the **skin** (external layering).
- A OCP/ISP rule from ch03/ch04 realized concretely: extract a giant `if/switch`-on-variant into polymorphic strategy objects.

## Anti-patterns
- **A bloated"context class with every algorithm variant inline**: each new variant doubles the class and merges-conflict the team — the pain Strategy targets.
- **Over-applying for a couple of rare-changing algorithms**: new classes/interfaces for two stable variants is over-engineering — the documented con.
- **Context selecting the strategy itself**: the client should make the choice (it knows the constraints); if the context picks, it's usually coupled to concrete strategies.
- **Forgetting the functional alternative**: when functions suffice, anonymous lambdas beat a strategy-object hierarchy.

## Code Examples
Runtime-swappable arithmetic strategies:
```pseudo
interface Strategy is  method execute(a, b)

class ConcreteStrategyAdd       implements Strategy is  method execute(a,b) is return a + b
class ConcreteStrategySubtract  implements Strategy is  method execute(a,b) is return a - b
class ConcreteStrategyMultiply  implements Strategy is  method execute(a,b) is return a * b

class Context is
  private strategy: Strategy
  method setStrategy(s: Strategy) is  this.strategy = s
  method executeStrategy(a, b) is  return strategy.execute(a, b)

// client picks based on user input
context.setStrategy(new ConcreteStrategyAdd())   // or Subtract, Multiply
result = context.executeStrategy(first, second)
```
- **What it demonstrates**: the context's `executeStrategy` is one delegation line — adding a strategy (e.g. `Divide`) is a new class, not an edit to `Context` or the other strategies.

## Reference Tables
| Role | Responsibility |
|---|---|
| Context | holds strategy; delegates; exposes setter |
| Strategy interface | single execution method |
| Concrete Strategy | one variant of the algorithm |
| Client | knows the variants; chooses and assigns the strategy |

State vs. Strategy (the book's framing — look-alike cousins):

| | State | Strategy |
|---|---|---|
| Helpers aware of each other? | yes — states transition the context | no — strategies independent |
| Intent | FSM behavior per state | one algorithm's interchangeable variants |

Strategy vs. its structural siblings (Command, Decorator, Template Method, State):

| Cousin | Distinction |
|---|---|
| Command | converts an operation into an object (defer/queue/undo); Strategy = different ways to do *one* thing |
| Decorator | changes the skin (external behavior); Strategy changes the guts (internal algorithm) |
| Template Method | inheritance-based, class level, static; Strategy = composition, object level, runtime |
| State | State's helpers may transition the context; Strategy's may not |

## Worked Example
A navigation app grew road / walking / cycling / transit routing inside one giant `Navigator` class — doubling in size per algorithm, merge conflicts, buggy changes ripple across working code. Strategy: extract each routing algorithm into a `RouteStrategy` with `buildRoute(origin, destination):Checkpoints`. `Navigator` holds a strategy ref and a `setStrategy` setter; UI buttons call `navigator.setStrategy(new WalkingRouteStrategy())` to switch. Adding "tourist-attractions route" is a new class — `Navigator` and the other strategies don't change. The navigator just renders checkpoints; it doesn't know or care which algorithm produced them. (This is also the shape that emerged naturally from "Program to an Interface" + "Favor Composition" in ch03.)

## Key Takeaways
1. Extract an algorithm's variants into interchangeable classes behind one interface; the context delegates.
2. Switch algorithm at runtime by calling the setter — context stays oblivious to the variant.
3. Replace inheritance-based behavior-per-subclass with composition-based behavior-per-strategy.
4. Turns a giant `switch`/`if`-on-variant conditional into polymorphism (OCP: new strategies don't touch the context).
5. Clients must understand the strategies to pick correctly (a real coupling cost).
6. In functional-friendly languages, prefer lambdas over a class-per-strategy unless you need the explicit type.

## Connects To
- **ch03/ch04**: Strategy is the canonical realization of "Program to an Interface" + "Favor Composition Over Inheritance" + OCP (the shipping-cost example in OCP).
- **ch18 Command**: same "parameterize with an action" look; Command = turn *any* operation into an object (defer/queue/undo); Strategy = interchangeable ways to do *one* thing.
- **ch13 Decorator**: "Decorator changes the skin, Strategy changes the guts."
- **ch23 State**: State is an extension of Strategy — State's helpers may transition the context, Strategy's stay independent.
- **ch25 Template Method**: complementary inverse — Template (inheritance, static) vs Strategy (composition, runtime).
- **ch11 Bridge / ch10 Adapter**: same composition shape, different intent (decouple hierarchies / adapt interface).