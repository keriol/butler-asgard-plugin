from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from alfred.butler_context import active_butler
from alfred.runtime import AlfredRuntime, build_alfred_runtime


class Asgard(Protocol):
    """Butler-owned identity and ingress boundary."""

    @property
    def butler_name(self) -> str:
        ...

    @property
    def available(self) -> bool:
        ...

    def matches_butler_name(self, requested_name: str) -> bool:
        ...

    def ask(self, message: str) -> dict[str, Any]:
        ...


@dataclass(frozen=True, slots=True)
class AlfredAsgard:
    """Alfred-owned Asgard identity and request boundary."""

    runtime: AlfredRuntime
    butler_name: str = "Alfred"

    @property
    def available(self) -> bool:
        return True

    def matches_butler_name(self, requested_name: str) -> bool:
        return (
            str(requested_name or "").strip().casefold()
            == self.butler_name.casefold()
        )

    def ask(self, message: str) -> dict[str, Any]:
        with active_butler(self.runtime):
            result = self.runtime.core.ask(message)

        response = dict(result)
        response["source_butler_name"] = self.butler_name
        return response


def build_alfred_asgard() -> AlfredAsgard:
    """Build Alfred's Asgard around one request-scoped Alfred runtime."""
    return AlfredAsgard(
        runtime=build_alfred_runtime()
    )
