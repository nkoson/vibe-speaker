# Independent references and verification

`reference_exports/manifest.json` records the origin, conditions and hashes of frozen
numeric exports. These are analytical and independently evaluated circuit references,
not measurements. Regenerate deliberately with:

```
.speaker-venv/bin/python framework/benchmarks/generate_reference_exports.py
```

Production tests consume frozen exports; they do not regenerate them or derive their
expected values through production physics helpers. `test_reference_exports.py`
checks production network solutions against independently specified transfer functions.
`catalog.json` also lists limiting-case and conservation tests for the wider framework.

`framework/tools/compare_reference_export.py` compares numeric CSV exports and emits
differences without design acceptance decisions. External export contributions should
retain the original file, engine/version, configuration, input hashes, frequency grid,
units, voltage/distance/timing basis and permission to redistribute. Label measurement
data as such only when its acquisition and uncertainty are documented.

See [passive analysis](../references/passive-analysis.md) for definitions and sources.
