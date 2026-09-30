from __future__ import annotations

from types import SimpleNamespace
from pathlib import Path

from alfred.asgard import AlfredAsgard
from alfred.butler_context import current_active_butler


def test_asgard_activates_the_runtime_for_request_execution():
    observed = []
    runtime = SimpleNamespace()

    def ask(message: str):
        observed.append((message, current_active_butler()))
        return {
            "ok": True,
            "response": "pong",
        }

    runtime.core = SimpleNamespace(
        ask=ask,
    )

    result = AlfredAsgard(runtime).ask("ping")

    assert result["ok"] is True
    assert observed == [
        ("ping", runtime)
    ]


def test_asgard_restores_previous_butler_context():
    runtime = SimpleNamespace(
        core=SimpleNamespace(
            ask=lambda _message: {
                "ok": True,
            }
        )
    )

    previous = current_active_butler()

    AlfredAsgard(runtime).ask("ping")

    assert current_active_butler() is previous


def test_midgard_source_has_no_runtime_core_execution_knowledge():
    source = (
        Path(__file__).resolve().parents[1]
        / "routers/midgard.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "runtime.core" not in source
    assert "build_alfred_runtime" not in source
    assert "_build_runtime" not in source
    assert "_build_asgard().ask(" in source
