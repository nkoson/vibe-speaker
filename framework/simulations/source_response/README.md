# source_response: one section's acoustic and electrical model

Builds the complex on-axis pressure per volt (1 m, free field) and the complex load impedance of one driver or driver-plus-horn on a common frequency grid. The result file is the standard "section" input of `crossover_network`, `crossover_fit` and `whole_speaker`. It also carries the directivity model and acoustic depth you declare, so downstream apps read everything about a section from one file.

## Run

```
python framework/simulations/source_response/run.py --input params.json --out results/ [--name section_mf]
```

## Input

| Key | Meaning |
|---|---|
| `name` | Section label carried into the result |
| `frequencies` | Grid, default 10 to 40000 Hz, 800 log points. Use the same grid for every section of a candidate |
| `acoustic.kind` | One of the source kinds below |
| `impedance.kind` | One of the impedance kinds below |
| `directivity` | Stored for `whole_speaker`: `{kind: piston, radius_mm|diameter_mm|sd_cm2}`, `{kind: gaussian, horizontal_deg, vertical_deg}`, `{kind: beamwidth_table, points: [[hz, h_deg, v_deg], ...]}`, `{kind: rectangular, width_mm, height_mm}` or `{kind: omni}` |
| `acoustic_depth_mm` | Stored for `whole_speaker`: acoustic centre behind the mounting face |
| `analysis.sensitivity_band_hz` | Band for the mean SPL statistic |

### Acoustic kinds

- `bandwidth_prior`: `sensitivity_db_2v83_1m`, optional `lower_hz`, `upper_hz`. Flat level with a second-order roll-off below `lower_hz` and a fourth-order roll-off reaching -10 dB at `upper_hz`. Use when only a published range is known.
- `published_curve`: `points: [[hz, spl_db], ...]`, `voltage_rms`, `distance_m`, optional `lower_rolloff_db_oct` (12), `upper_rolloff_db_oct` (24), `source` text. Minimum-phase reconstruction of a digitized datasheet plot.
- `lf_box`: `reference: {file, path}` to an `lf_box` result (`results.curves.0.pressure_pa` for cone plus port, `results.curves.0.cone_pressure_pa` for the cone alone). Optional `published_shape` (same fields as `published_curve`, plus `mode`) applies the datasheet shape above `blend_band_hz` (default [150, 300]) so breakup and the inductance roll-off appear. `mode: multiply` (the default) multiplies the datasheet shape onto the box model's own shape, which counts a roll-off present in both of them twice; `mode: replace` divides the box model's own shape out first, so below the blend band the box model owns the response, above it the box model owns only the level and the datasheet owns the shape. Use `replace` whenever the datasheet curve and the lumped model describe the same driver. `examples/section_lf.json` and `examples/section_lf_replace.json` are the same section with the same curve in the two modes.
- `measured`: `frequency_hz` with `spl_db` and `phase_deg`, or `real_pa` and `imag_pa`; `voltage_rms`, `distance_m`.
- `frd_file`: `file` in Hz / dB SPL / degrees, `voltage_rms`, `distance_m`; a two-column file gets minimum phase.

### Impedance kinds

- `resistive {r_ohm}`; `ribbon {r_ohm, parallel_l_mh}`; `resonant {re_ohm, le_mh, peak_r_ohm, peak_hz, peak_q}` for compression drivers and domes.
- `free_air {ts}`, `sealed {ts, net_volume_l, ql}`, `vented {ts, enclosure}`, `passive_radiator {ts, enclosure}` from Thiele/Small data.
- `curve {frequency_hz, real_ohm, imag_ohm}`; `zma_file {file}`; `reference {reference: {file, path}}` to read `results.curves.0.z_ohm` from an `lf_box` result.

## Output (`results`)

`f_hz`, `pressure_per_volt_pa` (complex record), `z_ohm` (complex record), `pressure_basis`, `impedance_basis`, echoed `directivity` and `acoustic_depth_mm`, `statistics` with the SPL at 2.83 V / 1 m, mean level in the sensitivity band and impedance minimum.

