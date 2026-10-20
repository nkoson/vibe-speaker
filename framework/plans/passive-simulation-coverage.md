# Passive simulation coverage

Implement on `codex/passive-simulation-coverage`, with reviewable commits after
each stage. Active DSP synthesis and hardware configuration are outside scope.
Simulations report observables, numerical objective values and signed margins;
the design agent interprets them using the engineering references.

1. Independent analytical/reference-export corpus, comparison metrics and provenance.
2. Measured polar ingestion, explicit phase/voltage/distance conventions, response
   preparation (windowed impulses, complex merging and curve arithmetic).
3. Lossy voice-coil impedance and suspension creep, measured parameter identification,
   polygonal angular diffraction and additional enclosure networks.
4. Passive-network load diagnostics and programme dissipation, spatial optimization
   objectives, and linear impulse/step/group-delay analysis.
5. Independent regression cases, complete example/test replay, reference and contract
   reconciliation.

Every new model needs a repository engineering reference citing independent primary
literature or official mathematical documentation. Neither discussion forums nor
unattributed software behavior is an engineering source. Export fixtures distinguish
analytical values, independently computed values and measurements. None establishes
universal empirical accuracy.

## Progress

- Branch created from `61a2f31`; working tree was clean.
- Existing numerical tests and shared implementations inspected.
- Independent circuit exports, analytical two-source data, hashes and comparison
  metrics committed; the corpus does not depend on production physics imports.
- Angular ingestion and response preparation committed, with explicit timing,
  coverage, calibration, symmetry, interpolation and phase provenance.
- Small-signal inductance/creep laws connected to linear consumers; isobaric scaling
  preserves the law. Nonlinear solvers reject unsupported frequency-memory laws.
- General chamber networks, PR bandpass/double-tuned configurations and driver/PR
  parameter identification implemented with individual state outputs.
- Convex angular diffraction checked against a circular analytical reference.
- Exact ideal transformers, winding parasitics, programme integration, reactive-load
  diagnostics, spatial fit targets and linear time-response diagnostics implemented.
- FRD/ZMA/CSV/WAV exports preserve scale and emit provenance sidecars.
- References reconciled with current scope and independent sources. No active DSP
  synthesis or controller integration was added.

## Coverage and evidence

| Capability | Entry point | Evidence |
|---|---|---|
| Frozen references and curve differences | `benchmarks/reference_exports`, `compare_reference_export.py` | Independent rational circuits and analytical coherent field |
| Measured angular sources | `polar_import` | Propagation removal, normalization, signed patterns and missing coverage |
| IR, merge, trace coordinates, arithmetic | `response_prepare` | Delayed impulse, known gain/delay and logarithmic axes |
| Frequency-dependent motor laws | `_common/driver_models.py` | Fractional phase/magnitude, passive compliance and zero-extension limits |
| Chamber and PR configurations | `enclosure_network` | Independent lumped limit and topology/state checks |
| Parameter identification | `parameter_identification` | Recovery from independently synthesized loaded-driver equations |
| Angular diffraction | `baffle_diffraction` | Circular formula and quadrature refinement |
| Ideal transformer/parasitics | `board_nodal` | Ratio, reflected load, power and explicit circuit equivalence |
| Reactive/programme diagnostics | `network_diagnostics` | Resistive/reactive limits and known integrated power |
| Spatial objectives | `network_fit` | Known attenuator and retained objective terms/margins |
| Linear time response | `response_diagnostics` | Analytical RC delay, impulse reconstruction and export normalization |

Empirical validation of arbitrary constructed speakers is not established by these
tests. Inputs requiring measurements remain explicit. The model interprets physical
results; mathematical domain checks and test assertions do not select designs.

## Completion

All implementation stages above are complete. The complete example chain and test
suite passed: 232 tests. The final angular-model CLI replay computed successfully,
and `git diff --check` reported no whitespace errors. The repository inventory now
contains 35 standalone applications. No implementation items remain on this list.
