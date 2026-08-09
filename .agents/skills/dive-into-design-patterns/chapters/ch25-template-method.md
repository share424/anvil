# Chapter 25: Template Method

## Core Idea
Define the skeleton of an algorithm in a **base class** as a single **template method** calling a series of step methods; subclasses override the steps (abstract or with defaults) but never the skeleton. Lets clients extend only particular steps of an algorithm while keeping its structure intact — and pulls duplicated "structure" code up into the superclass.

## Frameworks Introduced
- **Template Method** — behavioral pattern.
  - When to use: let clients extend only certain steps (not the whole algorithm); several classes contain near-identical algorithms with minor differences and you want to hoist the shared part.
  - How: in an Abstract Class, declare the template method (often `final`) as a sequence of step calls; each step is `abstract`, has a default impl, or is an empty **hook**; Concrete Classes override the steps they need and inherit the structure.

## Key Concepts
- **Template method**: the skeleton — the fixed sequence of step calls; subclasses must not override it.
- **Abstract step**: must be implemented by every subclass.
- **Optional step**: has a default implementation; subclasses may override.
- **Hook**: an optional step with an empty body; placed before/after crucial steps as an extension point; the algorithm works even if it's untouched.
- **Multiple template methods**: a class can have several.
- **Pulling up shared code**: steps with identical implementations across subclasses move into the base; varying steps stay in subclasses — eliminates duplication.
- **Inheritance-based, class level, static** — contrast with Strategy (composition, runtime).

## Mental Models
- Real-world analogy: a mass-housing architectural plan with predefined steps (foundation → framing → walls → plumbing → wiring) where each step has extension points so owners tweak details — the *order* of steps is fixed.
- The template method is a fixed recipe; subclasses supply (or vary) the ingredients at labeled steps, never rewriting the recipe.

## Anti-patterns
- **Duplicating the whole algorithm per variant** instead of overriding just the differing step: the duplication Template Method deletes.
- **Suppressing a default step in a subclass** (no-op override): risks an LSP violation — document it or restructure.
- **Subclasses overriding the template method itself**: defeats the pattern; mark it `final` to prevent it.
- **Too many steps**: the documented con — maintainability drops as the skeleton grows; keep it lean.

## Code Examples
Game AI skeleton with abstract steps + a default step + hooks via `attack()`:
```pseudo
class GameAI is
  method turn() is                       // TEMPLATE METHOD (skeleton)
    collectResources()
    buildStructures()
    buildUnits()
    attack()

  method collectResources() is           // DEFAULT step — shared across races
    foreach (s in this.builtStructures) do  s.collect()

  abstract method buildStructures()       // ABSTRACT step — every subclass implements
  abstract method buildUnits()
  abstract method sendScouts(position)
  abstract method sendWarriors(position)

  method attack() is                     // another template method
    enemy = closestEnemy()
    if (enemy == null)  sendScouts(map.center)
    else                 sendWarriors(enemy.position)

class OrcsAI extends GameAI is           // CONCRETE — overrides specific steps
  method buildStructures() is  // farms → barracks → stronghold
  method buildUnits() is       // peons as scouts, grunts as warriors
  method sendScouts(position) is  // ...
  method sendWarriors(position) is // ...

class MonstersAI extends GameAI is       // LSP-note: suppresses defaults
  method collectResources() is { }       // monsters don't collect (override of a default)
  method buildStructures() is { }
  method buildUnits() is { }
```
- **What it demonstrates**: `turn()` (and `attack()`) is the fixed skeleton; races supply the steps; `collectResources()` is shared by default; `MonstersAI` overrides default steps to no-ops (the documented LSP tension).

## Reference Tables
| Step kind | Has impl? | Subclass must override? |
|---|---|---|
| Abstract step | no | yes |
| Optional step | yes (default) | may override |
| Hook | yes (empty body) | may override — extension point only |

Template Method vs. Strategy (the book's key contrast):

| | Template Method | Strategy |
|---|---|---|
| Mechanism | inheritance | composition |
| Level | class level — static | object level — runtime |
| What changes | parts of *one* algorithm | whole *interchangeable* algorithm |

## Worked Example
A data-mining app parses DOC/CSV/PDF documents. The *algorithm structure* — `openFile → extractData → analyze → parseData → composeReport → closeFile` — is identical across formats; only the file-handling steps differ. Extract a `DataMiner` base with `mine()` as the template method; `openFile`/`extractData`/`parseData`/`closeFile` are abstract (per format), while `analyze`/`composeReport` are shared defaults pulled up. `DocMiner`, `CsvMiner`, `PdfMiner` each implement the abstract steps; none rewrites `mine()`. A new "report tweak" touches only the base's `composeReport`; a new format is a new subclass — the structure and the other subclasses are untouched.

## Key Takeaways
1. Put the algorithm's skeleton (the step order) in a base template method and freeze it (`final`).
2. Vary behavior by overriding individual steps — abstract, optional (default), or empty hook.
3. Hoist identical step implementations into the superclass to kill duplication.
4. Hooks before/after crucial steps give subclasses free extension points without altering the skeleton.
5. It's inheritance-based and static; pair with Strategy when you need runtime swapping.
6. Cons: skeleton constrains clients; overriding a default to no-op risks LSP; many steps get hard to maintain.

## Connects To
- **ch05 Factory Method**: Factory Method is a specialization of Template Method; a factory method may also serve as a step inside a larger Template Method.
- **ch24 Strategy**: complementary inverse — Template (inheritance, static) vs Strategy (composition, runtime).
- **ch04 LSP**: suppressing default steps via subclasses is the call-out where Template Method risks violating LSP.