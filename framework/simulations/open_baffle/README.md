# open_baffle: dipole response, pattern and excursion demand

Makes the dipole option quantitative instead of a conversation: the equivalence frequency and the 6 dB/octave rolloff below it, the `cos(theta)` pattern, the H-frame cavity resonance, and — the number that decides whether the idea survives — the volume displacement an open baffle needs to reach a stated SPL, which rises at 18 dB per octave rather than the monopole's 12.

A `cardioid` block turns the same machinery on the first-order gradient pair: the pattern `D = 1 + cos(theta)`, and the two limits that bound its band. Both limits are physics; the reported 2 to 2.5 octave practical passband is from a patent specification, not a measurement series. The realisation most passive cardioid cabinets actually use — a resistive rear vent rather than a second driver — has no published alignment mathematics and is **not** modelled.

## Run

```
python framework/simulations/open_baffle/run.py --input params.json --out results/
```

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 10 to 2000 Hz, 500 log points |
| `model` | `equivalence` (default, the sourced engineering form) or `point_dipole` (the exact two-monopole result, which keeps the peak and the null) |
| `baffle.path_mm` | **The front-to-back acoustic path**, the route the rear wave takes around the panel — not the baffle width |
| `cavity.depth_mm` | Optional H-frame or U-frame cavity depth |
| `angles_deg` | Pattern angles, default 0 to 90 in 15-degree steps |
| `driver.sd_cm2`, `driver.xmax_mm` | For the excursion table |
| `target.spl_db_at_1m`, `target.space`, `target.frequencies_hz` | The output the design is being asked for |

## Output (`results`)

- `geometry`: the equivalence frequency `f = 0.17 c / D`, the first peak at `c / (2 D)` and the first null at `c / D`. All three describe the same geometry.
- `relative_response`, `relative_response_db`, and both model curves side by side so the difference between them is visible.
- `pattern`: `cos(theta)` in dB — about 1 dB down at 30 degrees, 3 at 45, 6 at 60 — with the 4.8 dB of power a dipole gives up against a monopole at the same on-axis SPL.
- `cavity_resonance`: `F = 0.25 c / L`. It caps the usable band, and no source consulted states how far below it to cross, so that margin is a judgement to state.
- `excursion_demand.rows[]`: per frequency, the volume displacement a dipole and a monopole each need for the target SPL, the penalty ratio between them, the peak excursion one cone would have to make, and how many cones that is at the stated `xmax_mm`.

## The number to look at first

`excursion_demand`. One octave lower at constant SPL costs **eight times** the volume displacement, against four times for a monopole. That is the dominant fact in dipole woofer sizing and it is usually what settles the question before any of the pattern's benefit is discussed. Price the removed output — the 4.8 dB power deficit, the rolloff and the displacement — before committing to the loading.
