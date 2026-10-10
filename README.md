# Butler Asgard

Standalone provider-neutral Butler-side identity projection and ingress boundary.

Each concrete Butler owns its identity (canonical name, aliases, description, optional local profile image) and its executor. An Asgard instance exposes that identity and delegates requests to the injected executor. Cross-Butler selection and alias conflicts are Midgard's responsibility.

This first package is a contract/proving baseline, not a deployed Alfred/Wilfred consumer and not a released artifact. It does not implement runtime activation, authorization, transport, image-file loading, or client manifest serialization. The host must enforce runtime activation, policy, permissions, confirmation and request authentication. It must validate and convert optional image assets into client-safe metadata before publishing them.

The historical Alfred code and tests remain reachable in the imported Git history, but are deliberately removed from the current package and test collection. See `docs/PROVENANCE.md` for the original-to-filtered commit mapping.

## Development

On Python 3.12+:

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m build --wheel --sdist
```

CI also installs the wheel into a fresh virtual environment and smoke-tests the installed distribution.
