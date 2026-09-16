# baffle_diffraction: finite-baffle transfer

Complex on-axis factor that a rectangular front baffle applies to each source mounted on it: the 6 dB baffle step and the edge-diffraction ripple, plus the optional transfer of a recessed tweeter carrier. Multiply a section's infinite-baffle (2 pi) pressure, which is what `lf_box` with `space: half` produces, by this factor, or hand the result file to `whole_speaker` through its `baffle` reference. Datasheet curves of horns and tweeters were measured on some baffle already; apply the factor to them only when you judge the datasheet condition differs from your cabinet.

## Run

```
python framework/simulations/baffle_diffraction/run.py --input params.json --out results/
```

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 20 to 20000 Hz, 400 log points |
| `baffle.width_mm`, `baffle.height_mm` | Front panel outside dimensions |
| `observer_distance_m` | Observer on the source axis, default 3 m |
| `segments` | Perimeter segments for the edge sum, default 96 |
| `baffle.edge_radius_mm` | Roundover radius of the panel edges, default 0. A per-source `edge_radius_mm` overrides it |
| `sources[]` | `name`, `model` (`edge_diffraction`, `shelf` or `none`), `x_mm` and `z_mm` of the source centre measured from the baffle's left and bottom edge, `radius_mm` or `sd_cm2` for the piston beaming toward the edges, optional `edge_radius_mm`, optional `recess {setback_mm, opening_width_mm, opening_height_mm}` |

## Output (`results`)

`shelf_corner_hz` (`115 / W`) and `allison_full_support_hz` (`c / 2W`) for the width — the two name different points on a transition that spans roughly a decade, so read the computed curve rather than either number. Per source: `baffle_factor` (complex record; 0.5 at low frequency is the 4 pi limit), `relative_to_2pi_db` (0 dB means full baffle support, -6 dB none, positive values are diffraction peaks), `far_field_factor` and `far_field_relative_to_2pi_db`, `recess_transfer` and `combined_factor` when a recess was given.

- `sources[].step`: the depth of the step **at the stated observation distance** and **in the far field**, with the difference between them. The step is distance-dependent: a 250 mm baffle with a centred source shows about 5 dB at 0.25 m against 6 dB far field, because an edge wave reaches a near observer over a longer path than the direct sound and is therefore weaker. A correction derived at one distance and applied at another under- or over-compensates by exactly that difference, which is why a near-field splice wants two diffraction corrections, one at each distance.
- `sources[].edge_radius_effective_above_hz`: `c / (8 r)`, the lambda/8 frequency above which a roundover can act at all. Below it the edge is acoustically square whatever it looks like.

The full 6 dB step belongs to a speaker in free space. In a normal room the walls restore part of the low-frequency support and the realised step is unlikely to exceed about 3 dB, so how much to compensate is a voicing decision to state, with the free-space and in-room endpoints known. Compensating on axis tilts the off-axis and power response the other way.

Downstream reference: `{"file": "baffle.json", "frequency_path": "results.f_hz", "path": "results.sources.0.baffle_factor"}`.
