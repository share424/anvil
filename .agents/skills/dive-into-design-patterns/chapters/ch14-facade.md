# Chapter 14: Facade

## Core Idea
Provide a single, simplified interface to a complex subsystem (library/framework/many classes). The facade knows which subsystem objects to call and in what order; clients talk only to the facade, decoupling them from the subsystem's moving parts.

## Frameworks Introduced
- **Facade** — structural pattern.
  - When to use: you need a limited but straightforward interface to a complex subsystem; you want to structure a subsystem into layers (facades as layer entry points); subsystems should communicate only through facades.
  - How: declare the simplified interface on a new facade class; the facade initializes the subsystem parts, calls them in the right order, and returns the result; route all client traffic through the facade so subsystem churn is contained to the facade.

## Key Concepts
- **Complex Subsystem**: dozens of interrelated objects requiring careful initialization and ordering. Subsystem objects don't know the facade exists — they communicate directly.
- **Facade**: convenient access to a slice of the subsystem's functionality; only what clients care about.
- **Additional Facade**: split a bloating facade so it doesn't itself become a god object; usable by clients and other facades.
- **No new functionality**: the facade *re-presents* existing behavior; it adds no new feature (contrast with Mediator, which centralizes new communication).
- **Swap-isolation benefit**: upgrade/replace the underlying framework and you only rewrite the facade.

## Mental Models
- Real-world analogy: a shop phone operator is your facade to the ordering system, payment gateway, and delivery services — one number, one simple voice interface.
- Trade-off: limited functionality vs. simplicity — a cat-video app uses a pro video library but exposes only `encode(filename, format)`.

## Anti-patterns
- **God-object facade**: one facade coupled to every class in the app — the documented con; mitigate with Additional Facades.
- **Client code reaching past the facade**: bypassing the facade re-couples it to subsystem internals, defeating the isolation benefit.
- **Confusing Facade with Adapter**: Adapter makes one existing interface *usable* (wraps one object); Facade defines a *new* interface to a whole subsystem.

## Code Examples
Video converter facade hiding a 3rd-party framework:
```pseudo
class VideoConverter is                       // the Facade
  method convert(filename, format):File is
    file = new VideoFile(filename)
    sourceCodec = (new CodecFactory).extract(file)
    if (format == "mp4")  destinationCodec = new MPEG4CompressionCodec()
    else                  destinationCodec = new OggCompressionCodec()
    buffer = BitrateReader.read(filename, sourceCodec)
    result = BitrateReader.convert(buffer, destinationCodec)
    result = (new AudioMixer()).fix(result)
    return new File(result)

class Application is                          // client
  method main() is
    convertor = new VideoConverter()
    mp4 = convertor.convert("funny-cats-video.ogg", "mp4")
    mp4.save()
```
- **What it demonstrates**: the app depends on one `VideoConverter` instead of `VideoFile`, `CodecFactory`, `MPEG4CompressionCodec`, `BitrateReader`, `AudioMixer`, etc. Swapping the framework tomorrow means rewriting only the facade's `convert`.

## Reference Tables
Facade vs. its look-alikes:

| Pattern | Interface | Wraps | New functionality? |
|---|---|---|---|
| **Facade** | new, simplified | whole subsystem | no |
| Adapter | existing, made usable | usually one object | — |
| Mediator | (centralizes comm.) | components | yes (new comm.) |
| Proxy | same as service | one service | — |

When to split: a second facade the moment the first grows unrelated features.

## Worked Example
A cat-video uploader wants to use FFmpeg-style machinery (codecs, bitrate readers, audio mixers) but only ever calls `convert(name, "mp4")`. The `VideoConverter` facade orchestrates `CodecFactory` → `BitrateReader.read` → `BitrateReader.convert` → `AudioMixer.fix` → wrap in `File`, hiding the dance. Later you switch from the Ogg-leaning framework to an H.264 one: edit `VideoConverter.convert` only; the app keeps calling `convertor.convert(...)` unchanged.

## Key Takeaways
1. A facade is a one-stop, simplified front door to a complex subsystem — functionality vs. simplicity trade-off.
2. The subsystem doesn't know the facade; objects inside it still talk to each other directly.
3. Routing all client traffic through the facade isolates you from subsystem upgrades.
4. Split into Additional Facades before one facade becomes a god object.
5. Facade defines a *new* interface and adds *no* behavior; Adapter makes one existing interface usable; Mediator introduces new centralized communication.

## Connects To
- **ch10 Adapter**: Adapter = one object, different interface; Facade = whole subsystem, new simplified interface.
- **ch06 Abstract Factory**: AF can substitute for a Facade when you only want to hide how subsystem objects are *created*.
- **ch15 Flyweight**: Flyweight makes many small objects; Facade makes one object representing a subsystem.
- **ch16 Proxy / ch13 Decorator**: same "buffer a complex entity" idea; Proxy shares the service's interface (interchangeable); Facade does not.
- **ch20 Mediator**: similar job — organizing collaboration — but Mediator centralizes *new* communication and components only know the mediator.
- **ch09 Singleton**: a facade class is commonly made a Singleton.