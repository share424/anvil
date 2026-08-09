# Chapter 2: Introduction to Design Patterns

## Core Idea
A design pattern is a typical, named solution to a recurring software-design problem — a blueprint, not a copy-paste code snippet and not an algorithm. Patterns give a team a shared vocabulary ("use a Singleton") so design intent travels in one word.

## Frameworks Introduced
- **Pattern Anatomy**: the standard sections a pattern description carries — Intent, Motivation, Structure, Code Example (plus applicability, implementation steps, relations).
  - When to use: when reading or writing a pattern; these sections are how the GoF and this book structure every catalog entry.
  - How: scan Intent first for the problem+solution in one line, then Structure for the class relations, then Code Example for the idiom.
- **Pattern Classification (by intent)**: three families — **Creational** (object creation), **Structural** (assembling objects/classes into larger structures), **Behavioral** (communication & responsibility assignment).
  - When to use: when triaging a design problem by *what* is wrong (creation vs. composition vs. interaction).
  - How: state the problem type, then jump to the matching family in the catalog.
- **Pattern Granularity**: idioms (one language, lowest level) → design patterns (middle, language-agnostic class interactions) → architectural patterns (whole-system, highest level).
  - When to use: to calibrate expectations about a "pattern's" scope and portability.

## Key Concepts
- **Design pattern**: a pre-made blueprint you customize to solve a recurring design problem; the same pattern yields different code in different programs.
- **Algorithm vs. pattern**: an algorithm is a recipe (clear steps to a goal); a pattern is a blueprint (shows the result and features, ordering is up to you).
- **Creational patterns**: object-creation mechanisms that increase flexibility and reuse.
- **Structural patterns**: assembling objects/classes into flexible, efficient larger structures.
- **Behavioral patterns**: effective communication and responsibility assignment between objects.
- **Idiom**: a low-level pattern specific to a single language.
- **Architectural pattern**: a high-level pattern applicable to a whole application.
- **GoF book**: *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides, 1994) — the original 23-pattern catalog; named after the four authors.

## Mental Models
- Think of patterns as road engineering: a traffic-light fix (idiom) vs. a multi-level interchange (architectural pattern) — complexity must match the problem's scale.
- Treat a pattern name as a compressed specification: saying "use a Singleton" conveys the whole mechanism and its trade-offs in one word.

## Anti-patterns
- **Copying a pattern's code verbatim**: patterns are blueprints; the implementation must fit your program's realities.
- **Confusing patterns with algorithms**: expecting a fixed step sequence leads you to misuse patterns that are deliberately open-ended.
- **Reaching straight for an architectural pattern when an idiom suffices**: over-scaling the solution.

## Worked Example
How a pattern entry is structured (this book's catalog uses these sections consistently for all 22 patterns):

| Section | Tells you |
|---|---|
| Intent | problem + solution in 1–2 sentences |
| Motivation | a concrete scenario illustrating both |
| Structure | class diagram + relations |
| Code Example | an idiomatic implementation |
| Applicability | when to use it |
| Relations | how it connects to other patterns |

Pattern families at a glance:

| Family | Concern |
|---|---|
| Creational | how objects get made |
| Structural | how objects/classes compose |
| Behavioral | how objects talk & divide work |

## Key Takeaways
1. A pattern is a reusable *concept*, not reusable *code* — you implement it fresh each time.
2. Patterns ≠ algorithms: no mandated order of steps.
3. The three intent families are creational, structural, behavioral — route by *what* is wrong.
4. Pattern granularity runs idioms → design patterns → architectural patterns.
5. A shared pattern vocabulary collapses multi-paragraph design discussions into a single name.
6. The GoF (1994) formalized 23 patterns; many more have since been discovered.

## Connects To
- **Ch 1**: patterns are built from the OOP pillars and relations introduced there.
- **Ch 3–4**: most patterns instantiate the design/SOLID principles — recognize the principle behind each pattern you apply.