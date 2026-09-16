# response_metrics: curve statistics and comparisons

Resamples one or more response curves (simulation results or published points) onto a common grid, optionally smooths them, and reports descriptive statistics: mean and median level in a band, ripple, standard deviation and slope per band, sustained low-frequency cutoffs, the band held within a tolerance, octave-band means, and pairwise differences with RMS, maximum, octave-band means and the fraction of the band within given limits. Use it to score candidates consistently and to compare a candidate with a reference speaker's published curve.

## Run

```
python framework/simulations/response_metrics/run.py --input params.json --out results/ [--name metrics_c01]
```

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Common grid, default 20 to 20000 Hz, 600 log points |
| `analysis.smoothing_octaves` | Fractional-octave smoothing width (0 = none, 1/6 = .1667 for published-style curves) |
| `analysis.sensitivity_band_hz`, `ripple_bands_hz`, `reference_band_hz`, `cutoff_thresholds_db`, `band_tolerance_db`, `upper_reference_hz` | Statistic settings |
| `curves[]` | `{name, curve, file, frequency_path, path, offset_db}` for a simulation curve (a complex record is read through its `magnitude_db`), or `{name, points: [[hz, db], ...]}` for a published curve. `curve` names which of the seven CTA curves this is — `on_axis`, `listening_window`, `early_reflections`, `predicted_in_room`, `sound_power`, `early_reflections_di`, `sound_power_di` — so the metrics are named with the patent's own code; without it the curve's own name is used and the metrics are flagged as not comparable with published figures |
| `comparisons[]` | `{a, b, band_hz, align: none|mean_in_band, within_db: [...]}`; the difference is a minus b, after shifting a by the band-mean offset when aligned |

## Output (`results`)

Per curve: resampled `spl_db`, `source_coverage_hz`, `statistics` (means, ripple, std, slope, cutoffs with bound flags, `band_within_tolerance`, level at the upper reference, `octave_bands`). Per comparison: `difference_db`, `rms_difference_db`, `max_abs_difference_db` with frequency, `mean_difference_db`, `octave_band_differences`, `fraction_of_band_within_db`.

## The preference predictors, and what they are worth here

Every curve gets `preference_metrics`, and **every metric is named with the curve it came from** — `NBD_ON`, `SM_PIR`, `AAD_LW`. NBD, SM and AAD are each defined over any of the seven curves, so a bare `NBD` names nothing:

- **NBD**, narrow band deviation: the mean over half-octave bands, 100 Hz to 12 kHz, of the mean absolute deviation inside each band, ten log-spaced samples per band. It measures wiggle at the scale of a half octave and is blind to a slow trend, which is the point — a monotonic tilt costs almost nothing in the preference model and a 1 dB wiggle inside one half-octave costs directly. It is a better statistic than the per-band standard deviation next to it, and far better than a peak-to-peak ripple figure, which gives a 3 dB slow tilt and a 3 dB narrow notch the same number.
- **SM**, smoothness: the `r^2` of a straight-line fit of level against log frequency, 100 Hz to 16 kHz, with the slope and the residual reported beside it. Because the line is allowed to slope, SM polices scatter and not tilt, and a design with a large total tilt can score well; it is the weakest and most easily gamed of the four predictors.
- **AAD**, absolute average deviation: the mean absolute deviation from the 200 to 400 Hz mean level over 1/20-octave bands, 100 Hz to 16 kHz. It belongs to the patent's earlier model form and carries **zero weight** in the generalized four-term model. It is computed so that an older published score using AAD can be recognised for what it is rather than mistaken for NBD, which is a different quantity over different bands.

**LFX and LFQ are defined on sound power and the listening window only**, never on an axial curve. LFX needs two curves, because it is defined on the sound power against the listening-window mean. Name them with `analysis.lfx = {sound_power_curve, listening_window_curve}` and the result carries the frequency, its `log10` and how the bound resolved. An on-axis `f3` is not LFX and is usually the more flattering of the two, so do not compare one with published figures as if it were the other. LFX carries no penalty for Q, group delay or distortion, so it rewards a boomy high-Q alignment exactly as much as a clean one.

Naming `analysis.lfx` also produces **LFQ**, the mean absolute deviation of the listening-window curve between LFX and 300 Hz, which the patent computes and the generalized regression gives zero weight.

**The definitions are not the approximation; the curve set is.** All four were read at first hand in Harman's patent, so the formulas are not hedged. What is hedged is the orbit: every metric is labelled `standard_conformance: approximation` unless you override it, because a CTA-2034-A figure needs a complete 70-point orbit and this application only ever sees the curves you hand it. Never report one as a CTA-2034-A or Olive figure. No preference score is computed here at all: two of its four terms are directivity measurements and neither exists without the orbit. Use `spinorama` for that.

Extra input keys: `analysis.nbd_band_hz`, `analysis.sm_band_hz`, `analysis.lfx`, and `curves[].standard_conformance`.
