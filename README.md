# Butler Asgard 🎩

**One Butler-owned ingress boundary. Many independently named Butlers.**

Asgard is the reusable, framework-neutral boundary where a concrete Butler exposes its identity and receives a request. A Butler supplies an immutable identity, an asynchronous request handler and an availability probe. Asgard provides exact alias matching, correlation and canonical source attribution.

> **Status: private integration baseline (0.1.0.dev0).** Standalone package build, clean-install smoke test and neutral CI pass. Production adoption by Alfred and a second Wilfred-based Butler, image delivery and Midgard adapter are **not yet proven**. No public release has been made.

```text
External client -> Bifröst (transport) -> Midgard (select a Butler)
                                           |
                                   Butler-owned Asgard
                                           |
                                  concrete Butler runtime
                                           |
                              Core policy / owned capabilities
```

## A working first example

After installing a built wheel into a **test environment**:

```python
import asyncio
from butler_asgard import AsgardBoundary, ButlerIdentity, RequestEnvelope

async def execute(request: RequestEnvelope) -> str:
    return f"Received: {request.message}"

asgard = AsgardBoundary(
    identity=ButlerIdentity(
        canonical_name="Example Butler",
        aliases=("Example",),
        description="An independently configured Butler.",
        profile_picture="assets/profile.png",
    ),
    ingress=execute,
    availability=lambda: True,
)

response = asyncio.run(asgard.handle(
    RequestEnvelope(request_id="demo-1", message="hello")
))
assert response.source_butler_name == "Example Butler"
assert response.request_id == "demo-1"
```

The picture here is a **Butler-owned reference only**. The present Asgard package neither loads the file nor exposes it to clients.

## Start here

- **[Integrate Asgard into a Butler](docs/INTEGRATION.md)**: wheel installation, `assets/profile.png`, canonical name and aliases, request handler and runnable example.
- **[Architecture & boundaries](docs/ARCHITECTURE.md)**: precise ownership, lifecycle, security, error and transport rules.
- **[Publication readiness](docs/PUBLICATION.md)**: maturity, public extraction criteria, unresolved work and release gates.
- [Request and speaker context](docs/REQUEST_CONTEXT.md): optional context fields and ownership.
- [History provenance](docs/PROVENANCE.md): private-only Git history mappings. **Never copy this historical document into a public repo without review.**

## What is available now

- Immutable `ButlerIdentity(canonical_name, aliases, description, profile_picture)` injected by each Butler.
- Exact `strip().casefold()` target matching, including owner-defined aliases. No fuzzy target selection.
- An independently instantiated `AsgardBoundary(identity, ingress, availability)`.
- Async `handle(RequestEnvelope)` producing `ResponseEnvelope` with original request ID and canonical source name.
- Optional target name and speaker context in `RequestEnvelope`; speaker metadata is not an authorization credential.
- Wheel/sdist build and isolated-wheel smoke testing on Python 3.12 / 3.13.

## What Asgard does not do

Asgard is **not** a Wilfred tool/domain/capability plugin and does not register tools or discover external providers. It does **not** perform cross-Butler routing, authentication, permission checks, confirmations, home automation, image loading, HTTP, or client rendering. These belong to their owning components and concrete hosts.

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m build --wheel --sdist
python examples/basic_butler.py
```

Use the canonical environment of your consumer; installing a wheel is not runtime activation. Do not install or change a running Alfred/HA service as part of documentation proving.

License: Apache-2.0. This repository is currently private. Documentation is drafted for a future publication decision, **not** authorization to make history or private implementation public.
