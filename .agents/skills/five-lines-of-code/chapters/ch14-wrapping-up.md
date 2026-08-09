# Chapter 14: Wrapping up

## Core Idea
The book's underlying philosophy: decompose big transformations into tiny steps between stable ("green-to-green") states, let lines guide methods and methods guide classes, use the rules as tools for collaboration (not laws to police), prioritize simplicity over completeness, and prefer the team over the individual.

## Frameworks Introduced
- **Green to green**: refactor in small steps that each leave the code working; only ever context-switch from/to a green state (a mid-refactor context switch loses the loose threads in your head and spikes error risk; `git reset` to the last green state loses minimal work).
- **Lines → methods → classes → namespaces** (the clay-sculptor cascade): start from the inside and cascade outward — lines guide where methods go, methods guide where classes go, classes guide where packages/namespaces go. Prefer one method too many over one too few (a method can be the difference between a common affix and a new class). (Michelangelo: "every block of stone has a statue inside it.")
- **Rules are tools, not laws**: never apply blindly or use to police teammates; psychological safety is the #1 priority (reprise of Project Aristotle). Rules are a basis for conversation about quality and a launchpad for learning — common sense governs their application.
- **Team over individuals**: software development is a team effort; parallel solo work creates knowledge silos. Pair/ensemble programming distributes knowledge, skills, and responsibility ("if you want to go far, go together"). The team is the method of delivery. Three questions for "is this bad?": (1) Do your developers understand it? (2) Are they happy with it? (3) Is there a simpler version that doesn't break performance/security constraints?
- **Simplicity over completeness** (when designing rules): aim for System-1-applicable rules (fast, low-energy) over System-2 rules (accurate but energy-expensive) — programming is already a System-2 task exhausting mental capacity. On the "simple but wrong" → "complex but right" scale, err toward simplicity for behavioral change; a "these are guidelines" disclaimer plus common sense guards against blind adherence.
- **Objects ≈ higher-order functions**: a one-method object is a higher-order function; with fields it's a closure — same coupling. Choose whichever your team finds more readable (the book used objects for stylistic consistency, not superiority).

## Key Concepts
- **System 1 vs System 2** (Kahneman) — fast/imprecise/cheap vs slow/accurate/expensive; only one System-2 task at a time; rules must run on System 1.
- **Green to green** — small transformations between stable, working states.
- **Clay-sculptor metaphor** — code is malleable and reversible (vs stone); mold to reveal structure within.
- **Three continuation routes**: (1) **Micro-architecture** — deeper smells (Clean Code, Martin) or wider pattern catalog (Refactoring, Fowler); (2) **Macro-architecture / "people route"** — Conway's law, team topology (Team Topologies, Skelton); (3) **Software quality** — testing (TDD, Beck) for product teams, type theory (Types and Programming Languages, Pierce) for platform teams, provable correctness (Type-Driven Development with Idris, Brady; Lean) for the ambitious.

## Mental Models
- Refactoring = searching for ever-smaller steps; small steps reduce risk and preserve the freedom to change course.
- Cascade from the inside out: lines → methods → classes → packages; the smallest unit seeds the next.
- The team is the delivery unit; optimize for shared understanding and happiness, not individual parallelism.
- A rule's value is its applicability under cognitive load, not its universality — simple-and-applicable beats complete-and-ignored.

## Anti-patterns
- **Context-switching mid-refactor**: loses the loose threads; only switch at green states.
- **Using rules to police teammates**: destroys psychological safety, the top productivity factor.
- **One-method-too-few**: can hide a common affix and the class it implies; prefer over-extraction.
- **Designing rules to be universal**: drifts toward vague code-smell territory; lose ease of application.
- **Solo parallelism as efficiency**: creates knowledge silos; prefer pair/ensemble for distribution + trust.

## Key Takeaways
1. Decompose large transformations into tiny green-to-green steps; only ever context-switch from/to a green state.
2. Cascade outward from lines → methods → classes → namespaces; prefer one method too many over one too few.
3. Rules are tools, not laws — use them for collaboration and learning, never to police; common sense governs.
4. Prioritize the team over individuals; pair/ensemble distributes knowledge, skills, and responsibility.
5. Prefer simple, System-1-applicable rules over complete-but-demanding ones; simplicity drives behavioral change.
6. Continue via micro-architecture (smells/patterns), macro-architecture (Conway's law/team topology), or software quality (testing/type theory/provable correctness).

## Connects To
- **Ch 1–13**: this chapter is the synthesis — green-to-green reframes the whole part-1 workflow; the cascade is the part-1 method; rules-as-tools ties to Ch 13's anti-refactoring safety rules.
- **Ch 10**: feature-toggle adoption was the model for "build the reflex before exploiting the benefit" (small steps + culture).
- **Ch 11**: structure mirrors people (Conway's law) — the bridge to the macro-architecture route.
- **Ch 13**: psychological safety (Project Aristotle) reappears as the precondition for delivering visible bad code.
