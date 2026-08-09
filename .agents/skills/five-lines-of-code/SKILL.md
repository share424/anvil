---
name: five-lines-of-code
description: "Knowledge base from \"Five Lines of Code: How and when to refactor\" by Christian Clausen (Manning, 2021). Use when applying Clausen's refactoring rules and patterns (FIVE LINES, EXTRACT METHOD, REPLACE TYPE CODE WITH CLASSES, INTRODUCE STRATEGY PATTERN, etc.), deciding how/when to refactor or delete code, or referencing specific chapters."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Five Lines of Code: How and when to refactor
**Author**: Christian Clausen | **Foreword**: Robert C. Martin | **Pages**: ~338 | **Chapters**: 14 | **Generated**: 2026-07-30

## How to Use This Skill
- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `refactoring`, `type codes`, `getters`, `feature toggles`, etc.; I find and read the relevant chapter
- **With chapter** — ask for `ch05`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### The part-1 cascade (how Clausen refactors)
Use **lines to guide where methods go, methods to guide where classes go, classes to guide where packages go** — start from the inside and cascade outward (Ch 14). Refactor by **shape first, specifics later**: you can refactor without understanding what the code does, following its existing structure (Ch 3, 11). Always go **green to green** — small steps between working states; only context-switch at a green state (Ch 14).

### The 9 named rules (exact names matter — preserve codes)
- **FIVE LINES (R3.1.1)** — methods ≤ 5 statements (braces excluded); ≈ one pass through the fundamental data structure.
- **EITHER CALL OR PASS (R3.1.1)** — call methods on an object *or* pass it as an arg, not both; fix with EXTRACT METHOD.
- **IF ONLY AT THE START (R3.5.1)** — an `if` should be the first thing in the function; an `if`+`else if` chain is one atomic unit.
- **NEVER USE IF WITH ELSE (R4.1.1)** — `if`-`else` is a decision → replace with classes (REPLACE TYPE CODE WITH CLASSES).
- **NEVER USE SWITCH (R4.3.1)** — the only allowed switch is on an enum you're about to eliminate.
- **ONLY INHERIT FROM INTERFACES (R4.3.2)** — never inherit from classes (inheritance = default behavior + coupling).
- **USE PURE CONDITIONS (R5.3.2)** — conditions have no side effects; prerequisite for conditional arithmetic (`||`=+, `&&`=×).
- **NO INTERFACE WITH ONLY ONE IMPLEMENTATION (R5.4.3)** — postpone interfaces; extract via EXTRACT INTERFACE FROM IMPLEMENTATION when variance arrives.
- **DO NOT USE GETTERS OR SETTERS (R6.1.1)** — no getters/setters for non-Boolean fields; prefer push-based over pull-based architecture.
- **NEVER HAVE COMMON AFFIXES (R6.2.1)** — a common affix is a hidden class; ENCAPSULATE DATA.

### The 13 refactoring patterns (with codes)
- **EXTRACT METHOD (P3.2.1)** — break long functions; a blank line/comment is a method name waiting to be born.
- **REPLACE TYPE CODE WITH CLASSES (P4.1.3)** — enum/Boolean → interface + per-value classes; eliminates `if`/`switch`.
- **PUSH CODE INTO CLASSES (P4.1.5)** — move a method onto the class whose data it uses; simplifies the name.
- **INLINE METHOD (P4.1.7)** — remove a method that no longer aids readability; also a vandalism tool.
- **SPECIALIZE METHOD (P4.2.2)** — remove unneeded generality (a param always one value).
- **TRY DELETE THEN COMPILE (P4.5.1)** — delete to let the compiler find the unused.
- **UNIFY SIMILAR CLASSES (P5.1.1)** — merge classes differing only in constant methods (a basis, ≤ N−1 for N classes).
- **COMBINE IFS (P5.2.1)** — join adjacent `if`s with identical bodies via `||`.
- **INTRODUCE STRATEGY PATTERN (P5.4.2)** — move variance into its own class; the book's most powerful pattern; ultimate late binding.
- **EXTRACT INTERFACE FROM IMPLEMENTATION (P5.4.4)** — extract the interface only when a second implementation exists.
- **ELIMINATE GETTER OR SETTER (P6.1.3)** — make it private, push call sites in, delete the accessor.
- **ENCAPSULATE DATA (P6.2.3)** — group common-affix variables/methods into a class; pass `this`, not private fields.
- **ENFORCE SEQUENCE (P6.4.1)** — constructor runs the precondition; the instance is proof it ran.

