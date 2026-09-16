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
