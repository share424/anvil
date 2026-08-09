# Chapter 19: Iterator

## Core Idea
Extract a collection's traversal behavior into a separate **iterator** object that tracks its own progress and exposes `getNext()`/`hasMore()`. Clients traverse any collection uniformly without knowing its underlying structure, and several iterators can walk the same collection independently.

## Frameworks Introduced
- **Iterator** — behavioral pattern.
  - When to use: hide a collection's complex internal structure; cut duplicated traversal code; let code traverse varied/unknown data structures via a common interface.
  - How: declare an Iterator interface (`getNext`, `hasMore`, optionally `getPrev`/`reset`); declare a Collection interface with a method returning the Iterator interface; Concrete Iterators run a specific algorithm and carry their own position state; Concrete Collections hand the iterator a reference to themselves.

## Key Concepts
- **Iterator**: encapsulates the traversal algorithm *and* its state (position, remaining count).
- **Independent traversal**: each iterator holds its own state → many iterators over one collection at once; iteration can be paused and resumed.
- **Collection interface**: returns iterators typed as the Iterator interface so collections can return varied iterators without coupling clients.
- **Same interface, many algorithms**: depth-first, breadth-first, friends-only, coworkers-only — all implement `getNext()`/`hasMore()`.
- **Hiding internals / security**: pass an iterator (not the collection) to a client so it can read elements without careless/malicious mutation.
- **Lazy init**: the iterator can fetch elements on demand (e.g. an API page).

## Mental Models
- Real-world analogy: ways to tour Rome — random wandering, smartphone navigator, or human guide. Each is an "iterator" over the same collection of sights, with different traversal logic.
- A tree doesn't have to be traversed one fixed way; ask it for a depth-first iterator today and a breadth-first iterator tomorrow — the tree class never gains traversal methods.

## Anti-patterns
- **Burying traversal algorithms inside the collection class**: blurs the collection's real job (efficient storage), bloats it, and couples generic collections to app-specific traversals.
- **Coupling client code to specific collections**: because each collection exposes access differently, clients end up bound to concrete classes — solved by the shared iterator interface.
- **Using Iterator for simple collections/direct access**: it can be overkill and even slower than a direct loop (the documented cons).

## Code Examples
Social-network profile iterators with lazy fetch:
```pseudo
interface ProfileIterator is
  method getNext():Profile
  method hasMore():bool

interface SocialNetwork is
  method createFriendsIterator(profileId):ProfileIterator
  method createCoworkersIterator(profileId):ProfileIterator

class Facebook implements SocialNetwork is
  method createFriendsIterator(profileId) is
    return new FacebookIterator(this, profileId, "friends")
  method createCoworkersIterator(profileId) is
    return new FacebookIterator(this, profileId, "coworkers")

class FacebookIterator implements ProfileIterator is
  private field facebook: Facebook; profileId, type: string
  private field currentPosition; cache: array of Profile
  private method lazyInit() is
    if (cache == null)  cache = facebook.socialGraphRequest(profileId, type)
  method getNext() is
    if (hasMore())  result = cache[currentPosition]; currentPosition++; return result
  method hasMore() is  lazyInit(); return currentPosition < cache.length

// client works against interfaces — swap Facebook -> LinkedIn with no change
iterator = network.createFriendsIterator(profile.getId())
while (iterator.hasMore())
  System.sendEmail(iterator.getNext().getEmail(), message)
```
- **What it demonstrates**: `SocialSpammer.send(iterator, msg)` walks friends or coworkers of any network through the same two-method interface; the iterator's lazy `socialGraphRequest` keeps the REST/auth detail out of the client and out of the collection.

## Reference Tables
| Role | Responsibility |
|---|---|
| Iterator interface | `getNext`, `hasMore` (+ optional prev/reset) |
| Concrete Iterator | specific algorithm; owns position/state; linked to one collection |
| Collection interface | factory returning the Iterator interface |
| Concrete Collection | hands itself to the iterator; may offer several iterator types |
| Client | talks to interfaces only; gets iterators from collections |

## Worked Example
A profile-spamming tool needs to message friends of a profile and coworkers of a profile across different networks. Without iterators it would be tangled with per-network auth, REST calls, pagination, and traversal quirks inside business logic. With Iterator: `Facebook.createFriendsIterator(id)` returns a `ProfileIterator` that lazily calls `socialGraphRequest`, caches results, and exposes only `getNext/hasMore`. `SocialSpammer.send` takes the iterator and loops identically for friends or coworkers, Facebook or LinkedIn (just swap the `network` instance). New network = new collection + iterator classes; nothing else changes (OCP).

## Key Takeaways
1. Pull the traversal algorithm out of the collection into an iterator that owns its own state.
2. Clients depend on a tiny `getNext/hasMore` interface, not on the collection's concrete structure.
3. Several iterators can walk the same collection in parallel, and iteration can be paused/resumed.
4. New traversal strategies are new iterator classes — the collection and clients don't change (OCP).
5. Passing an iterator (not the collection) protects the collection from being mutated by the client.
6. Cons: overkill for simple collections; may be slower than direct access.

## Connects To
- **ch12 Composite**: use iterators to traverse Composite trees.
- **ch05 Factory Method**: pair with Iterator so collection subclasses return compatible iterator types.
- **ch21 Memento**: pair with Iterator to snapshot current iteration position and roll back if needed.
- **ch26 Visitor**: pair Iterator + Visitor to run an operation over a complex structure of differing classes.