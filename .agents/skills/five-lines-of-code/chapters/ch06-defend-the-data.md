# Chapter 6: Defend the data

## Core Idea
Encapsulate data so invariants can only be broken locally: ban getters/setters (push computations to the data, not data to a central manager), group common-affix members into classes, and use the constructor to make the compiler enforce sequence invariants.

## Frameworks Introduced
- **DO NOT USE GETTERS OR SETTERS (R6.1.1)**: no setters/getters for non-Boolean fields (name irrelevant; C# properties included).
  - When to use: always; getters break encapsulation and make invariants global.
  - Why: a getter lets the receiver redistribute/mutate the object; a setter couples callers to the internal structure. Prefer a *push-based* architecture (pass data as args, push computation to the data) over a *pull-based* one (dumb data + big managers).
- **ELIMINATE GETTER OR SETTER (P6.1.3)**: remove a getter/setter by moving the functionality closer to the data.
  - How: (1) make it `private` to surface all call sites as errors; (2) fix each with PUSH CODE INTO CLASSES (often producing a context-named method, e.g. `drive`→`notifyGreenLight`); (3) the getter is now unused — delete it.
- **NEVER HAVE COMMON AFFIXES (R6.2.1)**: no methods/variables sharing a prefix or suffix; a common affix signals a cohesion that belongs in a class.
  - When to use: spot `playerx`/`playery`/`drawPlayer`-style groups.
  - Why: classes give controlled external interface, hide helpers (important under FIVE LINES, which spawns many methods), and turn global invariants into local ones.
- **ENCAPSULATE DATA (P6.2.3)**: move variables + their affix-sharing methods into a new class.
  - How: (1) create the class; (2) move variables in, `let`→`private`, simplify names, add getters/setters (temporary); (3) the now-global-scope vars cause compiler errors — fix in 5 sub-steps: pick an instance name, replace access with getters/setters, if ≥2 methods error add the instance as a first param+arg, repeat until one method errors, instantiate at the old declaration site (beware loops!); then ELIMINATE GETTER OR SETTER on the temporary accessors.
- **ENFORCE SEQUENCE (P6.4.1)**: turn a "call A before B" invariant into a compiler-enforced property by moving B into a class whose constructor runs A.
  - When to use: a sequence invariant ("must `transform` before `update`").
  - How (internal variant): ENCAPSULATE DATA on the last method → make the constructor call the first method → if the two methods' args are connected, make them fields and drop them from the method. The instance *is proof* the precondition ran.

## Key Concepts
- **Pull-based vs push-based architecture** — pull: fetch data, compute centrally (dumb data + big managers, tight coupling); push: pass data as args, compute at the data (distributed functionality).
- **Local vs global invariant** — encapsulation limits where an invariant can be broken to one class; only that class's methods need checking.
- **Sequence invariant** — "X must be called before Y"; ENFORCE SEQUENCE eliminates it (you can't get an instance without running the constructor first).
- **Internal vs external ENFORCE SEQUENCE** — internal: target method moved inside the class (stronger encapsulation, no getter); external: public readonly field + a function taking the typed param.
- **Private-constructor enumeration** — when enums can't have methods, use `static readonly` instances + a `private constructor`; can't `switch` on it (which the book forbids anyway), so push code through into per-value classes (REPLACE TYPE CODE WITH CLASSES).
- **Law of Demeter** — "don't talk to strangers"; the smell behind DO NOT USE GETTERS OR SETTERS.
- **Single responsibility principle** — the smell behind NEVER HAVE COMMON AFFIXES ("methods should do one thing", for classes).

## Mental Models
- Think of a getter as a leak: the field escapes and anyone can redistribute/mutate it.
- A common affix is the code asking to be a class; the affix becomes the class name and the prefix/suffix is dropped from the members.
- The instance is proof: if a class's constructor runs the precondition, holding an instance proves the precondition held.

## Anti-patterns
- **Pull-based "manager" + dumb data classes**: tight coupling, global invariants; the getter anti-pattern.
- **Instantiating the encapsulating class inside a loop**: resets state each iteration; instantiate at the original declaration site, not where the lone error remains.
- **A `setColor(g)` that both calls and passes `g`**: violates EITHER CALL OR PASS — push `fillRect` in too, or extract it.
- **Public `setTile`-style methods on a map class**: nearly hands over the private array; push the whole operation in instead.

## Code Examples
```typescript
// Pull-based (bad) vs push-based (good) — generate a blog post link
// Pull: central function pulls data via getters
function generatePostLink(website, post) {
  return website.getUrl() + post.getAuthor().getUsername() + post.getId();
}
// Push: each class offers the service; no getters
class BlogPost {
  constructor(private author: User, private id: string) {}
  generateLink(website: Website) { return this.author.generateLink(website, this.id); }
}
function generatePostLink(website, post) { return post.generateLink(website); }
```
- **What it demonstrates**: push-based distributes functionality to the data and inlines the trivial top-level call.

```typescript
// ENFORCE SEQUENCE (internal): constructor runs the precondition
class CapitalizedString {
  private value: string;
  constructor(str: string) { this.value = capitalize(str); } // must happen first
  print() { console.log(this.value); }
}
```
- **What it demonstrates**: you cannot obtain a `CapitalizedString` without capitalizing; the sequence invariant is gone.

## Worked Example
**Encapsulating `playerx`/`playery`/`drawPlayer`** into `Player`. Create `Player`; move `playerx`/`playery` to `private x/y` + temporary `getX/getY/setX/setY`; the global-scope errors are fixed by adding a `player: Player` parameter to every method that touches the coords (≥2 errors → add param+arg; repeat until one method errors); instantiate `let player = new Player()` at the old `let` site. Push `drawPlayer` in and INLINE METHOD it. Then ELIMINATE GETTER OR SETTER: make `getX` private, push the failing `map[player.getY()][player.getX()+1].moveHorizontal(...)` lines into `Player` as `moveHorizontal(dx)`, `move(dx,dy)`, `pushHorizontal(...)`, `moveToTile(...)` — `getY` and both setters vanish with `getX`. `moveToTile` is now only called inside `Player`, so make it `private`.

## Reference Tables

| Rule/Pattern | Eliminates | Mechanism |
|---|---|---|
| DO NOT USE GETTERS OR SETTERS | field leaks | push computation to data |
| ELIMINATE GETTER OR SETTER | a specific getter/setter | private → PUSH CODE INTO CLASSES → delete |
| NEVER HAVE COMMON AFFIXES | scattered cohesion | group affix members into a class |
| ENCAPSULATE DATA | global variables/methods | move into a class, param-thread, instantiate at decl site |
| ENFORCE SEQUENCE | "A before B" invariant | constructor runs A; instance = proof |

## Key Takeaways
1. Getters/setters break encapsulation and make invariants global; prefer push-based (pass data, compute at the data) over pull-based (dumb data + managers).
2. ELIMINATE GETTER OR SETTER: make it private, push the failing call sites into the owner, delete the now-dead accessor.
3. A common affix = a hidden class; ENCAPSULATE DATA groups the members, and beware instantiating inside a loop.
4. ENFORCE SEQUENCE turns a sequence invariant into a compiler property — the instance is proof the precondition ran.
5. When enums can't have methods, a private-constructor class + per-value classes (REPLACE TYPE CODE WITH CLASSES) removes the enum and its switch.

## Connects To
- **Ch 2**: localizing invariants is the through-line; this chapter is the toolkit for it.
- **Ch 4/5**: reuses PUSH CODE INTO CLASSES, INLINE METHOD, REPLACE TYPE CODE WITH CLASSES produced earlier.
- **Ch 7**: ENFORCE SEQUENCE and encapsulation here are framed as "teaching the compiler invariants" next.
