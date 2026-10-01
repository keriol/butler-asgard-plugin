from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from alfred.asgard import AlfredAsgard
from alfred.butler_context import current_active_butler
from alfred.identity import ALFRED_IDENTITY, ButlerIdentity


def _runtime(ask, *, identity: ButlerIdentity = ALFRED_IDENTITY):
    return SimpleNamespace(
        core=SimpleNamespace(ask=ask),
        identity=identity,
    )


def test_alfred_runtime_owns_identity_and_asgard_projects_it():
    identity = ButlerIdentity(
        canonical_name="Test Butler",
        aliases=("Tester",),
    )
    runtime = _runtime(
        lambda _message: {"response": "ok"},
        identity=identity,
    )
    asgard = AlfredAsgard(runtime)

    assert runtime.identity is identity
    assert asgard.butler_name == "Test Butler"
    assert asgard.nicknames == ("Tester",)
    assert asgard.available is True


def test_asgard_matches_runtime_canonical_name_and_aliases():
    asgard = AlfredAsgard(
        _runtime(lambda _message: {"response": "ok"})
    )

    assert asgard.matches_butler_name("Alfred") is True
    assert asgard.matches_butler_name(" alfred ") is True
    assert asgard.matches_butler_name("alf") is True
    assert asgard.matches_butler_name("alfrè") is True
    assert asgard.matches_butler_name("Alfy") is True
    assert asgard.matches_butler_name("ALFIE") is True
    assert asgard.matches_butler_name("Wilfred") is False


def test_asgard_has_no_independent_identity_configuration():
    runtime = _runtime(
        lambda _message: {"response": "ok"},
        identity=ButlerIdentity(
            canonical_name="Runtime-Owned",
            aliases=("Runtime-Alias",),
        ),
    )
    asgard = AlfredAsgard(runtime)

    assert asgard.butler_name == "Runtime-Owned"
    assert asgard.nicknames == ("Runtime-Alias",)
    assert asgard.matches_butler_name("Runtime-Alias") is True


def test_alias_addressing_keeps_runtime_canonical_response_identity():
    runtime = _runtime(
        lambda _message: {"response": "pong"},
        identity=ButlerIdentity(
            canonical_name="Canonical",
            aliases=("Alias",),
        ),
    )
    asgard = AlfredAsgard(runtime)

    assert asgard.matches_butler_name("Alias") is True

    result = asgard.ask("ping")

    assert result["source_butler_name"] == "Canonical"


def test_asgard_activates_the_runtime_for_request_execution():
    observed = []
    runtime = SimpleNamespace(identity=ALFRED_IDENTITY)

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
