# Chapter 1: Refactoring refactoring

## Core Idea
Refactoring needs skills (what), culture (when), and tools (how); this book replaces fuzzy code smells with concrete, memorable rules and tiny compiler-checked refactoring patterns so refactoring can be learned without automated tests.

## Frameworks Introduced
- **Six-step workflow**: explore → specify → implement → test → refactor → deliver.
  - When to use: any programming task; refactoring is step 5, separated from TDD.
- **"First make the change easy, then make the easy change" (Kent Beck)**: in legacy systems, refactor before changing.

## Key Concepts
- **Refactoring** — changing code to be more human-readable and maintainable without changing what it does (book definition, Ch 1).
- **Good code** — human-readable, easy to maintain, and correctly does what it set out to do.
- **Code smells** — abstract descriptions suggesting bad code; powerful but hard to internalize.
- **Rules** — concrete, easy-to-recognize, absolute-named heuristics that stand in for smells while learning (three levels: name, description+exceptions, intention).
- **Spike (XP)** — code written to run once and delete; one of the "don't refactor" cases.
- **Red-green-refactor** — TDD loop; this book decouples refactoring from it.

## Mental Models
- Use rules as training wheels: follow the absolute name, then learn exceptions, then internalize the underlying smell.
- Think of rules as TODO lists: each rule links to refactoring patterns that fix violations via explicit steps.

## Anti-patterns
- **Refactor everything first in a legacy system**: instead refactor only the code you're about to change ("make the change easy").
- **Require automated tests before learning refactoring**:_testing is a separate hard skill; rely on compiler + version control + tiny steps first.

## Worked Example
A function returns `pow(base, exp / 2) * pow(base, exp / 2)`. Refactor to `let result = pow(base, exp / 2); return result * result;` — behavior unchanged, but faster (an example of refactoring for readability/performance that doesn't change what the code does).

## Key Takeaways
1. Make refactoring part of daily work: refactor after changes, or before changes in legacy code.
2. Don't refactor: throwaway spikes, retirement-bound maintenance code, strict performance-tuned code.
3. Use the compiler, version control (Git), and step-by-step patterns instead of requiring automated tests.
4. Tools needed: an OO language (TypeScript in the book), an editor (VS Code), Git.
5. Overarching example: a 2D Boulder-Dash-like puzzle game refactored through Part 1.

## Connects To
- **Ch 2**: technical foundation (readability, maintainability, composition).
- **Domain**: the 2D game is the domain for Part 1.