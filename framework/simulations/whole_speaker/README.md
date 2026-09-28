# whole_speaker: coherent system response

Sums every section of a candidate at the listening position: each section's free-field pressure per volt (from `source_response`), times its electrical transfer (from `crossover_network`, `board_nodal` or an ideal filter), times its baffle factor (from `baffle_diffraction`), radiated from its acoustic centre with its directivity model. Returns on-axis SPL with per-section contributions, horizontal and vertical maps, acoustic crossing points, path differences, optional floor-image cases, polarity permutations and acoustic-depth perturbations.

## Run

```
python framework/simulations/whole_speaker/run.py --input params.json --out results/ [--name system_c01]
```

## Coordinates

x lateral in mm from the cabinet centre line, z height in mm above the floor (cabinet bottom plus `cabinet.floor_offset_mm`), depth in mm behind the front face. The observer sits at `observer.distance_m` in front of the cabinet at `observer.ear_height_m`. Horizontal angles swing the observer around the vertical axis; vertical angles swing it up and down about the front centre.

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 20 to 20000 Hz, 600 log points; keep it inside the source grids |
| `input_voltage_rms` | Drive for SPL figures, default 2.83 |
| `observer` | `distance_m` (3), `ear_height_m` (1), `horizontal_angles_deg` (-90..90 step 5), `vertical_angles_deg` (-30..30 step 5), optional `horizontal_window_deg` / `vertical_window_deg` for window statistics |
| `cabinet` | `depth_mm` (for rear outlets), `floor_offset_mm` (plinth or feet) |
| `sections[]` | One entry per section, see below |
| `floor` | `{reflection, cases: [{distance_m, ear_height_m, reflection}]}` single coherent floor image |
| `polarity_study` | `true` evaluates every sign combination of the upper sections on axis |
| `arrays` | `{coherent_radiating_height_mm, border_frequencies_hz, groups: [{name, count, spacing_mm, upper_hz, band_hz, source: {radiating_diameter_mm}, frame_width_mm, frame_height_mm}]}` — the criteria for sources reproducing the **same** band, which the pair geometry does not cover |
| `analysis` | `ripple_bands_hz` (default [[100, 16000]]), `sensitivity_band_hz` ([500, 10000]), `reference_band_hz` ([150, 300]), `cutoff_thresholds_db`, `band_tolerance_db`, `crossing_search_band_hz`, `depth_perturbation_mm` |

`depth_perturbation_mm` is either one figure applied to every section, or an object keyed by section name so that each section is perturbed by an amount its own mounting makes plausible; a section left out, or given 0, is not perturbed. A shift larger than a section's own `acoustic_depth_mm` moves its acoustic centre in front of the baffle, which probes how steeply the summation degrades rather than describing a mounting, so each row carries the `acoustic_depth_mm` it was applied to.

### Section

