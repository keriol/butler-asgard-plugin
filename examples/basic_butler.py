"""Dependency-free Butler Asgard smoke example.

Run against an installed wheel, or PYTHONPATH=src python examples/basic_butler.py.
This does not connect to a network, Midgard, devices or any real Butler.
"""

import asyncio

from butler_asgard import (
    AsgardBoundary,
    ButlerIdentity,
    RequestEnvelope,
    SpeakerEnvelope,
)


async def echo(request: RequestEnvelope) -> str:
    return f"Echo: {request.message}"


async def main() -> None:
    boundary = AsgardBoundary(
        identity=ButlerIdentity(
            canonical_name="Example Butler",
            aliases=("Example", "EB"),
            description="Example standalone Butler instance",
            profile_picture="assets/profile.png",
        ),
        ingress=echo,
        availability=lambda: True,
    )

    assert boundary.matches_butler_name(" eb ")
    response = await boundary.handle(
        RequestEnvelope(
            request_id="example-1",
            message="hello",
            target_butler_name="EB",
            speaker=SpeakerEnvelope(
                speaker_id="example-device",
                language="en",
            ),
        )
    )
    assert response.request_id == "example-1"
    assert response.response == "Echo: hello"
    assert response.source_butler_name == "Example Butler"
    print(f"{response.source_butler_name}: {response.response}")


if __name__ == "__main__":
    asyncio.run(main())