### The guiding philosophy
- **Code is a liability, not an asset** — "less is better" (Ch 9); delete anything not paying for itself, even working features.
- **Adding > modifying** — a new method/endpoint/class can't break existing callers (Ch 10); modify by addition for backward compatibility.
- **Refactor to support a change vector** — don't refactor code that won't change; under uncertainty, throttle and add no variation points (Ch 11).
- **Make the compiler a teammate** — encode invariants as types/access/sequence; zero warnings; don't fight it (casts/`any`/defaults/inheritance/unchecked exceptions) (Ch 7).
- **Make bad code look bad** — if you can't make it good, make it visibly bad (three safe-vandalism rules) (Ch 13).
- **Simplicity over completeness** — rules must run on System 1; they're tools for collaboration, not laws to police (Ch 14).

### Socio-technical toolkit
- **Strangler fig** (gate + monitor legacy → migrate most-used, delete least) and **spike and stabilize** (6-week decide point) (Ch 9).
- **Feature toggles** (deploy ≠ release; remove ≤6 wk) and **branch by abstraction** (localize multi-site feature invariants) (Ch 10).
- **Invariant ladder**: eliminate → teach compiler → automated test → document → manual → pray (Ch 7).
- **Theory of constraints + resource pooling**; optimize only on failing perf tests; isolate tuning in a `magic` package (Ch 12).

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-refactoring-refactoring.md) | Refactoring refactoring | What/When/How of refactoring; skills-culture-tools; TypeScript+VSCode+Git |
| [ch02](chapters/ch02-looking-under-the-hood-of-refactoring.md) | Looking under the hood of refactoring | Readability/maintainability; composition over inheritance; addition over modification; nonlocal invariants; domain |
| [ch03](chapters/ch03-shatter-long-functions.md) | Shatter long functions | FIVE LINES, EXTRACT METHOD, EITHER CALL OR PASS, IF ONLY AT THE START |
| [ch04](chapters/ch04-make-type-codes-work.md) | Make type codes work | NEVER USE IF WITH ELSE, REPLACE TYPE CODE WITH CLASSES, PUSH CODE INTO CLASSES, INLINE METHOD, SPECIALIZE METHOD, NEVER USE SWITCH, ONLY INHERIT FROM INTERFACES, TRY DELETE THEN COMPILE |
| [ch05](chapters/ch05-fuse-similar-code-together.md) | Fuse similar code together | UNIFY SIMILAR CLASSES, COMBINE IFS, USE PURE CONDITIONS, INTRODUCE STRATEGY PATTERN, NO INTERFACE WITH ONLY ONE IMPLEMENTATION, EXTRACT INTERFACE FROM IMPLEMENTATION, UML class diagrams |
| [ch06](chapters/ch06-defend-the-data.md) | Defend the data | DO NOT USE GETTERS OR SETTERS, ELIMINATE GETTER OR SETTER, NEVER HAVE COMMON AFFIXES, ENCAPSULATE DATA, ENFORCE SEQUENCE, private-constructor enums |
| [ch07](chapters/ch07-collaborate-with-the-compiler.md) | Collaborate with the compiler | Compiler strengths/weaknesses; reachability, definite assignment, access control, types; invariant ladder; zero warnings; don't fight the compiler |
| [ch08](chapters/ch08-stay-away-from-comments.md) | Stay away from comments | Five comment categories; comment-as-method-name; invariant-documenting comments; "comment only what the code cannot say" |
| [ch09](chapters/ch09-love-deleting-code.md) | Love deleting code | Four incidental complexities; strangler fig; spike and stabilize; branch WIP limit; test cleanup; config scoped in time; library triage |
| [ch10](chapters/ch10-never-be-afraid-to-add-code.md) | Never be afraid to add code | Enter the danger; spikes; fixed 20% ratio; copy/paste velocity; extensibility; backward compatibility; feature toggles; branch by abstraction |
| [ch11](chapters/ch11-follow-the-structure-in-the-code.md) | Follow the structure in the code | Three behavior encodings (control flow/data structures/data); structure-space matrix; Conway's law; four unexploited-structure sources; five safety sources |
| [ch12](chapters/ch12-avoid-optimizations-and-generality.md) | Avoid optimizations and generality | Simplicity; build minimally; unify similar stability; perf tests; refactor before optimizing; theory of constraints; resource pooling; caching tiers; isolate tuning |
| [ch13](chapters/ch13-make-bad-code-look-bad.md) | Make bad code look bad | Anti-refactoring; pristine vs legacy; cyclomatic/cognitive complexity; three safe-vandalism rules; ten vandalism methods |
| [ch14](chapters/ch14-wrapping-up.md) | Wrapping up | Green to green; lines→methods→classes→namespaces; rules as tools not laws; team over individuals; simplicity over completeness; three continuation routes |

