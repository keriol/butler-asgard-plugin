"""Generic Asgard ownership assertions migrated from Alfred ALF-185 proving.

The historical Alfred tests remain in Git provenance. No private runtime imports.
"""
import asyncio

from butler_asgard import AsgardBoundary, ButlerIdentity, RequestEnvelope


def test_owner_identity_is_projected_without_a_second_asgard_identity_store():
    identity = ButlerIdentity(
        canonical_name="Butler-One",
        aliases=("One", "Uno"),
        description="A concrete Butler instance",
        profile_picture="assets/one.png",
    )
    async def answer(_request):
        return "pong"

    boundary = AsgardBoundary(identity, answer, lambda: True)
    assert boundary.identity is identity
    assert boundary.butler_name == "Butler-One"
    assert boundary.nicknames == ("One", "Uno")
    assert boundary.identity.description == "A concrete Butler instance"
    assert boundary.identity.profile_picture == "assets/one.png"
    assert boundary.available is True
    assert not hasattr(boundary, "butler_name_override")


def test_alias_matching_is_exact_and_normalized():
    async def answer(_request):
        return "pong"

    boundary = AsgardBoundary(
        ButlerIdentity("Butler-One", aliases=("One", "Unò")),
        answer,
        lambda: True,
    )
    assert all(boundary.matches_butler_name(n) for n in (
        "Butler-One", " butler-one ", "one", "UNÒ"
    ))
    assert not boundary.matches_butler_name("Butler-Two")
    assert not boundary.matches_butler_name("Uno")


def test_canonical_response_source_is_runtime_owned_even_when_addressed_by_alias():
    async def answer(_request):
        return "pong"

    boundary = AsgardBoundary(
        ButlerIdentity("Canonical", aliases=("Alias",)),
        answer,
        lambda: True,
    )
    assert boundary.matches_butler_name("Alias")
    result = asyncio.run(boundary.handle(RequestEnvelope(
        request_id="r-identity",
        message="ping",
        target_butler_name="Alias",
    )))
    assert result.request_id == "r-identity"
    assert result.source_butler_name == "Canonical"


def test_distinct_asgards_do_not_share_identity_or_presentation():
    async def answer(_request):
        return "ok"

    first = AsgardBoundary(
        ButlerIdentity("Butler-One", aliases=("One",), profile_picture="one.png"),
        answer, lambda: True,
    )
    second = AsgardBoundary(
        ButlerIdentity("Butler-Two", aliases=("Two",), profile_picture="two.png"),
        answer, lambda: False,
    )
    assert first.matches_butler_name("One")
    assert not second.matches_butler_name("One")
    assert first.identity.profile_picture != second.identity.profile_picture
    assert first.available and not second.available
