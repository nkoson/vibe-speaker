# spinorama: CTA-2034-A curve family and the Olive preference predictors

Assembles the full 70-point two-plane orbit from the same section model `whole_speaker` sums, and computes the listening window, the five early-reflection groups, sound power, the predicted in-room response, both directivity indices and the four Olive predictors with the preference score. It is the only place in the framework where a candidate is scored the way the published listening research scores one.

**Two levels of confidence apply and must not be conflated.** The curve-assembly geometry — which angles go in which group, and the ring weights — rests on one open-source reimplementation of a paywalled standard, with two known discrepancies exposed as options. The four predictors and the regression that combines them were read at first hand in Harman's own patent, so those formulas are not hedged. What remains hedged is the orbit: it is modelled, not measured.

**Every computational detail of the curve family comes from one open-source reimplementation of ANSI/CTA-2034-A**, not from the standard text, which is paywalled and was not read; the predictors do not, as above. Two of its details are known to differ from the literal standard and are exposed as options; the legacy option named `standard` is retained for compatibility; it is not independent certification against the standard text.

## Run

```
python framework/simulations/spinorama/run.py --input params.json --out results/
```

## Input

The section, cabinet and observer blocks are the same as `whole_speaker`'s, so a system already described for it needs only `rear_radiation` added.

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 20 to 20000 Hz, 600 log points. It must cover 100 Hz to 16 kHz for NBD and SM, and reach low enough for LFX to resolve |
| `observer.distance_m`, `observer.ear_height_m` | The orbit is computed on a sphere of this radius about the reference point |
| `cabinet.depth_mm`, `cabinet.floor_offset_mm`, `cabinet.baffle_width_mm` | As `whole_speaker`, plus the width that supplies a default rear-radiation corner |
| `sections[]` | As `whole_speaker`: `source`, `transfer`, `baffle`, `position`, `tilt_deg`, `rear_outlets` |
| `sections[].rear_radiation` | **Required for a score.** `{kind: "shadowed_monopole", corner_hz \| baffle_width_mm, floor_db (default -20), order (default 1)}` |
| `options.rear_wall` | `standard` (default: only +/-90 and 180 degrees) or `reimplementation` (the +/-90 to +/-170 fan) |
| `options.double_90_degree_weight` | `false` (default) or `true` |
| `analysis.nbd_band_hz`, `analysis.sm_band_hz` | Defaults 100-12000 and 100-16000 Hz |
| `analysis.lfx_upper_hz`, `analysis.lfx_reference_band_hz` | Defaults 300 Hz and 300-10000 Hz |
| `analysis.directivity_index_band_hz` | Window the DI statistics are taken over, default 500-10000 Hz |

### The rear-hemisphere prior, and why the score depends on it

For a front-only analytic pattern without a declared `rear_radiation` prior, a section contributes nothing at or behind 90 degrees from its axis, which is the infinite-baffle idealisation: correct for an infinite baffle, wrong for a real box at low frequency where the cabinet is small compared with a wavelength and radiates in every direction.

The prior is unity well below its corner and falls to `floor_db` above it, blended linearly in `cos(polar angle)` from the front hemisphere so the pattern is continuous at 90 degrees. The default corner is `c / (2 W)` from the baffle width. It is a declared prior with no measurement behind it, a BEM solve is what would replace it, and the sound power carries about a third of its weight in the 90-degree ring alone — so every figure derived from sound power inherits that uncertainty.

**A section needs a rear prior or a complete radiation model.** Omnidirectional, dipole, cardioid, angular edge-dipole, complete measured-plane and complete complex-grid sources can supply the full orbit without a shadow prior. Otherwise the orbit is incomplete and no score is emitted. The curves are still written, labelled as front-hemisphere approximations, and `results.preference_withheld` names the sections responsible.

## Output (`results`)

- `orbit`: point count, whether it is complete, the sections without a prior, any silent points, and the priors used.
- `options_used`: the two flagged discrepancies against the standard text, in full, with what was selected.
- `curves`: `on_axis`, `listening_window`, `early_reflections`, `sound_power`, `predicted_in_room` and the five `early_reflections_*` groups, all in dB at the input voltage.
- `sound_power_di_db` (`LW - SP`) and `early_reflections_di_db` (`LW - ER`).
- `horizontal`, `vertical`: the raw orbit curves at every angle.
- `predictors`: `nbd`, `smoothness` and `aad` for the on-axis, listening-window, early-reflections, sound-power and in-room curves, plus `lfx` and `lfq`. **Every metric is named with the curve it came from** — `NBD_ON`, `SM_PIR`, `AAD_LW` — because NBD, SM and AAD are each defined over any of the seven curves and a bare `NBD` names nothing; `predictors.named` lists every name emitted. LFX and LFQ are defined on sound power only. Each carries `standard_conformance`.
- `preference`: the score, the four weighted terms, the coefficients, the metric names the terms were taken from, and the patent's own **relative contributions — NBD_ON 31.5 %, LFX 30.5 %, NBD_PIR 20.5 %, SM_PIR 17.5 %** — so a reader can see which term moved the score. Emitted **only when the orbit is complete**; otherwise `preference_withheld` with the reason.
- `directivity_index_window`: min, max, mean and slope of `SPDI` over the requested band, with the ITU-R BS.1116-3 and EBU Tech 3276 windows quoted and their disagreement stated.

## What the score is and is not

Olive's generalized regression over seventy loudspeakers, evaluated on modelled curves rather than on anechoic measurements. It ranks; it does not certify. LFX carries about 30 percent of the model on its own and penalises nothing about Q, group delay or distortion, so it rewards a boomy high-Q alignment exactly as much as a clean one. SM is blind to tilt. A design optimised against this score alone will exploit both.
