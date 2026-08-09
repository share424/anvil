# AGENTS.md — anvil

Config-driven deep learning experiment framework (PyTorch + Lightning).

One YAML or typed blueprint = one experiment = one reproducible forge.
CLI and notebooks / Colab share one path: `anvil.forge(...)`.

**Install:** `anvil` = core only; `anvil[stock]`; `anvil[blueprints]` (includes stock);
`anvil[export]` (ONNX); `anvil[all]` (beartype + ONNX).

## Explicit over implicit

**Always prefer explicit over implicit whenever possible.**

- `_target_` is always a **fully-qualified dotted path** to a pydantic config
  class — never a short registered name, never a runtime `nn.Module` class.
- No registries that resolve magic strings by import order.
- No bare class-level defaults that construct modules at import time — use
  `Field(default_factory=...)`.
- No silent lifting / popping of config keys; declare fields on the owning type.
- Live `nn.Module` in a slot is allowed only as a loud escape hatch (run marked
  non-reproducible; resume refused). Do not make it the default path.

If a reader must know framework internals to understand which class a config
refers to, that is a design bug.

## Architecture — core / stock / blueprints

| Package | Metaphor | Role |
|---------|----------|------|
| **`anvil.core`** | the anvil | Frozen framework: `Buildable`, parse, `Task`/`Net`, runtime, `forge` / `resume` / `validate` / `test` / `export`, CLI |
| **`anvil.stock`** | material | Batteries-included: `components`, `data`, `tasks`, `metrics`, `callbacks` |
| **`anvil.blueprints`** | recipes | Ready-to-forge experiments that pin stock into concrete combos |

`anvil.core` stays small and frozen. Stock and blueprints grow forever.

**Boundary (keep green):**

- `anvil.core` → never imports stock or blueprints
- `anvil.stock` → may import core; never imports blueprints
- `anvil.blueprints` → may import core and stock
- `nn.Module` impl modules → never import `anvil`

### Config: pydantic is canonical

```text
YAML / dict / Python  →  pydantic (validated)  →  build()  →  objects
```

- **Python:** `backbone=ResNet18(pretrained=True)` — no `__target__`, no `_partial_`.
- **YAML:** `_target_: anvil.stock.components.backbones.ResNet18` + pydantic fields.
- Configs named after what they build (`ResNet18`, not `ResNet18Config`).
- Slots hold configs that `.build()` to `nn.Module`, not live modules.

### Task owns architecture + data

A stock task declares architecture slots and the batch type its data must produce.
Blueprints pin combos with `default_factory`:

```python
from anvil.blueprints import ResNet18Classification
import anvil

anvil.forge(ResNet18Classification())
# anvil forge configs/resnet18_cifar10.yaml
# anvil resume cifar/resnet18_baseline
# anvil export CONFIG --ckpt last.ckpt --out model.onnx
```

## Invariants

- **P1 — Model ≠ Task.** Pure `nn.Module` vs loss/metrics/`step(net, batch, stage)`.
- **P2 — Impl modules import no `anvil`.** Stock specs may import `anvil.core`.
- **P3 — Pydantic is the source of truth.** No path into training skips validation.
- **P4 — Fail at build time.** Wiring + batch contract at parse; meta-device + smoke after `build()`.
- **P5 — Task owns both contracts.** Architecture slots + batch type.
- **P6 — Nothing constructed before the seed.** Only `build()` after `seed_everything()`.
- **P7 — Core is frozen.** No experiment-specific branches in `anvil.core`.
- **P8 — One code path for CLI and notebooks.**
- Errors name the dotted config path + value + hint. Type hints on every public API.
- Prefer `Buildable` / `BaseModel` over untyped dicts once the framework owns a shape.
- **Docstrings:** Google style on public APIs (`ruff` `D` + `convention = "google"`).
  Tests keep Condition/Expected (D ignored under `tests/`).

## Workflow (every change)

1. Read first — this file and the existing code are the source of truth.
2. Ponytail ladder — top rung that holds; mark shortcuts with `# ponytail:`.
3. Skills — `five-lines-of-code`, `dive-into-design-patterns` when they bite.
4. Green to green after every non-trivial edit (commands below).
5. Never simplify away trust-boundary validation or data-loss prevention.

```bash
uv sync --group dev
uv run ruff check --fix .
uv run ruff format --check .
uv run ty check
uv run pytest tests/
```

## Skills

- `.agents/skills/five-lines-of-code`
- `.agents/skills/dive-into-design-patterns`
