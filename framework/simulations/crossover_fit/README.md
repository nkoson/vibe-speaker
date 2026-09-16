# crossover_fit: fit crossover values to a target

Adjusts the marked component values of a passive crossover so that the coherent on-axis sum of the whole speaker (same geometry model as `whole_speaker`) approaches a target level curve in a band, optionally while keeping the input impedance above a figure you state. It searches inside the bounds you give and stops at the evaluation budget. You decide the topology, the bounds, the target and whether the result is good; it returns the values and the curves.

## Run

```
python framework/simulations/crossover_fit/run.py --input params.json --out results/ [--name fit_c01]
```

## Input

| Key | Meaning |
|---|---|
| `system` | A `whole_speaker` parameter block without `transfer` entries: `observer`, `cabinet`, `sections[]` with `source`, `position`, optional `baffle`, `rear_outlets`, `tilt_deg`. Order must match `sections` below |
| `sections[]` | Same records as `crossover_network` (`name`, `polarity`, `wire_loop_ohm`, `source`, `elements`). Any leaf element may carry `fit: true` (bounds x0.25 to x4 of the start value) or `fit: {min, max}` in the element's unit |
| `target.spl_db` | Number, `"auto"` (mean of the starting response in the band) or `{file, frequency_path, path}` to a real curve (for example a reference speaker's published response) |
| `target.band_hz` | Fit band, default [100, 16000] |
| `target.weights[]` | `{band_hz, weight}` multipliers inside the band |
| `target.min_input_impedance_ohm`, `target.impedance_weight` | Penalty on input impedance below the figure in 20 to 20000 Hz |
| `target.vertical_angles_deg` | Observation angles included in the objective, default `[0]` |
| `fit_frequencies` | Grid used during the search, default 240 log points over the band widened by half an octave each side |
| `frequencies` | Grid for the reported final curves, default 10 to 40000 Hz, 800 points |
| `max_nfev` | Least-squares iterations per polarity trial, default 150 |
| `max_objective_calls` | Hard cap on objective evaluations, default 4000 |
| `polarity_trials` | 1 keeps the declared polarities; larger values try upper-section sign combinations (up to 2^(N-1)) |

## Output (`results`)

- `fitted_values[]`: id, section, unit key, start, fitted, bounds and `at_bound`; `statistics.values_at_bound` lists the ones resting on a bound (a hint to widen the bound or change the topology).
- `fitted_sections[]`: the `sections` block with fitted values and chosen polarity, ready to paste into `crossover_network` and then `whole_speaker`.
- `attempts[]`: per polarity trial the cost, in-band RMS error and solver message; `selected_polarity`.
- `target_spl_db`, `start_spl_db` on `fit_f_hz`; `on_axis_spl_db`, per-section `transfer` and `spl_db`, `input_z_ohm` on `f_hz`.
- `statistics`: in-band RMS error and ripple after the fit, input impedance minimum, objective calls used, variable count.

The fit searches the topology and bounds you give it against the source files you built; it does not know whether either is sensible. `framework/references/crossover-design.md` lists what to settle before fitting (the level budget, impedance compensation, the acoustic target) and what to check in a fitted network before accepting it.

## Auditing what the fit landed on

`results.fitted_network_audit[]` runs `crossover_network`'s compensation audit and insertion loss on the **fitted** values, so the two questions that decide whether a fit is worth quantizing are answered in the same document: does each driver still look resistive across its crossover, and what did the real parts cost in level. Mark a Zobel or a notch with `"role": "compensation"` and name the crossover with `sections[].compensation_audit = {crossover_hz, octaves}`; add `sections[].passband_hz` for the insertion-loss figures.

Read it with `statistics.values_at_bound` before anything else: a value resting on a bound means the topology or the bound is wrong, not that the optimizer finished.
