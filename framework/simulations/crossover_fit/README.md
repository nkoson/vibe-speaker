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
| `ablation` | `true`, or `{max_nfev, max_objective_calls, elements[]}`. Removes one element at a time and refits the rest. Off by default |
| `stock` | `{"C": [...uF], "L": [...mH], "R": [...ohm]}`, or `stock` on an individual leaf. Enables the quantization report. Off by default |

## Output (`results`)

- `fitted_values[]`: id, section, unit key, start, fitted, bounds and `at_bound`; `statistics.values_at_bound` lists the ones resting on a bound (a hint to widen the bound or change the topology).
- `fitted_sections[]`: the `sections` block with fitted values and chosen polarity, ready to paste into `crossover_network` and then `whole_speaker`.
- `attempts[]`: per polarity trial the cost, in-band RMS error and solver message; `selected_polarity`.
- `target_spl_db`, `start_spl_db` on `fit_f_hz`; `on_axis_spl_db`, per-section `transfer` and `spl_db`, `input_z_ohm` on `f_hz`.
- `statistics`: in-band RMS error and ripple after the fit, input impedance minimum, objective calls used, variable count.
- `fitted_efficiency` and `fitted_parts`: what the fitted network loses and how many bodies it asks for, on the same definitions `crossover_network` uses, so both are visible while the topology can still change rather than after it is quantized.
- `ablation` when requested: `reference` (the fitted network's own error) and one `trials[]` row per element with `delta_rms_db` — what the rest of the network cannot recover once that element is gone.
- `quantization` when stock lists are given: each fitted value snapped to the nearest stock value with its error, the whole-network error and impedance minimum after snapping, and `sections` ready to paste.

## Asking what an element is worth

`ablation` removes one element at a time — a series element shorted, a shunt element opened, which is what leaving the part out of the build does — and refits every remaining free value before scoring. So `delta_rms_db` is not "how much does this element change the response" but "how much of its job can the rest of the network take over", which is the question that decides whether to buy it. Trials are sorted cheapest removal first.

A small or negative delta says the element is earning little **on axis, against this target, in this design**. It says nothing about impedance, component stress, off-axis behaviour or tolerance robustness: `input_z_min_ohm` is reported per trial for the first of those, and the rest need `crossover_network` and `whole_speaker` on the variant. Nothing is removed for you, and there is no threshold at which the app suggests removing anything — a part that buys 0.2 dB may be worth keeping in one design and not in another, and that judgement is the designer's.

The pass costs roughly one fit per element. The call budget defaults to `max_nfev × (variables + 2)` because a finite-difference jacobian costs one call per free value; when a trial reports a budget status its number is a floor on the achievable error, not a converged result.

## Quantizing to stock

Values are **not** constrained to the stock grid during the search: a fit pinned to a grid hides which direction a value wanted to move, and `values_at_bound` becomes unreadable. Instead the fit runs free and `quantization` snaps each value afterwards to the nearest stock value in log space, then evaluates the snapped network as a whole, because the errors interact and are not the sum of the individual snap errors.

A large `error_percent` on a small value is the usual sign that the stock list does not carry what this topology wants — a tweeter coil of 0.015 mH against a grid starting at 0.1 mH is a topology finding, not a rounding detail. Rerun `crossover_network` on `quantization.sections` with the real DCR and ESR of the parts before treating any of it as the design.

The fit searches the topology and bounds you give it against the source files you built; it does not know whether either is sensible. `framework/references/crossover-design.md` lists what to settle before fitting (the level budget, impedance compensation, the acoustic target) and what to check in a fitted network before accepting it.

## Auditing what the fit landed on

`results.fitted_network_audit[]` runs `crossover_network`'s compensation audit and insertion loss on the **fitted** values, so the two questions that decide whether a fit is worth quantizing are answered in the same document: does each driver still look resistive across its crossover, and what did the real parts cost in level. Mark a Zobel or a notch with `"role": "compensation"` and name the crossover with `sections[].compensation_audit = {crossover_hz, octaves}`; add `sections[].passband_hz` for the insertion-loss figures.

Read it with `statistics.values_at_bound` before anything else: a value resting on a bound needs investigation of the stock range, topology and target; a constrained optimum may legitimately rest there.

Use explicit fit bounds derived from actual stock values or realizable banks when designing a build. The default bounds around a seed are numerical conveniences. Set an explicit target from the bass-supported level; `auto` inherits the starting network's losses. After snapping, put the actual stock DCR, ESR and ratings into the realized parameter file and rerun the network and whole speaker. Record any missing stock fallback. For an impedance/level trade, compare actual coil/DCR choices rather than assuming lower DCR is always preferable.
