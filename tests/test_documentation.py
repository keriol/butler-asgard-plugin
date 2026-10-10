"""Keep the documented example executable and free from private dependencies."""

import subprocess
import sys
from pathlib import Path


def test_basic_example_runs_through_current_package():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(repo_root / "examples/basic_butler.py")],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == "Example Butler: Echo: hello"


def test_documented_paths_and_publication_warning_present():
    repo_root = Path(__file__).resolve().parents[1]
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    integration = (repo_root / "docs/INTEGRATION.md").read_text(encoding="utf-8")
    architecture = (repo_root / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
    publication = (repo_root / "docs/PUBLICATION.md").read_text(encoding="utf-8")
    assert "docs/INTEGRATION.md" in readme
    assert "docs/ARCHITECTURE.md" in readme
    assert "assets/profile.png" in integration
    assert "WILFRED_NAME" in integration
    assert "Midgard" in architecture
    assert "NOT RELEASED" in publication
    assert "Privately proven" in architecture
    assert "It does not yet consume the standalone package" not in integration
    assert "production Alfred does not yet depend" not in publication
