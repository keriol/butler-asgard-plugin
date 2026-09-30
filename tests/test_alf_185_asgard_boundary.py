from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from alfred.asgard import AlfredAsgard
from alfred.butler_context import current_active_butler


def _runtime(ask):
    return SimpleNamespace(
        core=SimpleNamespace(ask=ask),
    )


def test_asgard_owns_alfred_identity():
    asgard = AlfredAsgard(
        _runtime(lambda _message: {"response": "ok"})
    )

    assert asgard.butler_name == "Alfred"
    assert asgard.available is True


def test_asgard_matches_canonical_name_and_nicknames():
    asgard = AlfredAsgard(
        _runtime(lambda _message: {"response": "ok"}),
        nicknames=("Alfie", "A"),
    )

    assert asgard.matches_butler_name("Alfred") is True
    assert asgard.matches_butler_name(" alfred ") is True
    assert asgard.matches_butler_name("alfie") is True
    assert asgard.matches_butler_name(" A ") is True
    assert asgard.matches_butler_name("Wilfred") is False


def test_asgard_with_no_nicknames_preserves_existing_behavior():
    asgard = AlfredAsgard(
        _runtime(lambda _message: {"response": "ok"})
    )

    assert asgard.nicknames == ()
    assert asgard.matches_butler_name("Alfred") is True
    assert asgard.matches_butler_name("Alfie") is False


def test_nickname_addressing_keeps_canonical_response_identity():
    asgard = AlfredAsgard(
        _runtime(lambda _message: {"response": "pong"}),
        nicknames=("Alfie",),
    )

    assert asgard.matches_butler_name("Alfie") is True

    result = asgard.ask("ping")

    assert result["source_butler_name"] == "Alfred"


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
    assert result["source_butler_name"] == "Alfred"
    assert observed == [
        ("ping", runtime)
    ]


def test_asgard_source_identity_overrides_runtime_output():
    runtime = _runtime(
        lambda _message: {
            "response": "pong",
            "source_butler_name": "Not-Alfred",
        }
    )

    result = AlfredAsgard(runtime).ask("ping")

    assert result["source_butler_name"] == "Alfred"


def test_asgard_restores_previous_butler_context():
    runtime = _runtime(
        lambda _message: {
            "ok": True,
            "response": "pong",
        }
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
