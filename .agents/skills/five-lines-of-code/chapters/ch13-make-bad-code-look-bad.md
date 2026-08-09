# Chapter 13: Make bad code look bad

## Core Idea
If you can't make code good, make it *visibly* bad — "anti-refactoring" signals process issues, segregates the codebase into pristine vs legacy, and accelerates future real refactoring. Follow three rules so the vandalism is always safe and reversible.

## Frameworks Introduced
- **Anti-refactoring**: deliberately make bad code stand out instead of doing a little "just-so-it's-not-horrible" refactoring that sweeps problems under the rug. A horrible mess is easier to find again and signals unsustainable constraints. Requires psychological safety (Google's Project Aristotle: the top productivity factor).
- **Pristine vs legacy segregation**: rather than "good enough," prefer clearly *bad* when you can't reach "quite good" — obvious bad code is constantly noticed and fixed; "good-enough" code hides rot. Start refactoring from files closest to fully pristine (cascading needs less surrounding work; broken-window theory keeps pristine files pristine).
- **Four bad-code lenses**:
  1. **The book's rules** — simple, concrete, eye-catching to a trained team (FIVE LINES, IF ONLY AT THE START…). Easy to invert on purpose.
  2. **Code smells** (Fowler/Clean Code) — complete and abstract; most need practice to spot, but a few ("magic constants," "duplicated code") are universal.
  3. **Cyclomatic complexity** — objective; counts paths (`if`/`for`/`while`/`||`/`&&` each +1). Also a lower bound on tests needed. Humans estimate it via indentation.
  4. **Cognitive complexity** — algorithmic but subjective; punishes nesting harder (a nested `if` scores higher). Closer to real reading difficulty; still amounts to indentation at a glance.
- **Three rules for safe vandalism**: (1) **Never destroy correct information** (preserve good names; you may remove incorrect/superfluous info like outdated comments). (2) **Don't make future refactoring harder** — preferably easier (e.g., put blank lines where you'd extract methods). (3) **The result must be eye-catching** — a visible gap from pristine code. Anything obeying all three is trivially undoable.
- **Ten safe vandalism methods**:
  1. **Use enums** instead of Booleans/type codes — eye-catching, and the standard enum-removal flow (REPLACE TYPE CODE WITH CLASSES → PUSH CODE INTO CLASSES → TRY DELETE THEN COMPILE) makes future refactoring *easier*.
  2. **Use ints/strings as type codes** when you can't even add an enum — strings carry the name in their content; trivial to promote to an enum later (launches method 1).
  3. **Put magic numbers in the code** — almost everyone reacts to them; inline a poorly-named constant (or comment if unsure) so no information is lost; easy to re-extract.
  4. **Add comments** — a comment that *should be a method name* both signals and seeds the future EXTRACT METHOD; colored/highlighted by editors and rare under Ch 8, so they pop.
  5. **Put whitespace in the code** — blank lines group statements (→ EXTRACT METHOD) or fields (→ ENCAPSULATE DATA); use when you see structure but can't name it. (Beware misleading whitespace.)
  6. **Group by naming** — place common-affix members together so NEVER HAVE COMMON AFFIXES jumps out (→ ENCAPSULATE DATA).
  7. **Add context to names** — append an affix (e.g. `_ArrUtil`) to create common affixes where none existed; break casing (`_`) for extra visibility. Ensure added context is accurate.
  8. **Create long methods** — INLINE poorly-extracted methods into one long method; preserves names via comments and makes the real structure (e.g. repeated `banner.state`) re-assessable. Less instantly spot-able but high recall.
  9. **Give methods many parameters** — undo a `Map` or a data-object/struct by exploding it into a long parameter list; screams at every definition *and* call site (road signs everywhere). Preserves names/types; uncovering which params couple is the future refactoring.
  10. **Use getters and setters** — encapsulate globals/public fields behind `get`/`set` (the conventional prefix makes them spot-able at definition and call sites); they should disappear as you push code into the class. Additive → no information lost.

