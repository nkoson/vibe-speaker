# directivity: source coverage versus frequency and angle

Evaluates the analytical directivity models used by `whole_speaker` so you can compare woofer beaming with horn or dome coverage around a crossover frequency before building a full candidate.

## Run

```
python framework/simulations/directivity/run.py --input params.json --out results/
```

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 200 to 20000 Hz, 200 log points |
| `horizontal_angles_deg`, `vertical_angles_deg` | Angle lists, default 0 to 90 in 5 degree steps |
| `sources[]` | `{name, directivity}` with the same model records as `source_response`, plus optional `os_waveguide: {throat_radius_mm, half_angle_deg, axial_positions_mm}` |

## Output (`results`)

Per source: `horizontal_db[angle][frequency]`, `vertical_db[angle][frequency]` relative to on axis, and `beamwidth_6db_deg[frequency]` (horizontal included angle; 360 when the model never falls 6 dB).

Read the woofer's beamwidth at the intended crossover and compare it with the horn's nominal coverage; the difference is the directivity mismatch you weigh in the design.

## The one source whose geometry is used rather than described

Give a source an `os_waveguide` block and the result carries the oblate-spheroidal contour `r(x) = sqrt(rt^2 + tan^2(theta0) x^2)` sampled at the axial positions you ask for, the mouth radius and area it reaches, and the cutoff

```
fc = 0.2 c sin(theta0) / (pi rt)          theta0 = HALF the included coverage angle
```

Verification bar: a 1-inch throat (`rt = 12.7 mm`) at a 60-degree included angle gives 862 Hz. Where the source also declares a Gaussian coverage the app reports whether the contour's included angle matches it, which catches a waveguide described with one angle and drawn with another.

**An OS waveguide has no sharp cutoff.** The figure above is the 0.2-of-asymptotic-throat-resistance convention, so it means roughly what exponential-horn cutoff means and nothing more. A low cutoff needs a big throat or a narrow angle, which is why OS waveguides are poor at low frequencies. Throat impedance for this contour has no closed form and is deliberately not computed here or anywhere else in the framework; see `horn_design` for why, and for the design arithmetic that is worth computing.
