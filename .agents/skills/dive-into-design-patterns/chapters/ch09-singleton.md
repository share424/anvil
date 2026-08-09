# Chapter 9: Singleton

## Core Idea
Guarantee a class has exactly one instance and provide a global access point to it. Private constructor + a static `getInstance()` that creates the instance on first call (lazy) and returns the cached one thereafter.

## Frameworks Introduced
- **Singleton** — creational pattern.
  - When to use: when exactly one instance of a class must be shared across clients (a single DB connection, a single config); as a safer alternative to a bare global variable.
  - How: add a private static instance field; make the constructor private; expose a public static `getInstance()` doing lazy init (with thread-safety) and returning the cached instance.

## Key Concepts
- **Single instance**: control access to a shared resource (DB, file).
- **Global access point**: like a global variable but protected from overwrite.
- **Lazy initialization**: create only on first `getInstance()` call, not at class load.
- **Private constructor**: blocks `new` from outside; only the static method can call it.
- **Thread safety**: double-checked locking needed so concurrent threads don't create multiple instances.
- **SRP violation (acknowledged)**: Singleton solves two problems at once (uniqueness + global access) — a documented trade-off.

## Mental Models
- Real-world analogy: a country has one official government; "The Government of X" is the global access point regardless of who's in it.
- The client never knows it's getting the same object back; `foo` and `bar` from two `getInstance()` calls are identical.

## Anti-patterns
- **Singleton masking bad design**: components reach for the global instance instead of receiving dependencies → tight hidden coupling.
- **Forgetting thread safety**: in a multithreaded app naïve lazy init can produce several instances.
- **Hard to unit-test**: private constructor + static method defeats most mock frameworks that rely on inheritance; "you'll need a creative way to mock it — or don't use Singleton."
- **Using it where a plain dependency would do**: prefer injecting a normal instance unless true uniqueness/global access is required.

## Code Examples
Thread-safe database singleton with double-checked locking:
```pseudo
class Database is
  private static field instance: Database
  private constructor Database() is
    // connect to the database server...

  public static method getInstance() is
    if (Database.instance == null) then
      acquireThreadLock() and then
        if (Database.instance == null) then   // re-check after acquiring lock
          Database.instance = new Database()
    return Database.instance

  public method query(sql) is
    // all app queries route here — throttling/caching hook

// client
Database foo = Database.getInstance()
foo.query("SELECT ...")
Database bar = Database.getInstance()   // bar IS foo
```
- **What it demonstrates**: `getInstance()` is the only entry; the double `null` check + lock prevents duplicate creation under concurrency.

## Reference Tables
Implementation checklist:

| Step | Action |
|---|---|
| 1 | Add a private static field for the instance |
| 2 | Declare a public static creation method (`getInstance`) |
| 3 | Lazy-init: create on first call, cache, return cached thereafter |
| 4 | Make the constructor private |
| 5 | Replace all `new Singleton()` calls with `getInstance()` |

When your "singleton" only needs one of the two properties, ask which one you really need.

## Worked Example
An app wants all queries throttled through one database connection Object. Without Singleton, each module opens its own connection (resource explosion) or shares a mutable global variable (anyone can overwrite it). With Singleton, `Database.getInstance()` returns the one cached connection; the private constructor prevents accidental `new Database()`, and `query()` is the single chokepoint where throttling/caching can be added. To allow N instances later, only the body of `getInstance()` changes.

## Key Takeaways
1. Singleton = one instance + global access — it intentionally violates SRP.
2. Lazy init: instance created on first request, not at load time.
3. Multi-threaded environments need double-checked locking.
4. The private constructor makes mocking hard; weigh that before adopting.
5. Don't let a Singleton camouflage over-coupled components.
6. Flyweight differs: many flyweight instances with different intrinsic state, and flyweights are immutable; a Singleton can be mutable.

## Connects To
- **ch06/7/8**: Abstract Factories, Builders, and Prototypes are commonly implemented *as* Singletons.
- **ch14 Facade**: a Facade class is often turned into a Singleton — one facade usually suffices.
- **ch15 Flyweight**: similar structure but many immutable shared objects vs. one mutable singleton.