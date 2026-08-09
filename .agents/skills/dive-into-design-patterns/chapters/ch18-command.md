# Chapter 18: Command

## Core Idea
Turn a request into a stand-alone object carrying everything needed to execute it (receiver, method, args). Senders trigger commands through a single `execute()` interface, so requests can be passed around, queued, scheduled, logged, sent remotely, and undone — GUI and business logic decouple cleanly. A.k.a. **Action, Transaction**.

## Frameworks Introduced
- **Command (Action, Transaction)** — behavioral pattern.
  - When to use: parameterize objects with operations; queue/schedule/remote-execute operations; implement reversible (undo/redo) operations.
  - How: declare a Command interface with a single `execute()` (optionally `undo()`); Concrete Commands hold a receiver + args (set via constructor, often immutable); the Sender stores a command and triggers it; the Client wires commands to senders.

## Key Concepts
- **Sender (Invoker)**: holds a command reference, triggers `execute()`; does *not* create the command — receives it (usually via constructor) from the client.
- **Command interface**: typically one execution method taking no params (params live in the command).
- **Concrete Command**: stores receiver + args; delegates the real work to the receiver; can be merged with the receiver for simple cases.
- **Receiver**: the business-logic object that does the actual work; any object can be a receiver.
- **Client**: creates and configures commands (passes receiver + args) and associates them with senders.
- **Undo/redo**: keep a **history** stack of executed commands; each saves a backup before running (`saveBackup`) and restores it on `undo()`. Alternative: run the inverse operation.
- **Composition of commands**: a command can assemble several simple commands into a complex one.

## Mental Models
- Real-world analogy: a restaurant order slip is a command — it carries all info the chef needs, queues on the wall, and is executed later; the waiter doesn't brief the chef verbally.
- The GUI no longer subclasses `Button` per action; one `Button` class holds a command field and runs it on click — toolbar buttons, menu items, and `Ctrl+C` all bind to the *same* command object, killing duplication.

## Anti-patterns
- **Subclassing the GUI element per action** (`CopyButton`, `PasteButton`): explodes subclasses, couples GUI to business logic, duplicates the same operation across toolbar/menu/shortcut.
- **Command performing the work itself**: it should delegate to a receiver (unless trivial) to stay a thin link — keeps separation of concerns.
- **Undo via naive state save with private fields**: hard to snapshot; mitigate with Memento. (Documented con.)
- **RAM-heavy history of full backups**: prefer the inverse-operation undo when feasible — though it can itself be hard/impossible.

## Code Examples
Undoable text-editor commands with a history stack:
```pseudo
abstract class Command is
  protected field app: Application; editor: Editor; backup: text
  constructor Command(app, editor) is  this.app = app; this.editor = editor
  method saveBackup() is  backup = editor.text
  method undo() is  editor.text = backup
  abstract method execute()          // true if it changes editor state (=> saved to history)

class CutCommand extends Command is
  method execute() is
    saveBackup()
    app.clipboard = editor.getSelection()
    editor.deleteSelection()
    return true

class PasteCommand extends Command is
  method execute() is
    saveBackup(); editor.replaceSelection(app.clipboard); return true

class CommandHistory is
  private field history: array of Command
  method push(c) is  // ...
  method pop():Command is  // ...

class Application is              // sender
  field history: CommandHistory
  method executeCommand(command) is
    if (command.execute())  history.push(command)
  method undo() is
    command = history.pop()
    if (command != null)  command.undo()
```
- **What it demonstrates**: toolbar/shortcut/menu all bind to `CopyCommand`/`CutCommand`/etc.; `execute()` returns whether to record for undo; `undo()` restores the saved backup — the app calls `command.undo()` polymorphically, never knowing the concrete class.

## Reference Tables
| Role | Responsibility |
|---|---|
| Sender (Invoker) | holds + triggers a command; doesn't build it |
| Command interface | single `execute()` (optionally `undo()`) |
| Concrete Command | stores receiver + args; delegates real work |
| Receiver | does the actual business work |
| Client | creates+configures commands, wires them to senders |

Connector comparison (with ch17/20/22):

| Pattern | Link style |
|---|---|
| **Command** | fixed, unidirectional sender→command→receiver |
| Chain of Responsibility | sequential, dynamic, first-willing-handler stops |
| Mediator | indirect, via mediator |
| Observer | dynamic subscribe/unsubscribe |

## Worked Example
Text editor with toolbar buttons, context menu, and keyboard shortcuts all needing Copy/Cut/Paste. Without Command you'd subclass `Button` or duplicate logic across menu/shortcut. With Command: `CopyCommand(app, editor)`, `CutCommand(...)`, etc., each bound to the toolbar button, the menu item, *and* the key shortcut — one command object, three triggers, zero duplication. State-changing commands save a backup and return `true` so `executeCommand` pushes them onto `CommandHistory`; `Ctrl+Z` pops and calls `undo()`. The base `Button` class never changes; new operations are new command classes (OCP).

## Key Takeaways
1. A command encapsulates a request (receiver + method + args) as an object — pass it, store it, queue it, serialize it.
2. Senders depend only on the Command interface; new commands don't break senders (OCP).
3. The same command can be wired to multiple triggers (button, menu, shortcut), eliminating duplicated operation code.
4. Undo/redo: history stack of commands; each command saves state and knows how to undo itself.
5. Commands can be composed into macro commands; serialized for deferred/remote execution.
6. Cons: an extra layer between sender and receiver; snapshot undo is hard with private state (pair with Memento) and RAM-heavy.

## Connects To
- **ch17/20/22**: the four sender→receiver connectors; Command is the fixed unidirectional one.
- **ch21 Memento**: pair Memento (save state) with Command (perform op + undo) for undo.
- **ch24 Strategy**: same "parameterize with an action" look, different intent — Command = convert any op into an object (defer/queue/undo); Strategy = different ways to do *one* thing, swappable in a context.
- **ch08 Prototype**: clone copies of commands for history.
- **ch26 Visitor**: Visitor is a "powerful Command" operating over objects of many classes.