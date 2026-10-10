# Architecture and ownership boundaries

This document describes the **intended invariant** and the **present implementation** of Butler Asgard. It is normative for future Asgard changes; where a capability is not implemented yet it is marked explicitly.

## Responsibility map

| Component | Owns | Must never own |
| --- | --- | --- |
| Concrete Butler runtime | Canonical name, aliases, description, local profile asset, runtime instance, domain execution and policy | Global routing for other Butlers |
| **Asgard (Butler-owned)** | Projection of the supplied identity; exact matching; addressability probe; neutral ingress request correlation; canonical response source | A second identity store; runtime construction; external authentication; cross-Butler selection; domain tools |
| **Midgard** | Selecting among visible Asgards; unknown/ambiguous/unavailable targets; channel semantics; routing errors, correlation/source checks | Concrete Butler identity definitions; reading local profile images |
| **Bifröst** | Client-facing protocol and transport adapters, request/manifest serialization | Butler execution; image filesystem access; selecting a substitute Butler |
| **Butler Core** | Provider-neutral execution contracts, permissions, confirmation, traces and policy | Concrete Asgard runtime, Butler-specific personality or frontend |
| Client / Hermes frontend | UI, speech and delivery presentation | Authorization to execute a Butler operation merely by naming it |

### Request path

```text
Client / voice / app
     |
  Bifröst               transport authentication, protocol
     |
  Midgard               target selection, ambiguity, routing failures
     |
  host composition      explicit Midgard <-> Asgard envelope adapter
     |
  Butler-owned Asgard   injected identity, availability, correlation
     |
  Butler runtime        activation, domain policy, permission, confirmations
     |
  capabilities/tools    authenticated and verified operations
```

No automatic fallback target is allowed. External command delivery is not authorization. Source name in a successful Asgard response is always the **owner-supplied canonical name**, never an alias or arbitrary executor-provided field.

## What an Asgard instance is

`AsgardBoundary(identity, ingress, availability)` is a **per-Butler object**. It is not a process supervisor, a global registry, a provider connection or a `wilfred.plugins.PluginDefinition`. It does not discover Python wheels using entry points. Installation/discovery/activation are different concepts and their composition is a host concern.

A concrete runtime must exist when its ingress is invoked. During startup, shutdown or suspension `availability` is expected to return `False`. Asgard raises `RuntimeError` if its availability probe is false; it does not launch a Butler or choose another. A host adapter/Midgard is responsible for translating failures into client-safe structured errors.

A frozen Asgard object is **not** a concurrency or lifecycle guarantee. Its injected executor can have mutable state: that state, async safety, cancellation, task supervision and cleanup remain the runtime owner's job.

## Identity and target resolution

The concrete Butler supplies `ButlerIdentity(canonical_name, aliases, description, profile_picture)`. Intra-instance matching uses exact `strip().casefold()`, not fuzzy matching, phonetics, voice intent guessing or regex. A canonical name and aliases must be unique within one identity. Collision across **different** Butler identities is for Midgard to mark ambiguous.

Current `RequestEnvelope`: `request_id`, `message`, optional `target_butler_name`, optional `SpeakerEnvelope(speaker_id, persistent, call_me, language)`.

`ResponseEnvelope`: `request_id`, `response`, `source_butler_name`. Asgard preserves input correlation and supplies the canonical source. It does **not** itself verify that the `target_butler_name` matches its own identity; host/Midgard must resolve the target first.

The current executor contract returns a `str`. A non-string executor result causes `TypeError`; a missing runtime causes `RuntimeError`. Asgard does not currently define a stable structured error envelope, HTTP status, retry semantics or deadlines. Do not describe these as available functionality.

## Security and policy

- A supplied `SpeakerEnvelope` is **metadata**, not authentication, user identity proof or permission.
- A successful match for `target_butler_name` grants **no execution rights**.
- The host authenticates and validates external requests. Runtime/Core enforce READ/ACTION/DANGEROUS policy and confirmation. Post-action state must be observed and verified separately.
- No secret, personal state, private endpoint, absolute path, API token, acquisition implementation or file contents belongs in a public manifest.
- An optional picture can be displayed only after the host verifies an owner-controlled file and converts it to **client-safe** bounded metadata. Asgard currently does not load images.
- Target resolution must be deterministic. Unknown, duplicated, offline or failing targets must return a neutral error via Midgard/adapter, not silently route to Alfred or a default Butler.
- Tracing and logs must avoid raw private request bodies or credential-bearing headers.

## Transport and adapter contract

Present Asgard envelopes are framework-neutral and **not directly type-compatible** with Midgard's `AsgardTarget.handle(MidgardRequest)->MidgardResult`. The concrete composition layer is the one place for request/response conversion. It must preserve speaker and target fields, ID correlation and canonical source; handle invalid/malformed replies without leaking executor exceptions; and leave Midgard's central error taxonomy untouched.

Asgard does not import Midgard, Bifröst, FastAPI, Wilfred or Alfred. Midgard does not construct Butler runtimes. Neither component gets a competing router.

## Maturity and proving

| Claim | Status | Evidence |
| --- | --- | --- |
| Package, typed contracts, alias matching, local unavailability | **Available in private baseline** | Standalone tests + Python 3.12/3.13 wheel CI |
| Optional speaker/target context preserved to injected executor | **Available in private baseline** | `tests/test_context.py` |
| Butler-isolated instance identity | **Available as Asgard contract** | `tests/test_ownership_contract.py` |
| Real Alfred consumer migration | **Privately proven** | ALF-222: CI, server deployment and Android request/reply |
| Second Wilfred / Manfred consumer through Midgard | **Not implemented** | ALF-197 |
| Host-side Midgard envelope adapter | **Privately proven for Alfred** | ALF-222; generic consumer integration remains tracked in ASG-003 |
| Profile image data URI and manifest projection | **Designed to enable** | ASG-002, MID-009, BIF-015, ALF-217 |
| Published public release | **Not published** | Explicit release + security review required |

This document supersedes earlier wording that positioned Asgard as a global resolver of concrete Butler instances: **Midgard chooses the target; Asgard belongs to the target Butler**. The active Butler invariant itself remains the concrete runtime's responsibility.
