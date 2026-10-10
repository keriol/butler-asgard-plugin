"""No transport, global registry, runtime construction or domain policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol


def _norm(value: str) -> str:
    return value.strip().casefold()


@dataclass(frozen=True, slots=True)
class ButlerIdentity:
    """Immutable description supplied by a concrete Butler, never by Asgard."""

    canonical_name: str
    aliases: tuple[str, ...] = ()
    description: str = ""
    profile_picture: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.canonical_name, str) or not _norm(self.canonical_name):
            raise ValueError("canonical_name must not be blank")
        if not isinstance(self.aliases, tuple) or not all(isinstance(a, str) and _norm(a) for a in self.aliases):
            raise ValueError("aliases must be a tuple of nonblank strings")
        accepted = (_norm(self.canonical_name), *(_norm(a) for a in self.aliases))
        if len(set(accepted)) != len(accepted):
            raise ValueError("duplicate canonical name/alias")
        if not isinstance(self.description, str):
            raise TypeError("description must be a string")
        if self.profile_picture is not None and not isinstance(self.profile_picture, str):
            raise TypeError("profile_picture must be a string or None")

    def matches(self, requested_name: str) -> bool:
        if not isinstance(requested_name, str) or not _norm(requested_name):
            return False
        return _norm(requested_name) in (_norm(self.canonical_name), *(_norm(x) for x in self.aliases))


@dataclass(frozen=True, slots=True)
class SpeakerEnvelope:
    """Caller-supplied speaking context, not authorization evidence."""

    speaker_id: str
    persistent: bool = False
    call_me: str | None = None
    language: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.speaker_id, str) or not self.speaker_id.strip():
            raise ValueError("speaker_id must not be blank")
        if not isinstance(self.persistent, bool):
            raise TypeError("persistent must be boolean")
        for field_name in ("call_me", "language"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string or None")


@dataclass(frozen=True, slots=True)
class RequestEnvelope:
    request_id: str
    message: str
    target_butler_name: str | None = None
    speaker: SpeakerEnvelope | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must not be blank")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must not be blank")
        if self.target_butler_name is not None and (
            not isinstance(self.target_butler_name, str) or not self.target_butler_name.strip()
        ):
            raise ValueError("target_butler_name must be nonblank or None")
        if self.speaker is not None and not isinstance(self.speaker, SpeakerEnvelope):
            raise TypeError("speaker must be SpeakerEnvelope or None")


@dataclass(frozen=True, slots=True)
class ResponseEnvelope:
    request_id: str
    response: str
    source_butler_name: str


class ButlerIngress(Protocol):
    async def __call__(self, request: RequestEnvelope) -> str:
        """Execute inside the concrete Butler's policy/runtime context."""
        ...


@dataclass(frozen=True, slots=True)
class AsgardBoundary:
    """Per-Butler projection and ingress, with no global selection policy."""

    identity: ButlerIdentity
    ingress: ButlerIngress
    availability: Callable[[], bool]

    @property
    def butler_name(self) -> str:
        return self.identity.canonical_name

    @property
    def nicknames(self) -> tuple[str, ...]:
        return self.identity.aliases

    @property
    def available(self) -> bool:
        return bool(self.availability())

    def matches_butler_name(self, requested_name: str) -> bool:
        return self.identity.matches(requested_name)

    async def handle(self, request: RequestEnvelope) -> ResponseEnvelope:
        if not self.available:
            raise RuntimeError("Butler ingress unavailable")
        response = await self.ingress(request)
        if not isinstance(response, str):
            raise TypeError("Butler ingress must return a text response")
        return ResponseEnvelope(
            request_id=request.request_id,
            response=response,
            source_butler_name=self.identity.canonical_name,
        )