| Key | Meaning |
|---|---|
| `name` | Label |
| `source` | `{file}` of a `source_response` result; supplies pressure per volt, directivity and acoustic depth. `pressure_path` overrides the curve path |
| `pressure_per_volt` | Alternative `{file, frequency_path, path}` reference to any complex pressure-per-volt curve |
| `transfer` | `{file, path}` to `results.sections.N.transfer` of `crossover_network`, to `results.modes.M.loads.N.transfer` of `board_nodal`, or `{ideal: {type: linkwitz_riley|butterworth, order, low_hz, high_hz, gain_db, polarity, delay_ms}}`; omitted = unity |
| `baffle` | `{file, path}` to `results.sources.N.baffle_factor` of `baffle_diffraction`; omitted = unity |
| `position` | `x_mm`, `z_mm`, optional `depth_mm` (overrides the source file's acoustic depth) |
| `directivity` | Overrides the source file's model |
| `tilt_deg` | Vertical aiming of the source axis, positive up |
| `rear_outlets[]` | Ports or passive radiators fed by this section: `pressure {file, path}` (`results.curves.0.outlet_pressure_pa` from `lf_box`), `voltage_rms` of that curve, `positions [{x_mm, z_mm}]`, `face` (`rear` or `front`), optional `baffle` reference and `directivity` (piston for a passive radiator). When you use outlets, give the section the cone-only pressure (`cone_pressure_pa`) so the outlet is not counted twice |

## Output (`results`)

- `on_axis`: `spl_db`, `phase_deg`, complex `pressure`, `power_sum_db` (incoherent sum, for reading interference loss), `sections[]` with each section's `spl_db` and `phase_deg`.
- `geometry[]`: acoustic centres and distances; `path_differences[]` between sections in mm and microseconds.
- `horizontal`, `vertical`: `angles_deg`, `spl_db[angle][f]`, `relative_to_axis_db`, window statistics when requested.
- `floor_cases[]`, `polarity_study.cases[]` (signs, curve, ripple and mean in the first ripple band), `depth_perturbations[]`.
- `arrays`: see below.
- `statistics`: ripple and mean per band, sensitivity-band mean and median, sustained low cutoffs relative to the reference band, `band_within_tolerance`, `acoustic_crossings[]` (frequency where adjacent sections are equal and their level there), `section_presence[]` (band where each section dominates and how far below the sum it sits there).

## Pair geometry: the prediction that was available before the fit

`results.pair_geometry.pairs[]` is three lines of arithmetic over positions the model already holds, and it turns the vertical map from a diagnosis into a prediction. Per adjacent pair:

- `spacing_mm` (`d1`, centre to centre in the baffle plane) and `depth_offset_mm` (`d2`, between the acoustic centres);
- `null_frequency_hz = c / (2 d1)` — the lowest frequency at which the pair can null at all. Below it the pair still tilts and narrows its lobe, but it cannot null;
- `spacing_bound_hz = c / d1` — Linkwitz's `d1 / lambda = 1` bound, above which the pattern breaks into multiple beams. It is an **upper bound, not a target**: at exactly one wavelength the pattern is already badly compromised;
- `lobe_tilt_deg = arctan(d2 / d1)` and `offset_delay_us = d2 / c` — the tilt the depth offset produces and the pure delay that would correct it, which a passive network generally cannot supply. In a passive design the offset is handled mechanically or accepted as tilt and stated;
- `at_crossings[]` — `d1 / lambda` at each acoustic crossing the statistics found for that pair.

## The same-band case, and the measurement distance nobody checks

The pair geometry above governs drivers that cross over to **each other**. `results.arrays` governs the other case: two or more sources reproducing the **same** band — the woofers of an MTM, a stacked pair, a column. This model sums sections, and a driver pair inside one section is a single point source to it, so the groups are **declared** in `arrays.groups` rather than inferred.

- `groups[].spacing`: the `lambda/2` criterion as a pass or fail, with `half_wavelength_limit_hz = c / (2 d)` — the frequency above which the group stops being one source. For an MTM with 180 mm between woofer acoustic centres that is **953 Hz, and that is the number that should set the crossover before any fitting happens.**
- `groups[].active_radiating_factor`: the radiating area as a fraction of the array's frame against the 80 % criterion, with the reason circular sources cannot meet it — touching circles average `ARF = pi/4 = 78.5 %` before any flange or gap is allowed for. The paper's own conclusion is that this is precisely what a waveguide is for.
- `criteria`: the five WST criteria as stated, including why criteria 1 and 2 are alternatives.
- `near_field`: the border `d_B = (3 F H^2 / 2) sqrt(1 - (1/(3 F H))^2)` at each frequency against **the distance this result was computed at**, and the frequency above which the observer is inside it. Inside `d_B` level falls 3 dB per doubling rather than 6, and polar data is not a far-field property at all: for a 1 m tall coherent radiating section the border is about 1.4 m at 1 kHz and about **15 m at 10 kHz**. There is no near field below `F = 1/(3H)`, so an array does not control its own bass however tall it is.

**Read the near-field caveat before quoting the border.** The formula is derived for a line source of height `H` radiating an isophasic wavefront, and a conventional multiway is not that. Give the height of the **coherent radiating section**, not the cabinet, and read the result as an indication of where far-field assumptions become safe rather than as a computed border for this geometry.

Compute these before choosing a crossover frequency. A crossover chosen first will simply be reported as a poor vertical window afterwards.

## Rear radiation

`sections[].rear_radiation` declares what happens behind the cabinet: `{kind: "shadowed_monopole", corner_hz | baffle_width_mm, floor_db, order}`. Without it a section contributes nothing at or behind 90 degrees from its axis, which is the infinite-baffle idealisation. It changes nothing on axis or in a normal off-axis window, and it is required by `spinorama` for a complete orbit.

## Source and evaluation consistency

The result is already normalized using reference distance versus actual path distance; do not add a second listening-distance-to-1 m SPL correction. Check a unity section against its source and baffle. A source calibrated or terminal-normalized by `source_response` exposes `outlet_pressure_per_volt_pa`; use that for the same section's outlet with `voltage_rms: 1`, and use cone-only pressure for the main source.

At a hump or dip, inspect `on_axis.sections` complex pressures and reconstruct their coherent sum before blaming a driver's raw response. Label system cutoffs with their threshold/reference band and bound, keep fixed-frequency bass levels alongside them, and report trough/plateau margins where small level changes move a cutoff. Choose depth scenarios from stated acoustic-center uncertainty; larger probes and common/relative shifts answer different questions.
