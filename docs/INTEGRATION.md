# Integrating Asgard into a Butler

This guide describes **the API implemented now**, then clearly marks future integrations. The Butler owns its identity and all sensitive runtime configuration. Asgard provides a neutral, per-instance ingress boundary, not a new plugin system.

## 1. Install the package

Python **3.12+**. Build from a trusted private checkout or consume a versioned wheel in a dedicated test environment:

```sh
python -m build --wheel --sdist
python -m pip install --no-deps dist/butler_asgard-0.1.0-py3-none-any.whl
```

This package is **not necessarily published to PyPI**. A GitHub Public Alpha release, once verified, is not a PyPI distribution or a promise of stable APIs. Production use requires consumer-specific integration, review and verification; Alfred's private adoption of the earlier development revision is evidence for Alfred only.

## 2. Where to configure the name, aliases and image

**The concrete Butler runtime is the only identity authority.** Recommended *host layout convention*, not a mandatory Asgard file loader:

```text
my-butler/
  config/
    identity.toml         # OPTIONAL host-owned configuration
  assets/
    profile.png           # RECOMMENDED owner-supplied picture name
  src/my_butler/
    identity.py           # owner resolves and validates configuration
    composition.py        # owner constructs AsgardBoundary
    runtime.py            # owner handles goals and policy
```

Use **`assets/profile.png`** for a default picture in each Butler installation. The identical filename is safe because files live in **separate instance roots**. Asgard never discovers or reads this file automatically. A caller must resolve an owner-controlled asset reference and eventually project safe bytes at its own presentation adapter. **Do not send an absolute local path in a public manifest.**

Suggested future host-owned TOML layout, **not currently parsed by Asgard**:

```toml
[identity]
canonical_name = "Example Butler"
aliases = ["Example", "EB"]
description = "Example personal Butler"
profile_picture = "assets/profile.png"
```

For the **currently implemented API**, inject `ButlerIdentity` into the instance directly:

```python
from butler_asgard import ButlerIdentity

identity = ButlerIdentity(
    canonical_name="Example Butler",
    aliases=("Example", "EB"),
    description="Example personal Butler",
    profile_picture="assets/profile.png",
)
```

`canonical_name` is the authoritative response name. `aliases` are exact addressing synonyms. They cannot be blank or duplicates of each other or the canonical name after `strip().casefold()`. Aliases are **not** global Midgard routing configuration. A conflict between two Butler instances must be resolved by Midgard as ambiguous, not by picking a default.

### Alfred (current private implementation)

Alfred retains authority for its own identity and compatibility ingress. On 2026-10-10 it adopted the pinned standalone Asgard package behind that compatibility boundary, with green CI, a healthy server deployment, and an Android Interphone request/reply observed. This private consumer proof does not certify other Butler instances or a public Asgard release.

Do not copy Alfred configuration, assets, source code, personal aliases or private endpoints into a public Asgard distribution.

### Wilfred / Manfred (current implementation)

Public Wilfred supports `[identity] name` and `locale` via TOML, and the `WILFRED_NAME` environment override. `WilfredRuntime(identity=wilfred.config.ButlerIdentity(name=...))` and its status tool use that concrete instance name (WILF-074). Example for a second test instance:

```toml
[identity]
name = "Manfred"
locale = "en"

[runtime]
log_level = "INFO"
```

**Current Wilfred `main`:** the identity parser supports `name`, `locale`, `aliases`, `description` and a validated relative `profile_picture` reference (WILF-076). The host configuration uses `name`, not the Asgard example's `canonical_name`, and Wilfred does not automatically instantiate or register Asgard. Manfred is a *separate deployment of Wilfred*, not a product fork or separately versioned Butler library. These development-line capabilities do not retroactively alter released Wilfred baselines.

## 3. Supply a governed executor

```python
from butler_asgard import AsgardBoundary, RequestEnvelope

async def execute(request: RequestEnvelope) -> str:
    # Your concrete Butler MUST enforce auth, policy, permission,
    # confirmation and action verification at its owning layer.
    # This is a harmless example, not an execution engine.
    return f"Echo: {request.message}"

asgard = AsgardBoundary(
    identity=identity,
    ingress=execute,
    availability=lambda: True,
)
```

`availability` must indicate the actual addressability of that concrete instance. It must not construct a missing runtime as a fallback. Asgard checks availability at request time and fails closed if unavailable. The synchronous callable itself does not define a process lifecycle or health supervisor.

## 4. Invoke the neutral boundary

```python
import asyncio
from butler_asgard import RequestEnvelope, SpeakerEnvelope

result = asyncio.run(asgard.handle(RequestEnvelope(
    request_id="req-123",
    message="hello",
    target_butler_name="EB",
    speaker=SpeakerEnvelope(speaker_id="local-example", language="en"),
)))

assert result.request_id == "req-123"
assert result.response == "Echo: hello"
assert result.source_butler_name == "Example Butler"
```

Speaker fields are **caller-provided context, not proof of identity**. Name matching is available through `asgard.matches_butler_name(" eb ")`; `handle()` does not itself select or validate cross-Butler targets. Only Midgard may select amongst Butler instances.

## 5. Connecting to Midgard and Bifröst (not yet implemented here)

The host-owned adapter must implement Midgard's `AsgardTarget` structural interface: `butler_name`, `nicknames`, `available`, `matches_butler_name(name)` and `async handle(MidgardRequest) -> MidgardResult`. Its conversion must preserve `request_id`, `message`, `target_butler_name` and the optional `speaker` fields without accidental loss; return a `MidgardResponse` with Asgard's canonical source identity.

The current Asgard handler returns its **own** `ResponseEnvelope`, not a `MidgardResult`, so you **cannot** pass an `AsgardBoundary` directly into `MidgardRouter`. The adapter and its routing tests are tracked in ASG-003. Midgard owns ambiguous/unknown/unavailable/correlation/source-identity errors. Bifröst owns transport serialization and presentation.

## 6. Profile image publication (planned)

Currently, `profile_picture="assets/profile.png"` is a reference. It is **not automatically exposed to clients**.

The planned path is:

```text
Butler-local assets/profile.png
  -> host validates asset and size/type, reads bytes
  -> host builds bounded data:image/png;base64,... metadata
  -> Midgard manifest passes metadata unchanged [MID-009]
  -> Bifröst serializes optional field [BIF-015]
  -> client displays its picture
```

Recommended filename: **`assets/profile.png`**, owned separately by each Butler. PNG is the expected first supported format. A missing/invalid image should produce *no picture*, never make the Butler unroutable. Never expose a private path or accept arbitrary remote fetches. Treat future size and byte limits as a required implementation/test decision, not a limit already enforced today. See ASG-002, MID-009, BIF-015, ALF-217.

## 7. Verification checklist

Before adoption: test exact canonical/alias matching, empty and duplicate aliases, per-instance independence, canonical source identity, request-ID integrity, unavailable executor not called, caller context preserved, policy/confirmation not bypassed, and real Midgard adapter errors. Build and test the wheel in a clean Python environment, then prove a real consumer in isolation; verify production changes via READ -> ACTION -> READ -> VERIFY.

Run `python examples/basic_butler.py` to exercise the standalone API without Midgard, HTTP, network, private credentials or a live Butler.
