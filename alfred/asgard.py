from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from alfred.butler_context import active_butler
from alfred.runtime import AlfredRuntime, build_alfred_runtime


class Asgard(Protocol):
    """Runtime-side Butler boundary consumed by Midgard-facing ingress."""

    def ask(self, message: str) -> dict[str, Any]:
        ...


@dataclass(frozen=True, slots=True)
class AlfredAsgard:
    """Alfred implementation of the minimal Asgard request boundary."""

    runtime: AlfredRuntime

    def ask(self, message: str) -> dict[str, Any]:
        with active_butler(self.runtime):
            return self.runtime.core.ask(message)


def build_alfred_asgard() -> AlfredAsgard:
    """Build an Asgard endpoint backed by one request-scoped Alfred runtime."""
    return AlfredAsgard(
        runtime=build_alfred_runtime()
    )
