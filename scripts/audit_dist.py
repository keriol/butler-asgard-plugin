"""Validate wheel/sdist contents before any Asgard public distribution."""

from __future__ import annotations

import argparse
import re
import tarfile
import zipfile
from pathlib import Path, PurePosixPath


def validate_member(name: str, *, kind: str) -> str:
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "\\" in name
        or not path.parts
        or any(part.startswith(".") and part not in (".dist-info",) for part in path.parts)
    ):
        raise AssertionError(f"invalid archive member: {name!r}")
    if any(part in {"alfred", "secrets", ".git", "__pycache__", ".venv"} for part in path.parts):
        raise AssertionError(f"private/unwanted archive member: {name!r}")
    if any(part.lower().endswith((".pem", ".key", ".p12", ".env", ".sqlite", ".db", ".pyc")) for part in path.parts):
        raise AssertionError(f"private/unwanted archive member: {name!r}")
    if kind == "wheel":
        first = path.parts[0]
        if first != "butler_asgard" and not first.endswith(".dist-info"):
            raise AssertionError(f"unexpected wheel member: {name!r}")
    else:
        relative = PurePosixPath(*path.parts[1:])  # Strip versioned sdist root.
        if not relative.parts:
            return ""
        if str(relative) == "docs/PROVENANCE.md":
            raise AssertionError("private provenance must not ship")
        first = relative.parts[0]
        if first not in {"src", "tests", "examples", "docs", "LICENSE", "README.md", "pyproject.toml", "MANIFEST.in", "setup.cfg", "PKG-INFO"}:
            raise AssertionError(f"unexpected sdist member: {name!r}")
    return str(path)


def audit(dist: Path) -> None:
    wheels = list(dist.glob("butler_asgard-*.whl"))
    archives = list(dist.glob("butler_asgard-*.tar.gz"))
    assert len(wheels) == 1, f"expected one wheel, found {len(wheels)}"
    assert len(archives) == 1, f"expected one sdist, found {len(archives)}"

    with zipfile.ZipFile(wheels[0]) as wheel:
        names = [validate_member(item.filename, kind="wheel") for item in wheel.infolist() if not item.is_dir()]
        assert "butler_asgard/__init__.py" in names
        assert "butler_asgard/boundary.py" in names
        assert any(name.endswith(".dist-info/METADATA") for name in names)
        assert any(name.endswith(".dist-info/RECORD") for name in names)
        print(f"PASS wheel: {len(names)} files")

    with tarfile.open(archives[0], mode="r:gz") as sdist:
        members = sdist.getmembers()
        names = [validate_member(item.name, kind="sdist") for item in members if item.isfile()]
        assert any(name.endswith("/src/butler_asgard/boundary.py") for name in names)
        assert any(name.endswith("/pyproject.toml") for name in names)
        assert any(name.endswith("/README.md") for name in names)
        for item in members:
            assert item.isfile() or item.isdir(), f"unexpected sdist link/device: {item.name}"
        print(f"PASS sdist: {len(names)} files")

    print("PASS distribution contents: allowed roots, no old Alfred package or provenance archive")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", nargs="?", type=Path, default=Path("dist"))
    audit(parser.parse_args().dist)
