# Chapter 8: Stay away from comments

## Core Idea
Comments are usually deodorant over smelly code; the compiler doesn't check them, so they rot. Default to deleting them — only invariant-documenting comments that the compiler/tests can't replace earn a stay. "Comment only what the code cannot say."

## Frameworks Introduced
- **The five comment categories** (ordered easiest→hardest to handle):
  1. **Outdated comments** — wrong/misleading (the code changed, the comment didn't). Delete; they can cause bugs.
  2. **Commented-out code** — version control already keeps history. Delete; never keep as a revert crutch.
  3. **Trivial comments** — restate the code (`/// Log error` / `Logger.error(...)`). Delete; no one reads them.
  4. **Comments that document the code** — extract the block into a method *named after the comment*, then the comment becomes trivial and is deleted.
  5. **Invariant-documenting comments** — document a non-local invariant. Try, in order: eliminate → encode in the compiler (Ch 7) → cover with an automated test; keep only if all fail.
- **Comment-as-method-name**: a documenting comment is a method name waiting to be born. (Reuses EXTRACT METHOD from Ch 3.)
- **Planning comments**: `/// Fetch data / Transform / Submit` are a great road map *during* development; re-evaluate each before delivery (becomes a method or is deleted as trivial).

## Key Concepts
- **Why comments rot** — not compiler-checked, no constraints, so in long-lived systems they drift out of sync; misleading comments are worse than no comment.
- **Deodorant** (Fowler) — comments mask smelly code; clean the code instead.
- **The fallacy** (Henney) — authors of incomprehensible code won't magically express themselves clearly in comments.
- **Process invariants** — `TODO`/`FIXME`/`HACK` are invariants of the *process*, not the code; keep them local but track the count, and it must trend down.
- **Javadoc/external-tool comments** are out of scope here (this chapter is about in-method comments).
- **Sunk-cost vs value** — a comment's value is what it prevents, not what it cost to write.

## Mental Models
- Treat a comment as a todo: can the code say it (a method name, a type, a test)? If yes, make it code. If no, keep it.
- Intermediate/planning comments are great *during* the refactoring phase; deliver none without re-evaluating.
- A comment that can never prevent a bug is dead weight; one that can is the only kind worth keeping.

## Anti-patterns
- **Keeping a comment that disagrees with the code** (`||` vs `&&`): actively introduces bugs.
- **Commenting out code "in case"**: version control is the case; branching is cheaper than the mental clutter.
- **Long method names are bad**: false — frequent words should be short, but rare operations *should* have long, descriptive names (the comment becomes the name).
- **Letting `TODO`/`FIXME` accumulate**: they fester; the count must go down, and "the best time to plant a tree was 20 years ago."

## Code Examples
```typescript
// Comment documenting the code → becomes a method name, then deleted
/// Build request url
if (queryString) fullUrl += "?" + queryString;
// becomes
fullUrl = buildRequestUrl(fullUrl, queryString);
function buildRequestUrl(fullUrl: string, queryString: string) {
  if (queryString) fullUrl += "?" + queryString;
  return fullUrl;
}
```
- **What it demonstrates**: a comment that names a block is an EXTRACT METHOD instruction; afterward the comment is trivial and deleted.

```typescript
// Invariant-documenting comment that stays (can't be a test/compiler check cheaply)
/// Log off used to force re-authentication on next request
session.logout();
```
- **What it demonstrates**: this documents a non-local invariant the compiler can't express and a test would be dreadfully hard to write — so it earns its place.

## Worked Example
A developer rewrites `fib` from recursion to Binet's formula but, unsure it'll work and weak at Git, comments out the old recursive version and leaves it. The fix: branch in Git, delete the old code, experiment; if it fails, `git checkout main` and delete the branch; if it works, merge clean. No commented-out code ships. The same instinct (uncertainty) should have produced a *spike* (Ch 10), not dead code in main.

## Key Takeaways
1. Comments aren't compiler-checked, so they rot; default to deleting them and cleaning the code instead.
2. Five categories: outdated, commented-out, trivial → delete; documenting → turn into a method name; invariant → keep only if compiler/test can't replace it.
3. "Comment only what the code cannot say" — if a method name, type, or test can say it, make it code.
4. Planning comments are fine mid-refactor; re-evaluate every one before delivery.
5. `TODO`/`FIXME`/`HACK` are process invariants — keep them local but drive the count down.

## Connects To
- **Ch 3**: "comment as method name" first appeared there (EXTRACT METHOD turns `// Draw map` into `drawMap`).
- **Ch 7**: invariant-documenting comments are the bottom of the invariant ladder when compiler/test encoding is infeasible.
- **Ch 9**: commented-out code is a form of code that should be deleted; the same "less is better" ethos.
