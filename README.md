# Butler Asgard

Standalone provider-neutral Butler-side identity projection and ingress boundary.

Each concrete Butler owns its identity (canonical name, aliases, description, optional local profile image) and its executor. An Asgard instance exposes that identity and delegates requests to the injected executor. Cross-Butler selection and alias conflicts are Midgard's responsibility.

This first package is a contract/proving baseline, not a deployed Alfred/Wilfred consumer and not a released artifact. It does not implement runtime activation, authorization, transport, image-file loading, or client manifest serialization. The host must enforce runtime activation, policy, permissions, confirmation and request authentication. It must validate and convert optional image assets into client-safe metadata before publishing them.

The original Alfred history is retained in `alfred/asgard.py` and `tests/test_alf_185_asgard_boundary.py` for provenance; those historical files are not installed as part of this package.

See `docs/PROVENANCE.md` for the original-to-filtered commit mapping.
