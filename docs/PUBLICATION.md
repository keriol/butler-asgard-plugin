# Butler Asgard Plugin: Public Alpha release gates 🎩

> **0.1.0 RELEASE CANDIDATE · GitHub publication/tag/assets must be verified separately**
>
> Source version alone does not prove a GitHub release. Repository visibility, annotated tag, release assets and public Help updates require separate evidence.

## The Butler has a name. Asgard knows whom you called.

One house can have Alfred. A developer lab can have Wilfred. An experimental installation can have Manfred. They do not need three different implementations of the same entrance.

**Butler Asgard** is the small provider-neutral package that exposes a Butler-owned identity and receives requests on behalf of exactly one concrete Butler instance.

```text
Bifröst client -> Midgard chooses Butler -> that Butler's Asgard -> runtime
```

Each runtime defines its **canonical name**, optional **aliases**, a **description**, and an optional **profile picture reference**. Asgard recognizes exact names and aliases, keeps request IDs intact and always signs responses with the canonical Butler identity. It neither invents a runtime nor guesses an alternative target.

### Try the standalone contract

```python
from butler_asgard import AsgardBoundary, ButlerIdentity

identity = ButlerIdentity(
    canonical_name="My Butler",
    aliases=("Butler",),
    profile_picture="assets/profile.png",
)
asgard = AsgardBoundary(identity, my_async_executor, my_availability_check)
```

The concrete application supplies `my_async_executor` and `my_availability_check`. The image filename is a **recommended host convention**, not an Asgard file-loader feature.

For working, dependency-free code see [`examples/basic_butler.py`](../examples/basic_butler.py). To integrate it for real, read [`INTEGRATION.md`](INTEGRATION.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md).

### Three principles

**The Butler owns its identity.** No hidden Asgard name store, no public package that knows a private Butler's personality or server paths.

**Routing stays in Midgard.** Asgard is the endpoint, not a global dispatcher. No fuzzy matching, no cross-Butler fallback.

**Permission survives the doorway.** A caller's declared name, speaker ID or matched alias never authorizes execution. The host and runtime still enforce authentication, permissions, confirmations and observable post-action verification.

### Current maturity

**Available in the 0.1.0 package contract:** installable pure-Python wheel, isolated CI, neutral request/response envelopes, alias matching, canonical source identity and injected availability/async execution.

**Privately proven:** Alfred's host-owned Midgard adapter and first real standalone Asgard consumer, with green CI, healthy deployment and an Android Interphone request/reply on 2026-10-10. This does not certify the second Butler consumer or new physical-action verification.

**Designed to enable, not yet implemented:** built-in image projection to manifests, polished multi-Butler installation recipes, public distribution/release.

A public 0.1.0 release must be verified by its GitHub release and assets, not inferred from this document. Production Alfred uses a pinned earlier development package; historical IGNITION-001 shipped Alfred-owned internal Asgard instead.

## Publication checklist: every item is a real gate

- [x] First real Alfred consumer proved via CI, server deployment and Android response (ALF-222); additional Midgard error/correlation and multiple-instance proving remain separate work.
- [ ] ASG-002/MID-009/BIF-015/ALF-217 picture projection implemented or clearly omitted from the initial public release.
- [ ] Configuration examples match actual Wilfred/Alfred public contracts; examples tested under clean install.
- [ ] Public API, Python versions, changelog, compatibility promises and license reviewed.
- [ ] Audited **entire Git history**, not just `main`: author metadata, blobs, commits, old names, assets, diffs, commit messages, credentials, private runtime details and external endpoints.
- [x] ASG-005: owner deliberately accepted retained historical code, metadata, PR and issue disclosure; preserve the **same repository** and its history, without force-push.
- [ ] CI on final 0.1.0 main/tag candidate succeeds; build wheel+sdist, clean install, smoke, package contents, permissions and license verified.
- [ ] No private acquisition code, personal settings or unrelated runtime behavior present anywhere in publishable history.
- [ ] Explicit GitHub release membership, annotated tag and verified release assets before announcing a version.

## Ownership links

- ASG-001, standalone provenance and consumers: issue #1
- ASG-002, identity picture metadata: issue #6
- ASG-003, Midgard composition adapter: issue #9
- DOC-001, external-command contract: issue #3
- DOC-002, this documentation: issue #14
- MID-009, BIF-015, ALF-217: neutral transport and concrete picture projection

Asgard is the Butler's doorway. What happens beyond it remains the Butler's responsibility.
