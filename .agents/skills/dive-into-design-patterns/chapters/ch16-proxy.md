# Chapter 16: Proxy

## Core Idea
Provide a **substitute** for a service object with the *same interface*, controlling access and doing work **before or after** delegating to the real service — lazy init, access control, logging, caching, remote calls — without clients or the service knowing.

## Frameworks Introduced
- **Proxy** — structural pattern.
  - When to use: you need lazy/protection/remote/logging/caching/smart-reference behavior around a service whose interface you can mirror.
  - How: declare a Service Interface; the real Service and the Proxy both implement it; the Proxy holds a reference to the service (usually creates and manages its lifecycle) and delegates after its own processing.

## Key Concepts
- **Service Interface**: the proxy must mirror it to "disguise" itself as the service.
- **Service**: the real object providing the business logic.
- **Proxy**: references the service, does its own work (lazy creation, access check, cache lookup, log, network hop), then forwards.
- **Lifecycle ownership**: a proxy usually *creates and manages* its service — the key difference from Decorator, whose composition is client-controlled.
- **Kinds of proxy** (the book enumerates): **Virtual** (lazy init), **Protection** (access control), **Remote** (network to a server), **Logging**, **Caching**, **Smart Reference** (reference tracking / dismissal).
- **Same interface**: a proxy is interchangeable with the service in client code (unlike Facade, which is a different interface).

## Mental Models
- Real-world analogy: a credit card proxies a bank account which proxies a bundle of cash — all share a "make a payment" interface; you carry the card, not the cash.
- You can pass a proxy anywhere a service is expected; nothing in client code changes — the disguise is total.

## Anti-patterns
- **Solving discovery/initialization with client-side boilerplate**: duplicating lazy-init code in every client — push it into a proxy once.
- **Adding behavior by editing the service class**: often impossible (closed library / `final`); wrap it instead.
- **Confusing Proxy with Decorator**: same structure, but Decorator composes client-driven stacks to extend behavior; Proxy self-manages the service for access/control.
- **Confusing Proxy with Facade**: Facade buffers a *subsystem* with a *new* interface; Proxy buffers *one service* with the *same* interface.

## Code Examples
Caching proxy around a YouTube library:
```pseudo
interface ThirdPartyYouTubeLib is
  method listVideos()
  method getVideoInfo(id)
  method downloadVideo(id)

class ThirdPartyYouTubeClass implements ThirdPartyYouTubeLib is   // the real (slow) service
  method listVideos() is       // send API request to YouTube
  method getVideoInfo(id) is   // fetch metadata
  method downloadVideo(id) is  // download the file

class CachedYouTubeClass implements ThirdPartyYouTubeLib is       // the PROXY
  private field service: ThirdPartyYouTubeLib
  private field listCache, videoCache
  field needReset
  constructor CachedYouTubeClass(service) is  this.service = service
  method listVideos() is
    if (listCache == null || needReset)  listCache = service.listVideos()
    return listCache
  method getVideoInfo(id) is
    if (videoCache == null || needReset) videoCache = service.getVideoInfo(id)
    return videoCache
  method downloadVideo(id) is
    if (!downloadExists(id) || needReset)  service.downloadVideo(id)

class YouTubeManager is                       // client — unchanged, works through interface
  protected field service: ThirdPartyYouTubeLib
  constructor YouTubeManager(service) is  this.service = service
  method renderVideoPage(id) is  info = service.getVideoInfo(id)   // ...

// app wires the proxy in front of the real service
aYouTubeService = new ThirdPartyYouTubeClass()
aYouTubeProxy = new CachedYouTubeClass(aYouTubeService)
manager = new YouTubeManager(aYouTubeProxy)    // client receives a proxy as if it were the service
```
- **What it demonstrates**: `YouTubeManager` is unchanged — it just got a `CachedYouTubeClass` where it once got `ThirdPartyYouTubeClass`; repeated calls hit the proxy's cache, not YouTube.

## Reference Tables
The proxy taxonomy (use-cases):

| Proxy type | Purpose |
|---|---|
| Virtual | lazy initialization of a heavyweight object |
| Protection | access control — pass request only if credentials match |
| Remote | local facade for a server-side object; hides networking |
| Logging | record each request before forwarding |
| Caching | cache results; request params as cache keys |
| Smart Reference | track references; dismiss the object when none remain |

Proxy vs. Decorator vs. Facade (the book's framing):

| Pattern | Interface vs. service | Wraps | Composition controlled by |
|---|---|---|---|
| **Proxy** | same | one service | the proxy itself (lifecycle) |
| Decorator | same / enhanced | the target | the client |
| Facade | new | a subsystem | the facade |

## Worked Example
A `ThirdPartyYouTubeClass` re-downloads the same video on every call — wasteful and uncacheable from outside (closed/`final`). Insert `CachedYouTubeClass` implementing `ThirdPartyYouTubeLib`: it caches `listVideos`/`getVideoInfo`/`downloadVideo` results and forwards to the real service only on a miss or a reset. The GUI manager that used the real class directly keeps working unchanged — pass it the proxy via the shared interface. Same shape solves lazy init for a DB connection (`VirtualProxy` lazily instantiates `RealDatabase` on first query), protection (`ProtectionProxy` checks the caller's role), or remote (`RemoteProxy` marshals calls over the network).

## Key Takeaways
1. A proxy mirrors the service interface so it's interchangeable — clients don't change.
2. It does work *before/after* delegating: lazy create, access-check, log, cache, remote-hop, reference-track.
3. Proxies typically own the service's lifecycle; Decorator stacks don't.
4. If no service interface exists, extract one — otherwise make the proxy a *subclass* of the service to inherit the interface.
5. Cons: more classes; a request may be delayed (e.g. lazy creation).
6. Same interface but the buffer + self-initialization is exactly what separates Proxy from Decorator (client-driven, enhanced) and Facade (new interface, whole subsystem).

## Connects To
- **ch13 Decorator**: same structure, different intent + lifecycle ownership.
- **ch14 Facade**: both buffer a complex entity and self-init; Facade uses a different interface (not interchangeable), Proxy uses the same.
- **ch10 Adapter**: Adapter = different interface to one object; Proxy = same interface.
- **ch19**: itself null — but proxies and **Iterator** often co-exist for lazy traversal over remote/virtual collections.