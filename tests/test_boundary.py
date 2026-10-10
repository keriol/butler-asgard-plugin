import asyncio

import pytest

from butler_asgard import AsgardBoundary, ButlerIdentity, RequestEnvelope


def test_identity_normalizes_without_fuzzy_matching():
    identity = ButlerIdentity("Alfred", aliases=("Alf", "Alfrè"))
    assert identity.matches(" ALF ")
    assert identity.matches("alfrè")
    assert not identity.matches("Alfredo")
    assert not identity.matches("")


def test_reject_duplicate_and_blank_identity():
    with pytest.raises(ValueError):
        ButlerIdentity(" ")
    with pytest.raises(ValueError):
        ButlerIdentity("Alfred", ("alfred",))
    with pytest.raises(ValueError):
        ButlerIdentity("Wilfred", ("",))


def test_per_instance_identity_and_canonical_response():
    async def echo(request):
        return request.message

    async def check():
        for name in ("Alfred", "Wilfred", "Manfred"):
            boundary = AsgardBoundary(ButlerIdentity(name, (f"{name}-alias",)), echo, lambda: True)
            assert boundary.matches_butler_name(f" {name.upper()}-ALIAS ")
            response = await boundary.handle(RequestEnvelope("r-1", "hello"))
            assert response.request_id == "r-1"
            assert response.source_butler_name == name
            assert response.response == "hello"

    asyncio.run(check())


def test_unavailable_never_executes():
    calls = []
    async def executor(request):
        calls.append(request)
        return "should not execute"
    boundary = AsgardBoundary(ButlerIdentity("Wilfred"), executor, lambda: False)
    with pytest.raises(RuntimeError):
        asyncio.run(boundary.handle(RequestEnvelope("x", "hello"))
    assert calls == []


def test_ingress_cannot_forge_source_identity():
    async def ingress(_request):
        return "reply"
    identity = ButlerIdentity("Manfred", profile_picture="assets/manfred.png")
    boundary = AsgardBoundary(identity, ingress, lambda: True)
    assert boundary.identity.profile_picture == "assets/manfred.png"
    response = asyncio.run(boundary.handle(RequestEnvelope("req", "go")))
    assert response.source_butler_name == "Manfred"
