# Butler Asgard Plugin 0.1.0 Public Alpha

**Release scope:** standalone, Butler-owned ingress and identity projection boundary, Python 3.12+.

## Included

- Frozen `ButlerIdentity` with a runtime-supplied canonical name, exact aliases, description and optional picture **reference**.
- `AsgardBoundary` composed by its concrete Butler host, with async ingress and injected availability probe.
- `RequestEnvelope` and `ResponseEnvelope`: request ID correlation, optional target/speaker context, canonical source attribution.
- Deterministic `strip().casefold()` name matching, with host/Midgard responsible for cross-Butler conflicts.
- Runnable neutral example and tests.
- Wheel and source archive with archive-content allowlist and clean-install checks on Python 3.12 and 3.13.

## Integration evidence

Alfred privately adopted the earlier `0.1.0.dev0` Asgard commit through a compatibility adapter and verified a server deployment and Android Interphone request/response. The **0.1.0 package is a separate source/release checkpoint**, not an automatic Alfred upgrade or part of the historical IGNITION-001 release.

## Deliberately out of scope

- Cross-Butler routing (Midgard), external transport (Bifröst), caller authentication, execution permissions, confirmations and domain policy.
- Butler runtime discovery, plugin entry-point registration, process lifecycle or HTTP serving.
- Loading, transforming or client-serving the profile image.
- Publicly proven second Wilfred/Manfred Butler through the communication network.
- Public compatibility guarantees or a PyPI release.

## Publication evidence checklist

The text of this file is not release proof. Confirm all of the following before announcement:

1. The **same** GitHub repository is publicly visible, after the owner's accepted-history decision.
2. Final 0.1.0 commit on `main` passes CI for Python 3.12 and 3.13, wheel and sdist scan, isolated installation and smoke.
3. Annotated tag `v0.1.0` points to the reviewed green main commit.
4. A GitHub **pre-release** is published from that tag and contains a verified wheel and sdist.
5. Butler public docs / Help are updated **after** release evidence, distinguishing 0.1.0 from previous Ignition and private Alfred integration.

## Historical disclosure decision

The repository retains its filtered historical Asgard/Alfred ingress code, public author metadata, and existing GitHub issue/PR history by the owner's explicit decision in ASG-005. That history does not form part of the `butler-asgard` installed package. Publishing the repository also exposes the historical Git data; a clean wheel alone is not a full repository-history privacy guarantee.
