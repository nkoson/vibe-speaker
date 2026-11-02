# Electrical loads and crossover comparisons

These interfaces return curves, assumptions, residuals and coverage observations to the agent. They do not qualify evidence, reject a design, require a particular inductance law or define acceptable error. Missing provenance, unknown support bands and underdetermined fits remain visible data. Parsing failures, missing numerical operands and unsolvable systems remain computation failures, distinct from engineering validation.

## Load evidence

`source_response` accepts optional `electrical_load` metadata at its top level or inside its `impedance` object. Inline ladder `load` and nodal `impedance` objects accept the same metadata. An LF driver's metadata lives in `driver.electrical_load`.

```json
{
  "kind": "free_air",
  "ts": {
    "fs_hz": 55, "vas_l": 18, "qms": 4.5, "qes": 0.48,
    "re_ohm": 5.7, "sd_cm2": 135,
    "inductance_model": {"kind": "lr2", "le_mh": 0.11, "l2_mh": 0.65, "r2_ohm": 4.2}
  },
  "electrical_load": {
    "identity": "driver-source-revision",
    "evidence": ["inventory/source-record.json"],
    "supported_band_hz": [80, 12000],
    "alternatives": []
  }
}
```

Values above illustrate the contract; they are not general defaults. Constant, Leach, LR2 and semi-inductance models retain their existing units and equations. `kind: blocked` accepts `ts` with Re and an inductance model and returns the blocked electrical impedance without the mechanical branch. Free-air and enclosure loads include their mechanical loading. `resistive`, `resonant`, `ribbon`, complex `curve`, ZMA and result references remain available. A supported complex curve can be used directly without fitting it.

The versioned record appears at `source_contract.electrical_load` for canonical sources, and beside individual network/driver curves as `load_contract`. It contains the model, resolved inductance law, impedance scope, units, evidence, identity, model content digest, phase basis, alternatives and transformation history. `identity` is a caller's source identity or a deterministic digest of the model; `model_identity` describes its supplied realization. The evaluated band is never promoted to an evidence-supported band. An absent `supported_band_hz` remains null. Evidence and alternative records are preserved as supplied, not certified or automatically selected.

`observations` gives the requested band, count outside the stated support band, missing-evidence indicator, nonfinite/negative-real impedance counts and minimum real impedance. Imported curves additionally report their sampled band and extrapolated-point count. A two-column ZMA retains the legacy zero-phase numerical interpretation and explicitly reports `assumed_zero_missing_phase`. A legacy T/S `le_mh` retains its numerical behavior and reports `legacy_constant_inductance_from_ts`.

The shared resolver handles source references, ladder loads and nodal loads. Explicit overrides record the previous source identity and retained acoustic basis. LF, cavity, chamber-network and distributed-loading producers retain their driver/load model; electrothermal results retain the cold evidence and resistance shift. `whole_speaker.electrical_loads` exposes both acoustic-source and transfer-load records for comparison. Differences are reported without a consistency verdict. Schematic-generated netlists preserve source impedance paths and load metadata.

Acoustic source contracts remain separate. Electrical-only alternatives retain acoustic pressure per terminal volt. If a parameter change also changes that pressure, supply the corresponding replacement source or recompute the physical dependency chain through `system_scenarios`. The apps describe which operation was performed; the agent assesses physical relevance.

## Alternative loads in either fitter

Both `crossover_fit` and `network_fit` accept:

```json
{
  "load_scenarios": [
    {
      "name": "alternate",
      "loads": {"driver": {"kind": "resistive", "r_ohm": 4}},
      "sources": {},
      "basis": "controlled electrical sensitivity probe"
    }
  ],
  "load_scenario_objective": {"mode": "weighted_mean"}
}
```

A nominal case is always included. Keys identify ladder section names or nodal load IDs. `sources` optionally maps the same identities to replacement source references; nodal acoustic system sections associate via `load_id`. Replacing a ladder source without an explicit alternative load also replaces its load. Unmatched load/source keys are observations, not validation errors.

Objective modes are `nominal` (default, preserving existing optimization), `weighted_mean` or `worst_case`. Weighted means use equal weights unless supplied with `load_scenario_objective.weights`, a name-to-weight mapping, or each case's `weight`. Weights have no probability meaning. Negative weights contribute zero; a zero total or unknown mode uses the nominal objective, with the effective aggregation reported. No worst-case criterion is imposed by default. `network_fit.load_scenario_constraints: all` explicitly applies the caller's numerical constraints across all cases; otherwise they apply to nominal only. Ladder penalties are part of each case's residual and follow the declared aggregation.

Ladder outputs include full-grid scenario network results, branch transfers, complex load/input impedances, physical-leaf stresses, coherent acoustic sum and individual complex contributions. Stock realizations include the same scenario reports. Nodal trial rows contain each case's cost, margins, loads, stresses, source impedances and acoustic contributions. These support band-specific leakage, overlap, phase and sum comparisons. Numerical minima remain optimizer results; the agent chooses the design.

Model alternatives remain separate from component production tolerances. `system_scenarios` uses its existing shared draws across model cases, retains `load_evidence` for each step/draw, and optionally returns complete `step_results` with `retain_results: true`. Temporary computation files are removed as before; retained curves and contracts survive in the result.

## Identification diagnostics

`parameter_identification.observations[]` can set `role: held_out` to exclude an entire observation from optimization, or `held_out_indices` to exclude selected frequencies. The remaining samples alone determine parameters and the Jacobian. Magnitude-only files or inline `magnitude` arrays can be fitted without supplied phase; they report the missing phase and use magnitude residuals. Complex/phase residuals and observed-load circuit comparisons remain unspecified where phase is absent. `audit_bands: [{name, band_hz}]` reports fit and held-out complex RMS, magnitude and phase errors separately. Empty subsets report zero points and null statistics. `error_budget` is retained as caller context and does not trigger an acceptance decision.

`transfer_audits: [{name, elements}]` uses ordinary ladder elements to compare the observed and fitted load in the same circuit. Outputs include both terminal transfers, input impedances, and gain/phase differences. This exposes the crossover effect of a local fit residual without treating one scalar score as sufficient evidence. `alternative_parameters` evaluates caller-supplied parameter alternatives; it does not infer an admissible confidence region from a fit residual.

Existing bounds, bound distances, scaled Jacobian singular values and rank remain available. Single-condition fits without a known mass or motor scale now compute and report `not_independently_identified` rather than rejecting the observation. Fitted `driver_ts` explicitly retains the inductance model, and `impedance_model` is directly reusable with its evidence. The fitting band is recorded separately from any caller-stated support band.

## Verification and interpretation

`tests/test_electrical_load_contract.py` uses independent primitive electrical equations across four inductance laws and three ladder/nodal topologies. It checks file replay, metadata, phase/coverage observations, exclusion of held-out samples, fit-to-circuit residuals, and scenario retention. Controlled resistor-divider examples exercise both fitters: a changed load moves the weighted objective's preferred resistance, while an identical alternative leaves it unchanged. These are synthetic analytical cases, not measurements or universal driver priors.

For engineering interpretation, see [driver impedance and identification](../references/driver-impedance-identification.md). Numerical checks establish implementation consistency. The agent interprets load evidence, response changes, stress and tradeoffs against the current brief.
