# Chapter 3: Shatter long functions

## Core Idea
Break long methods with the FIVE LINES rule and EXTRACT METHOD, balance abstraction with EITHER CALL OR PASS, and isolate checks with IF ONLY AT THE START — all without needing to understand what the code does.

## Frameworks Introduced
- **FIVE LINES (R3.1.1)**: a method should not contain more than five lines, excluding `{` and `}`.
  - When to use: always; the limit is "one pass through the fundamental data structure" (≈5 for a 2D array).
- **EXTRACT METHOD (P3.2.1)**: take part of a method into its own named method.
  - How: mark grouping (blank lines/comments) → new empty method → put call at top → cut/paste body → compile → add parameters (and `return p;` for assignments) → pass args → remove obsolete comments.
- **EITHER CALL OR PASS (R3.1.1)**: a function should either call methods on an object or pass it as an argument, but not both.
  - When to use: a method mixes abstraction levels; fix by EXTRACT METHOD.
- **IF ONLY AT THE START (R3.5.1)**: if you have an `if`, it should be the first thing in the function.
  - When to use: an `if` sits mid-method; extract it (an `if`+`else if` chain is one atomic unit).

## Key Concepts
- **Statement/line** — an `if`, `for`, `while`, or anything ending in `;` (whitespace/braces excluded when counting).
- **Good function name** — honest (describes intent), complete (captures everything), understandable (uses domain words).
- **Shape-based refactoring** — find groupings via blank lines/comments without reading specifics; "best way to eat an elephant is one bite at a time".
- **`if` as a check vs `if`-`else` as a decision** (foreshadows Ch 4).

## Mental Models
- Use lines to guide methods, methods to guide classes (the Part-1 cascade, reprised in Ch 14).
- Work bottom-up when extracting (pushes `return` upward so you eventually return in all branches).
- Treat method names as comments placed at least every 5 lines.

## Anti-patterns
- **Diving into specifics before shaping**: unproductive; group by structure first.
- **Keeping comments that became method names**: delete them once the method exists (they go stale).
- **Breaking an `else if` chain**: it's an atomic unit; don't split it (that's why we need Ch 4).

## Code Examples
```typescript
function draw() {
  let g = createGraphics();   // extracted; EITHER CALL OR PASS satisfied
  drawMap(g);
  drawPlayer(g);
}
```
- **What it demonstrates**: EXTRACT METHOD shrinks `draw` to ≤5 lines and gives each piece an honest domain name, eliminating comments.

## Worked Example
`draw` had two commented groupings `// Draw map` and `// Draw player`. Steps: create empty `drawMap`, call it where the comment was, cut the grouped lines into its body, compile, add the `g: CanvasRenderingContext2D` parameter, pass `g`. Repeat for `drawPlayer`. The comments become method names and are deleted. Then `EITHER CALL OR PASS` flags that `draw` both calls and passes `g`; extract `createGraphics` to fix it.

## Key Takeaways
1. Any method can be reduced to ≤5 lines by repeated EXTRACT METHOD.
2. Refactor by shape first, specifics later — saves time and works on code you don't understand.
3. EXTRACT METHOD exploits the compiler as a safety net: introduce parameters to cause errors, then fix them.
4. Honest, complete, domain-understandable names are the readability payoff of small methods.
5. IF ONLY AT THE START isolates checks; an `if`+`else if` chain is the smallest extractable unit.

## Connects To
- **Ch 4**: `handleInput`'s `else if` chain can't be split by EXTRACT METHOD → introduces NEVER USE IF WITH ELSE and REPLACE TYPE CODE WITH CLASSES.
- **EITHER CALL OR PASS**: reused in Ch 6 (passing `g`) and Ch 12 (refactor before optimize).