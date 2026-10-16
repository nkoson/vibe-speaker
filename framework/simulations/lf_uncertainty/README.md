# lf_uncertainty: spread of the bass model over tolerances

Runs `lf_box` physics many times with the driver and build parameters drawn from uniform spreads you declare, and reports percentiles of extension, excursion, port speed and impedance minimum. Use it to see how robust an alignment is to production variation before you commit to it.

## Run

```
python framework/simulations/lf_uncertainty/run.py --input params.json --out results/ [--name lf_unc_c01]
```

## Input

Same `driver.ts` and `enclosure` as `lf_box`, plus:

| Key | Default | Meaning |
|---|---|---|
| `drive.voltage_rms` | 2.83 | Drive for excursion and port speed |
| `draws` | 128 | Number of random draws |
| `seed` | 1 | Random seed, for reproducible documents |
| `spreads.fs_hz`, `qes`, `qms`, `vas_l`, `re_ohm`, `net_volume_l` | .12, .10, .15, .25, .03, .03 | Relative half-widths |
| `spreads.tuning_hz_abs` | 1.0 | Absolute tuning half-width in Hz |
| `spreads.ql_range` | [5, 20] | Leakage Q drawn uniformly in this range |
| `spreads.added_mass_g_abs` | 0 | Passive-radiator added mass half-width |
| `analysis.reference_band_hz`, `stress_band_hz`, `cutoff_thresholds_db`, `percentiles` | [150,300], [20,300], [-6,-10], [5,50,95] | Statistics settings |

## Output (`results`)

- `nominal_spl_db` and `spl_percentiles.p5/p50/p95` curves on `f_hz`.
- `summary`: percentiles of each sampled parameter and of `f6_hz`, `f10_hz`, `max_excursion_peak_mm`, `max_port_air_speed_peak_ms`, `impedance_min_ohm`; `total_draws` gives the denominator. Cutoff `resolved_draws` counts only resolved crossings; `bound_counts` separately reports `resolved`, `left_censored` and `no_sustained_pass`. `unresolved_draws` includes censored/no-pass draws. Cutoff percentiles are explicitly conditional on resolved draws and remain present as null when none resolve. Do not present them as all-scenario robustness or omit no-pass draws from a joint target assessment.
- `samples[]`: every draw with its parameters and metrics.

## The defaults, and why they are that wide

The spreads are sized to the **method spread of the measurement**, not to a catalogue tolerance: 25 percent on `Vas`, which is the middle of the reported 20 to 30 percent disagreement between measurement methods, and 12 percent on `fs`, the resonance shift that compliance spread implies at constant mass. `results.spread_basis` carries the reason for every default in the result document itself.

`Mms` is not drawn — it is derived from `fs` and `Vas` — so `results.derived_parameter_spread` reports the `Mms` and `Qts` spread the drawn parameters actually produced. Compare it with the reported 20 to 30 percent before believing either figure. A perturbation tighter than the thing it perturbs gives false comfort; one much wider is a sensitivity probe rather than a robustness figure. See `framework/references/measurement-and-model-limits.md` section 8 for realistic uncertainty versus deliberate probes.
