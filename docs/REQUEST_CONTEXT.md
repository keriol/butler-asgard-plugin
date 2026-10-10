# ASG-003: per-request context preservation

`RequestEnvelope` has optional `target_butler_name` and `SpeakerEnvelope` fields so a consumer-side adapter can preserve the input of a `MidgardRequest` without silently losing caller context.

The fields are **opaque caller-supplied context**, not proof of identity, user authentication, authorization or permission. The concrete Butler authenticates callers and enforces operation policy separately. Neither Asgard nor its envelope resolves targets.

A composition adapter, in the concrete Butler / hosting integration layer, maps:

- `MidgardRequest.request_id` → `RequestEnvelope.request_id`;
- `MidgardRequest.message` → `RequestEnvelope.message`;
- `MidgardRequest.target_butler_name` → `RequestEnvelope.target_butler_name`;
- optional `MidgardRequest.speaker` fields → `SpeakerEnvelope`;
- `ResponseEnvelope` → `MidgardResponse`, preserving canonical Butler source identity and correlation.

Structured `MidgardError` and all cross-Butler routing policies stay owned by Midgard and the adapter. Do not import Midgard or Core into `butler_asgard`.

No network protocol, authentication scheme, asset handling or client presentation is provided by this contract.
