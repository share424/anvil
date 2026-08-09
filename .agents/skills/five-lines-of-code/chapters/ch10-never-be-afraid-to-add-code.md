# Chapter 10: Never be afraid to add code

## Core Idea
Adding code is safer than modifying it, so fight "coding stage fright" with spikes, a fixed effort ratio, and modification-by-addition (extensibility, backward compatibility, feature toggles, branch by abstraction). Optimize for developer life, not perfect code.

## Frameworks Introduced
- **Enter the danger** (improvisational theater / Lencioni): confront the most uncertain area first — that's where the learning is. Deploy to production on day one to kill the fear.
- **Spikes as fear-killer**: the recommended workflow starts with a throwaway spike; spike code may never reach main, so flaws don't matter and fear dissipates. *Product is knowledge, not code* — codify the outcome as a slide/whitepaper so stakeholders see value.
- **Fixed 20% ratio** (DevOps Handbook): cap nonfunctional/support-tool time at ~20%; keeps support-tool complexity ≤ production-code complexity and stops pipeline-procrastination. Best implementation: reserved Fridays (a full day, low context-switch overhead).
- **Optimize for developer life**: minimize task→working; maximizes practice and feedback-loop speed; "improve faster than competitors and you overtake them."
- **Copy-and-paste velocity trade-off**: sharing code = high *global* behavior-change velocity but high fragility; duplicating = high *local* velocity, safe experimentation, low fragility. During a spike, duplicate freely; once settled, ask "should this be coupled? when this changes, should the source change? does my team own the unified code?" — if any answer is no, keep it separate.
- **Three-step variation workflow**: (1) duplicate, (2) work with/adapt it, (3) unify with the source if it makes sense.
- **Expand-Contract pattern** (DB migrations): expand (add new, safe) → migrate callers (longest) → contract (delete the old). Mirrors the three-step workflow.
- **Extensibility via addition**: REPLACE TYPE CODE WITH CLASSES and INTRODUCE STRATEGY PATTERN turn static control flow (`if`/`switch`) into dynamic method calls — add a class to add behavior. Postpone variation points until needed (accidental vs essential complexity).
- **Modification by addition for backward compatibility** (Microsoft/Raymond Chen): never change a public method — add a new one; duplicate → implement → unify; monitor the old; remove when usage is zero. Version only the outermost layer, in the entry-point names (avoid PHP's `mysql_escape_string`/`mysql_real_escape_string`/`mysqli_real_escape_string` mess).
- **Feature toggles** (primitive progression): `FeatureToggle` class → static flag returning `false` → wrap existing code in `if(flag){}else{}` → duplicate into the `if` → make changes → tie flag to an env var. Lets you integrate/deploy continuously; schedule toggle removal ≤6 weeks (remove `else` if on, `if` if off).
- **Branch by abstraction**: when a feature touches multiple sites, REPLACE TYPE CODE WITH CLASSES on the Boolean flag → return `Version1`/`Version2` classes implementing an interface → push the `if`s into the classes. Localizes the feature's invariants; removal = delete one class, delete the interface (NO INTERFACE WITH ONLY ONE IMPLEMENTATION), inline.

## Key Concepts
- **Coding stage fright** — productivity collapse from knowing all the ways code can be bad; fight it.
- **Psychological safety** (Google study) — biggest predictor of team productivity; courage is a Scrum value.
- **Accidental vs essential complexity** — essential = inherent to the domain; accidental = not representative of the domain (e.g. premature variation points). Refactoring targets accidental.
- **Deploy vs release** — feature toggles separate them; release becomes a business decision.
- **A/B testing** — tie rollout to a metric (Obama 2008: family photo + "Learn More" → ~40% better, ~$60M extra donations).
- **Knightmare** cautionary tale — repurposed stale flag + manual deploy + no kill switch → $400M lost in 45 min. Flags must not fester.
- **Backward compatibility** — "the safest thing to do in code is not to change anything"; Windows 95 code runs in Windows 10.

## Mental Models
- Adding > modifying: a new method/endpoint/class can't break existing callers; use addition to make changes safe.
- The product of a spike is knowledge (a slide), not code; never let spike code into production or spikes become production-fear.
- Duplicate to experiment, unify to expose structure — decide after the code settles, not before.
- If a feature touches many sites, an `if` per site spreads the invariant; a class localizes it (branch by abstraction).

## Anti-patterns
- **Pipeline-before-code**: building elaborate CI/feature-toggle/deploy tooling with no production code to push through it — procrastination dressed as progress.
- **Refactoring sprints / every-fifth-sprint**: too intensive, no feeling of progress, and four sprints of accruing tangle precede it; prefer reserved Fridays.
- **Using spike code in production**: signals the product is code, so spikes become scary; keep spikes throwaway.
- **Premature extensibility**: every variation point adds accidental complexity; introduce only when needed.
- **Changing a public method/API**: breaks callers; add a new one, deprecate the old, monitor, remove at zero usage.
- **Leaving feature flags in**: they're temporary `if`s (debt); festering flags caused Knight's loss. Schedule removal ≤6 weeks.
- **Per-site `if` for a multi-site feature**: spreads invariants; use branch by abstraction.

## Reference Tables

| Fear | Counter |
|---|---|
| Building the wrong thing | spike (product = knowledge) |
| Waste/risk | fixed 20% ratio; reserved Fridays |
| Imperfection / imposter | optimize for developer life; gradual improvement |
| Modifying existing code | modify by addition (new method/endpoint/class) |
| Integrating unfinished code | feature toggles (deploy ≠ release) |
| Multi-site feature `if`s | branch by abstraction |

## Key Takeaways
1. Adding code is safer than modifying it — use addition (new methods/classes/endpoints) as the default change mechanism.
2. Fight stage fright: enter the danger, spike first (product = knowledge, not code), deploy on day one.
3. Cap support-tool effort at ~20% (reserved Fridays) to stop pipeline-procrastination; optimize for developer life.
4. Duplicate to experiment, unify to expose structure — ask the three coupling questions before unifying.
5. Backward compatibility = never change a public surface, add a new one; version only the outermost layer, in names.
6. Feature toggles separate deploy from release; remove them ≤6 weeks; for multi-site features use branch by abstraction to localize invariants.

## Connects To
- **Ch 4/5**: REPLACE TYPE CODE WITH CLASSES and INTRODUCE STRATEGY PATTERN are the extensibility engines.
- **Ch 9**: spike-and-stabilize and the 6-week rule; deletion makes addition safe.
- **Ch 7**: NEVER USE IF WITH ELSE — feature-toggle `if`s are a tolerated, temporary exception; branch by abstraction removes them.
