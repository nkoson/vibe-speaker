# transmission_line: tapered line length, modes and driver offset

Length and mode arithmetic for a tapered quarter-wave line: `L = SF c / (4 fb)` with the published taper-factor table, the reduced speed of sound in a stuffed line, the mode series, and the driver offsets that place the cone on a velocity node of a higher mode.

**Deliberately low priority, and the source's own conclusion is why:** at equal volume and equal tuning a transmission line gives **no deeper bass** than a reflex box. The loading buys cone-displacement control and low terminus velocity, not extension. If extension is the objective, `lf_box` settles it in one vented run at the same volume and tuning.

## Run

```
python framework/simulations/transmission_line/run.py --input params.json --out results/
```

## Input

| Key | Meaning |
|---|---|
| `line.tuning_hz` | The tuning the line is being designed to |
| `line.throat_area_cm2`, `line.terminus_area_cm2` | The taper ratio is terminus over throat: below 1 the line tapers down, above 1 it expands |
| `line.unstuffed_speed_m_s`, `line.stuffed_speed_m_s` | Defaults 342 and 319 m/s, the measured pair |

## Output (`results`)

- `taper`: the ratio, the interpolated `SF`, whether it sits inside the published 0.1 to 10 range, and the table itself.
- `lengths_m` / `lengths_mm`: the line length with the unstuffed speed, with the stuffed speed and with the framework's own `c`, plus `untapered_length_m` for comparison. **Never use `L = c / (4 fb)` for a tapered line**: `SF` spans 0.62 to 1.42 across the published taper ratios.
- `line_volume_l`: the mean-area volume of each, so the line can be compared against a reflex box of the same volume.
- `modes`: the tuned fundamental, the odd-harmonic estimate, and the geometric quarter-wave frequency of the length. The ratio between the last two is `SF`, which is why they have to be reported apart or the length looks wrong.
- `driver_offset.options[]`: the fraction along the line at which the cone sits on a velocity node of the 3/4-wave and 5/4-wave modes, derived from the closed-open geometry, with the distance in millimetres. The source says to offset the driver without stating where; these fractions are the derivation.
- `comparison`: the equal-volume conclusion, stated where a reader will meet it.

## Limits

Length arithmetic, not a response. Nothing here predicts the level, the ripple or the group delay of the line, and `lf_box` does not model a transmission line at all. The taper table and the stuffed speed come from one self-published modelling site, and the advantages claimed for the loading are asserted there without numbers.