## Stating the gate on an imported measurement

A gated impulse response is valid only above roughly `1 / t_gate`: a 5.6 ms gate is trustworthy above about 180 Hz, and below that the data is not merely noisy, it is absent — replaced by whatever the near-field splice or the roll-off prior put there. Give `acoustic.gate_ms` with any `measured` or `frd_file` source and the document's `validity` block reports `gated_valid_above_hz` with a sentence saying so. Omit it and the block says the low-frequency validity limit is unknown, which is what a response quoted without its gate actually means.

`piston_radius_mm` is optional and adds the `ka = 1` frequency to the same block.

## Explicit LF drive basis and acoustic calibration

`acoustic.voltage_basis` for `lf_box` is `source` (legacy default) or `driver_terminal`. The legacy pressure includes any box-drive series loss and says so in `pressure_basis`. Use `driver_terminal` when applying the physical crossover downstream: it removes the box's external series resistance by the complex factor `(Zdriver + Rs)/Zdriver`, keeping the exported impedance unchanged. The selected `results.curves.<index>` supplies its own drive voltage. A prefiltered box with `terminal_transfer` is rejected for terminal normalization; generate an unfiltered source and apply the network downstream. Prefer a zero-external-resistance source run and keep allowance/stress runs separately.

Optional `acoustic.level_calibration: {"gain_db": -2.0, "basis": "source, conditions, band and derivation"}` scales acoustic pressure only and is echoed in the output. It does not scale impedance, current, excursion, thermal predictions or ratings. The gain is an explicit prior/calibration, not evidence that a driver is mechanically different.

For LF boxes with an outlet, `results.outlet_pressure_per_volt_pa` carries the same drive normalization and calibration. It retains the box outlet shape rather than the cone's published upper-band replacement. When placing an outlet separately in `whole_speaker`, take the cone-only field as the source and reference this outlet output with `voltage_rms: 1`. Apply baffle/placement factors to both. Referencing raw box pressure instead bypasses the normalization/calibration and can silently misbalance the sum.

Before fitting, compare graph anchors and upper slope, deep bass, a unity source and a known resistor case. `framework/templates/simulation-audit.md` describes the evidence to retain.

`examples/section_lf_terminal.json` demonstrates terminal normalization and a declared acoustic calibration alongside the legacy multiplication and replacement examples. Its -2 dB gain is illustrative, not a measured driver claim.

## Phase, baffle and simulation-source contract

`acoustic.kind: simulation` reads a canonical `reference` pressure curve (default path `results.pressure_per_volt_pa`) and inherits its `source_contract`. The impedance input remains explicit, commonly a reference to that same model's `results.z_ohm`. This connects cavity and geometry-derived sources without another box correction.

`acoustic.contract.phase_reference` is `intrinsic` by default. For supplied common-observer complex data, set `common_observer`, `reference_distance_m` and `observer_position_m` in cabinet coordinates. The source removes the common reference delay; the radiation loader removes the reference geometry before propagating to a new observer, so relative path effects occur once. Magnitude-only reconstructed/zero-phase data does not contain that supplied timing information.

`contract.baffle` is `external` or `included`; applying an external baffle reference to an included source is a conflicting input. `measured` magnitude-only input defaults to reconstructed minimum phase, or uses `phase_assumption: zero` when explicitly supplied. FRD output identifies supplied, reconstructed or zero phase. `delay_s` separates a known delay during complex interpolation. Native source conditions and the exported contract remain part of interpretation.

Simulation imports inherit their angular directivity as well as their source
contract. `polar_import` supplies a measured two-plane source with explicit coverage
and acquisition timing. See [response preparation](../response_prepare/README.md)
and [polar import](../polar_import/README.md).

T/S inputs support `inductance_model` (`constant`, `leach`, `lr2`,
`semi_inductance`) and `creep`; the same laws feed the linear box, cavity, room
and distributed-loading solves. See [driver impedance](../../references/driver-impedance-identification.md).
