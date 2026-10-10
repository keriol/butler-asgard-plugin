import asyncio
import pytest
from butler_asgard import AsgardBoundary, ButlerIdentity, RequestEnvelope, SpeakerEnvelope


def test_optional_context_is_retained_for_ingress():
    received = []

    async def ingress(request):
        received.append(request)
        return request.message

    speaker = SpeakerEnvelope("speaker-42", persistent=True, call_me="Guest", language="it-IT")
    original = RequestEnvelope(
        "req-2", "hello", target_butler_name="Alf", speaker=speaker
    )
    boundary = AsgardBoundary(ButlerIdentity("Alfred", aliases=("Alf",)), ingress, lambda: True)
    result = asyncio.run(boundary.handle(original))
    assert received == [original]
    assert received[0].speaker is speaker
    assert received[0].target_butler_name == "Alf"
    assert result.request_id == original.request_id
    assert result.source_butler_name == "Alfred"


def test_empty_context_is_backwards_compatible():
    request = RequestEnvelope("r", "hello")
    assert request.target_butler_name is None
    assert request.speaker is None


@pytest.mark.parametrize("context", [
    {"target_butler_name": ""},
    {"target_butler_name": "  "},
    {"target_butler_name": 7},
    {"speaker": "speaker-id"},
])
def test_bad_context_fails_closed(context):
    with pytest.raises((ValueError, TypeError)):
        RequestEnvelope("r", "hello", **context)


def test_speaker_does_not_claim_authentication():
    speaker = SpeakerEnvelope("device-user-id", persistent=False)
    assert not speaker.persistent
    with pytest.raises(ValueError):
        SpeakerEnvelope(" ")
    with pytest.raises(TypeError):
        SpeakerEnvelope("id", persistent="yes")
