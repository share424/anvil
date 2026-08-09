# Chapter 21: Memento

## Core Idea
Save and restore an object's prior state **without breaking its encapsulation**. The originator itself produces an immutable **memento** (snapshot) of its private state; a **caretaker** stores mementos and hands them back for restoration, but can't read or alter their contents. A.k.a. **Snapshot**.

## Frameworks Introduced
- **Memento (Snapshot)** — behavioral pattern.
  - When to use: you need snapshots/restoration of an object's state (undo, transactions/rollback), and exposing its fields/getters/setters would violate encapsulation.
  - How: the **Originator** creates an immutable Memento carrying its state and can restore from it; the **Caretaker** holds a stack/history of Mementos and asks the originator to restore; a narrow interface (or nested-class visibility) lets only the originator read the memento's contents.

## Key Concepts
- **Originator**: owns the state; has `createSnapshot()` and a restore path; full access to the memento.
- **Memento**: immutable value object mirroring the originator's fields; only the originator reads/writes its contents; others see only metadata (time, operation name).
- **Caretaker**: decides *when* to snapshot and *when* to restore; stores the memento stack; cannot tamper with state.
- **Access control, three implementations**: (1) nested class (memento nested in originator → private members visible only to originator); (2) intermediate interface (caretaker uses a metadata-only interface, memento's members public for the originator); (3) strict, where the memento is *linked* to its originator and carries the restore method itself.
- **Encapsulation preserved**: no other object can read or alter the snapshot, so refactoring the originator doesn't ripple.
- **Transactions/rollback**: not just undo — used to roll back an operation on error.

## Mental Models
- Real-world: making a full, sealed copy of your editor before each edit — *you* make the copy (so private state is fine), and only you can unseal it; the history list just stores opaque boxes.
- Commands act as caretakers here: a command fetches the editor's memento *before* mutating, and on undo it asks the memento to restore.

## Anti-patterns
- **Outsiders copying an object's private fields** "from the outside": breaks encapsulation and forces re-editing the snapshot class on every internal refactor.
- **Public-field mementos**: expose internal state to every class; changes ripple; fragile.
- **RAM blow-up from too-frequent snapshots**: documented con — caretakers must prune obsolete mementos and track originator lifecycle.
- **Trusting immutability in dynamic languages**: PHP/Python/JS can't guarantee the snapshot stays untouched via type privacy — guard with convention/discipline.

## Code Examples
Editor originator + immutable Snapshot memento + Command caretaker (the stricter linked form):
```pseudo
class Editor is                            // ORIGINATOR
  private field text, curX, curY, selectionWidth
  method setText(text) is        this.text = text
  method setCursor(x, y) is      this.curX = x; this.curY = y
  method setSelectionWidth(w) is  this.selectionWidth = w
  method createSnapshot():Snapshot is
    return new Snapshot(this, text, curX, curY, selectionWidth)

class Snapshot is                          // MEMENTO (immutable, linked to its editor)
  private field editor: Editor
  private field text, curX, curY, selectionWidth
  constructor Snapshot(editor, text, curX, curY, selectionWidth) is
    this.editor = editor; this.text = text; this.curX = curX
    this.curY = curY; this.selectionWidth = selectionWidth
  method restore() is                      // restore knows the originator
    editor.setText(text); editor.setCursor(curX, curY)
    editor.setSelectionWidth(selectionWidth)

class Command is                           // CARETAKER
  private field backup: Snapshot
  method makeBackup() is  backup = editor.createSnapshot()
  method undo() is        if (backup != null)  backup.restore()
```
- **What it demonstrates**: no class but `Editor` reads `Snapshot`'s fields; the command holds the boxed snapshot and just calls `backup.restore()` on undo — encapsulation intact, full undo achieved.

## Reference Tables
| Role | Access to memento | Responsibility |
|---|---|---|
| Originator | full (reads/writes state) | creates snapshots; restores from them |
| Memento | immutable; carries state (+ optional back-ref to originator) | value object |
| Caretaker | metadata only (e.g. timestamp) — never state | stores history; triggers restore |

Access-control implementation trade-off:

| Implementation | Needs nested classes? | Encapsulation strength |
|---|---|---|
| Nested class | yes | strongest (language-enforced) |
| Intermediate interface + public memento members | no | by convention |
| Linked memento carrying `restore()` | either works | strong + multi-originator; originator needs setters |

## Worked Example
A text editor wants undo. Snapshots must include text, cursor x/y, and selection width — all private. The editor's `createSnapshot()` builds a `Snapshot` that takes these in its constructor and never exposes them. A `Command` (Cut, Paste, …) calls `makeBackup()` before mutating, keeping the snapshot. On `Ctrl+Z`, the history pops the command and the command calls `backup.restore()`, which writes the saved values back via the editor's setters. Because each memento is linked to the editor that created it, one centralized undo stack can serve several independent editor windows. Inline state and its full lifecycle stay hidden — the pattern's whole point.

## Key Takeaways
1. The originator makes its own snapshot, so private fields are fine — encapsulation stays intact.
2. Mementos are immutable; only the originator reads their state; caretakers see metadata only.
3. Caretakers (commands, history) decide when to snapshot and when to restore.
4. Three access strategies: nested class, intermediate interface, or linked memento with `restore()` on the memento.
5. Undo is the famous use-case, but transactions/rollback is equally important.
6. Cons: RAM grows with snapshot frequency; caretakers must track originator lifecycle; dynamic languages can't enforce immutability.

## Connects To
- **ch18 Command**: the canonical undo stack — commands perform operations, mementos save the pre-state. Pair them.
- **ch19 Iterator**: Memento can snapshot an iterator's position mid-traversal and roll it back.
- **ch08 Prototype**: a *simpler* alternative when the object has no tricky external links — clone it instead of formal mementos.