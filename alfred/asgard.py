from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from alfred.butler_context import active_butler
from alfred.runtime import AlfredRuntime, build_alfred_runtime
from config import ALFRED_VERSION


ASGARD_VERSION = "alfred-internal"


class Asgard(Protocol):
    """Butler-owned identity projection and ingress boundary."""

    @property
    def butler_name(self) -> str:
        ...

    @property
    def nicknames(self) -> tuple[str, ...]:
        ...

    @property
    def available(self) -> bool:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def version(self) -> str:
        ...

    @property
    def asgard_version(self) -> str:
        ...

    def matches_butler_name(self, requested_name: str) -> bool:
        ...

    def ask(self, message: str) -> dict[str, Any]:
        ...


@dataclass(frozen=True, slots=True)
class AlfredAsgard:
    """Alfred-owned Asgard projection and request boundary."""

    runtime: AlfredRuntime

    @property
    def butler_name(self) -> str:
        return self.runtime.identity.canonical_name

    @property
    def nicknames(self) -> tuple[str, ...]:
        return self.runtime.identity.aliases

    @property
    def available(self) -> bool:
        return True

    @property
    def description(self) -> str:
        return self.runtime.identity.description

    @property
    def version(self) -> str:
        return ALFRED_VERSION

    @property
    def asgard_version(self) -> str:
        return ASGARD_VERSION

    def matches_butler_name(self, requested_name: str) -> bool:
        return self.runtime.identity.matches(requested_name)

    def ask(self, message: str) -> dict[str, Any]:
        with active_butler(self.runtime):
            result = self.runtime.core.ask(message)

        response = dict(result)
        response["source_butler_name"] = self.runtime.identity.canonical_name
        return response


def build_alfred_asgard() -> AlfredAsgard:
    """Build Alfred's Asgard around one request-scoped Alfred runtime."""
    return AlfredAsgard(
        runtime=build_alfred_runtime()
    )
