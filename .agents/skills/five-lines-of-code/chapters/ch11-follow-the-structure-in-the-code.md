# Chapter 11: Follow the structure in the code

## Core Idea
Behavior lives in one of three places — control flow, data structures, or data — and refactoring moves it between them. Spot unexploited structure (whitespace, duplication, common affixes, runtime-type inspection) and solidify it with the part-1 patterns; but observe how the code *actually* changes before exploiting any structure, and throttle refactoring under uncertainty.

## Frameworks Introduced
- **Structure-space matrix** (scope × origin): inter-team/in-code = external API (macro-architecture); intra-team/in-code = data/functions, most refactoring (micro-architecture); inter-team/in-people = org chart/processes; intra-team/in-people = behavior/domain experts. Structure mirrors *horizontally* (Conway's law: org structure constrains the external API; domain-expert behavior bleeds into code).
- **Three behavior encodings**:
  1. **Control flow** — control operators, method calls, or lines. Big changes are easy (move statements); method calls/lines express non-local structure; only operators/calls can loop infinitely. Patterns: EXTRACT METHOD, COMBINE IFS.
  2. **Data structures** — behavior frozen into structure (binary search ↔ BST). Type-safe, local, small changes easy; can cache/reuse for performance. Patterns: REPLACE TYPE CODE WITH CLASSES, INTRODUCE STRATEGY PATTERN (move control flow → data structures).
  3. **Data** — behavior in raw values/references (no compiler support; halting-problem blind spot). Hardest to maintain; actively transform it to one of the others.
- **Refactor to support a change vector**: refactoring solidifies structure toward the changes you expect; don't refactor code that won't change. Under uncertainty, throttle refactoring, prioritize correctness, encapsulate the unrefactored code, and *don't add variation points* (they add complexity and hide structure). New/uncertain code → enums + loops (quick to change, heavily tested); mature code → mold with refactoring. Solidity should track confidence in direction.
- **Observe, don't predict**: use empirical techniques (Toyota Kata, Evidence-Based Management, Popcorn Flow). Don't be smart with speculative generality.
  - Chess story: don't build a piece interface for a game unchanged in 500 years.
  - Change rules: doesn't change → do nothing; changes unpredictably → refactor only to avoid fragility; otherwise → refactor to accommodate the *past* kinds of changes.
- **Five safety sources** (for refactoring without understanding): (1) testing (functional tests; walk a mile in users' shoes), (2) mastery (decompose into negligible steps; practice until mechanical), (3) tool assistance (IDE refactors), (4) formal verification (proof assistants for failure-expensive code), (5) fault tolerance (feature-toggle auto-rollback). Use a bit of each; accept residual risk.
- **Four unexploited-structure sources**:
  - **Whitespace** → EXTRACT METHOD (grouped statements) / ENCAPSULATE DATA (grouped fields).
  - **Duplication** → EXTRACT METHOD (statements) → ENCAPSULATE DATA (methods across classes) → UNIFY SIMILAR CLASSES (similar classes) → INTRODUCE STRATEGY PATTERN (similar flow, different statements).
  - **Common affixes** → ENCAPSULATE DATA (fields/methods) or namespaces/packages (classes; NEVER HAVE COMMON AFFIXES).
  - **Runtime-type inspection** (`typeof`/`instanceof`/reflection/casts) → introduce an interface, make both classes implement it, PUSH CODE INTO CLASSES (the `if` disappears — a special case of NEVER USE IF WITH ELSE). If you don't control the types, push the inspection to the edge so the core stays pristine.

## Key Concepts
- **Macro- vs micro-architecture** — inter-team (product/API/platforms) vs intra-team (what the team controls; this book's patterns).
- **Conway's law** — org structure constrains the external API.
- **Users as code/constraint** — if you can retrain users they're in refactoring scope (model behavior as-is, then improve with training); if not, they constrain you.
- **Change vector** — the direction the software is taking; refactoring supports it.
- **Accidental vs essential complexity** (reprise) — variation points add accidental complexity; only add when needed.
- **Dynamic dispatch** — OO's replacement for runtime-type inspection; interfaces + method calls beat `instanceof` chains.

## Mental Models
- "Data structures are algorithms frozen in time" — moving behavior from control flow to data structures trades big-change ease for small-change safety + performance.
- Refactoring doesn't change behavior; it either manages duplication within one encoding or moves structure between encodings.
- Low-effort, low-risk artifacts (blank lines, duplication, common affixes, type inspection) are reliable signals of the author's mental model — exploit them.
- The code's solidity should represent your confidence in its direction; don't cast uncertain code in concrete.

## Anti-patterns
- **Speculative extensibility/generality**: adds accidental complexity and hides structure; observe first.
- **Refactoring code that won't change**: no return on the risk/effort.
- **Adding variation points under uncertainty**: complexity that hampers experimentation.
- **Runtime-type inspection in the core**: push it to the edge; keep the core interface-driven.
- **Relying on a single safety source**: each has a failure mode (test gaps, human error, tool bugs, proof-assistant bugs, rollback mis-detection); blend them.

## Reference Tables

| Structure signal | Refactoring |
|---|---|
| Whitespace between statements | EXTRACT METHOD |
| Whitespace between fields | ENCAPSULATE DATA |
| Duplicated statements | EXTRACT METHOD → (ENCAPSULATE DATA) |
| Similar classes | UNIFY SIMILAR CLASSES |
| Similar flow, different statements | INTRODUCE STRATEGY PATTERN |
| Common affixes (fields/methods) | ENCAPSULATE DATA |
| Common affixes (classes) | namespace/package |
| `instanceof`/`typeof` chains | interface + PUSH CODE INTO CLASSES |

| Change behavior | Action |
|---|---|
| Doesn't change | do nothing |
| Changes unpredictably | refactor only to avoid fragility |
| Changes predictably | refactor to accommodate past change types |

## Key Takeaways
1. Behavior is encoded in control flow, data structures, or data; refactoring moves it between them (never changes behavior).
2. Solidity should track confidence — refactor to support the observed change vector; under uncertainty, throttle and don't add variation points.
3. Observe how code changes rather than predicting; use empirical techniques; don't build generality for a 500-year-stable domain.
4. Refactor without understanding by leaning on five safety sources (tests, mastery, tools, formal verification, fault tolerance).
5. Four reliable structure signals: whitespace, duplication, common affixes, runtime-type inspection — each maps to a specific part-1 pattern.

## Connects To
- **Ch 3–6**: the patterns invoked here (EXTRACT METHOD, ENCAPSULATE DATA, UNIFY SIMILAR CLASSES, INTRODUCE STRATEGY PATTERN, REPLACE TYPE CODE WITH CLASSES, PUSH CODE INTO CLASSES).
- **Ch 7**: runtime-type inspection weakness; data-encoding's halting-problem blind spot.
- **Ch 10**: accidental vs essential complexity; feature toggles as fault tolerance.
- **Ch 12**: throttle refactoring under uncertainty reappears as "avoid premature optimization/generality."