## Key Concepts
- **"If you cannot make it good, make it stand out"** — the chapter's mantra.
- **Broken window theory** — one bad window invites more; pristine files stay pristine longer (disputed as sociology but useful as metaphor).
- **Project Aristotle** — Google/re:Work finding that psychological safety is the top productivity factor; needed to deliver visible bad code as a messenger.
- **Cyclomatic vs cognitive complexity** — objective path count vs nesting-punished subjective estimate; both reduce to indentation for at-a-glance reading.
- **Road signs** — smells visible at many call sites (long param lists, getters) spread the signal throughout the codebase.
- **Additive vandalism** — adding code (comments, getters, whitespace) can't destroy information.

## Mental Models
- "Good-enough" is the worst tier — it hides rot; prefer visibly bad or quite good.
- A vandalism method is good if it both *signals* and *previews the fix* (enum → REPLACE TYPE CODE WITH CLASSES; comment → EXTRACT METHOD; common affix → ENCAPSULATE DATA).
- Start refactoring where pristine is nearly complete — cascades need little surrounding work and broken windows are fewer.
- Additive changes (comments, getters, whitespace, affixes) are the safest vandalism — no information can be lost.

## Anti-patterns
- **"Just-so-it's-not-horrible" refactoring**: sweeps problems under the rug; deliver a visible mess instead.
- **Destroying correct info to make it stand out**: don't wreck a good name to highlight a bad body.
- **Vandalism that blocks future refactoring**: e.g., inlining in a way that obscures the real structure; the second rule forbids it.
- **Subtle vandalism**: if it's not eye-catching, it fails the third rule and won't get fixed.
- **A `Map`/data-object to "hide" many params**: blindsides the compiler or masks the smell; undo it into a real parameter list.
- **Dropping the `magic`/pristine contract**: the segregated regions only work if pristine stays pristine and legacy is unmistakably legacy.

## Reference Tables

| Method | Signal | Previews fix |
|---|---|---|
| Enums | named type code | REPLACE TYPE CODE WITH CLASSES |
| Ints/strings as type codes | `else if`/`switch` chain | → enum (method 1) |
| Magic numbers | universal reaction | re-extract constant |
| Comments (method-name) | colored, rare | EXTRACT METHOD |
| Whitespace | paragraph breaks | EXTRACT METHOD / ENCAPSULATE DATA |
| Group by naming | affix cluster | ENCAPSULATE DATA |
| Add context to names | unnatural affix | ENCAPSULATE DATA |
| Long methods | recall, re-assess | re-extract correctly |
| Many parameters | every call site | push code into classes |
| Getters/setters | `get`/`set` prefix | push code into class, delete accessor |

| Bad-code lens | Trait |
|---|---|
| Book's rules | simple, concrete, team-trained |
| Code smells | complete, abstract, practiced |
| Cyclomatic complexity | objective path count |
| Cognitive complexity | nesting-punished, subjective |

## Key Takeaways
1. If you can't make it good, make it visibly bad — anti-refactoring signals process issues and segregates pristine from legacy code.
2. Three safety rules: never destroy correct info, don't make future refactoring harder (prefer easier), and the result must be eye-catching.
3. Four bad-code lenses: the book's rules, code smells, cyclomatic complexity, cognitive complexity — all reduce to indentation/spot-ability at a glance.
4. Ten reversible methods (enums, type codes, magic numbers, comments, whitespace, naming groups, name context, long methods, many parameters, getters/setters) each both signal and preview the eventual refactoring.
5. Start real refactoring from files nearest to fully pristine (cascades are safer; broken-window theory preserves them).

## Connects To
- **Ch 4/5/6**: every vandalism method previews a part-1 pattern (REPLACE TYPE CODE WITH CLASSES, EXTRACT METHOD, ENCAPSULATE DATA, PUSH CODE INTO CLASSES).
- **Ch 8**: comments are rare after deletion, so an added comment-as-method-name pops; the same comment→method transformation.
- **Ch 12**: the `magic` package isolation is the same "signal quality at a glance" idea applied to tuned code.
- **Ch 7**: cyclomatic complexity is also a lower bound on tests needed; getters/Map-anti-patterns reprise the "don't fight the compiler" offenses.