## Topic Index
- **A/B testing** → ch09, ch10
- **Access control** → ch07
- **Addition over modification** → ch02, ch10
- **Anti-refactoring** → ch13
- **assertExhausted / never** → ch07
- **Backward compatibility** → ch10
- **Branch by abstraction** → ch10
- **Branch limit (WIP)** → ch09
- **Broken window theory** → ch07, ch13
- **Caching** → ch12
- **Circus/bus/lottery factor** → ch09
- **Cognitive complexity** → ch13
- **COMBINE IFS** → ch05
- **Common affixes** → ch06, ch11, ch13
- **Compiler as todo list** → ch07
- **Composition over inheritance** → ch02, ch07
- **Conditional arithmetic** → ch05
- **Conservative analysis** → ch07
- **Constant method / basis** → ch05
- **Cyclomatic complexity** → ch13
- **Definite assignment** → ch07
- **Deleting code** → ch09
- **DO NOT USE GETTERS OR SETTERS** → ch06
- **Domain** → ch02
- **Dynamic dispatch** → ch11
- **EITHER CALL OR PASS** → ch03
- **ELIMINATE GETTER OR SETTER** → ch06
- **ENCAPSULATE DATA** → ch06
- **ENFORCE SEQUENCE** → ch06
- **Enter the danger** → ch10
- **Essential vs accidental complexity** → ch10, ch11, ch12
- **EXTRACT INTERFACE FROM IMPLEMENTATION** → ch05
- **EXTRACT METHOD** → ch03
- **Feature toggles** → ch09, ch10
- **FIVE LINES** → ch03
- **Frozen project** → ch09
- **Green to green** → ch14
- **Halting problem** → ch07
- **Hot spot (profiling)** → ch12
- **IF ONLY AT THE START** → ch03
- **INLINE METHOD** → ch04
- **INTRODUCE STRATEGY PATTERN** → ch05
- **Invariant ladder** → ch07
- **Law of Demeter** → ch06
- **Legacy code / strangler fig** → ch09
- **Less is better / sunk cost** → ch09
- **Lines → methods → classes** → ch14
- **Macro- vs micro-architecture** → ch11
- **Magic bit pattern / tuning** → ch12
- **NEVER HAVE COMMON AFFIXES** → ch06
- **NEVER USE IF WITH ELSE** → ch04
- **NEVER USE SWITCH** → ch04
- **NO INTERFACE WITH ONLY ONE IMPLEMENTATION** → ch05
- **Nonlocal invariant** → ch02, ch06
- **ONLY INHERIT FROM INTERFACES** → ch04
- **Optimization** → ch12
- **Performance tests (benchmark/load/approval)** → ch12
- **Private-constructor enumeration** → ch06
- **Profiling** → ch12
- **Pull-based vs push-based** → ch06
- **Pure conditions** → ch05
- **PUSH CODE INTO CLASSES** → ch04
- **Reachability** → ch07
- **REPLACE TYPE CODE WITH CLASSES** → ch04
- **Resource pooling / theory of constraints** → ch12
- **Sequence invariant** → ch06
- **Simplicity over completeness** → ch14
- **Spike / spike and stabilize** → ch09, ch10
- **Strategy pattern** → ch05
- **System 1 vs System 2** → ch14
- **Technical debt / waste / drag / ignorance** → ch09
- **TRY DELETE THEN COMPILE** → ch04
- **UML class diagram** → ch05
- **UNIFY SIMILAR CLASSES** → ch05
- **USE PURE CONDITIONS** → ch05
- **Warnings (zero policy)** → ch07

## Supporting Files
- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and refactoring patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

## Scope & Limits
This skill covers the book content only. For hands-on implementation in your codebase, combine with project-specific tools. For topics beyond this book, check related skills or ask the agent directly.
