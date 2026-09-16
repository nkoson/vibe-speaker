# cavity_modes: internal acoustics of the bass chamber

Solves the standing waves inside the rectangular bass chamber with the lining as damping, and couples the cone and the port or passive radiator to those modes. Reports the mode list with lined Q values, how much the cavity changes the cone's motion relative to the lumped model (`cone_deviation_db`), how much midrange leaks out of the port relative to the bass level (`outlet_relative_db`), the internal pressure envelope for the panel model, and optional pressure sections. Two bases are available: fast analytical rectangular modes for screening, and a 3D finite-volume basis that masks brace windows and port tubes for the finalist.

**The finite-volume basis is a wave-based solve, so the elements-per-wavelength rule applies to it.** `results.validity.mesh_rule` reports the maximum cell size `h = c P / (10 f_max)` at shape-function order `P` — 1 for this scheme — and whether the finest mesh used is inside it. The rule addresses interpolation error only: the pollution term of the error bound carries an extra factor of `k`, so a mesh that resolves the lowest modes is progressively less adequate as frequency rises, which is what the mesh convergence figures are for. And numerical accuracy is never agreement with measurement: quadratic elements at 10 degrees of freedom per wavelength reproduce analytic room modes to better than 0.1 %, and that says nothing about how far the answer sits from a microphone.

## Run

```
python framework/simulations/cavity_modes/run.py --input params.json --out results/ [--name cavity_c01]
```

The FVM basis with two meshes on a 150 L chamber takes tens of seconds.

## Coordinates

Internal coordinates of the chamber: x from the inside left wall, y from the inside front wall toward the rear, z from the inside bottom. The driver sits on the front wall; ports and radiators on the rear wall by default (`face: front` puts them on the front).

## Input

| Key | Meaning |
|---|---|
| `cavity.width_mm`, `depth_mm`, `height_mm` | Inside dimensions of the bass chamber |
| `cavity.braces[]` | Window braces: `z_mm` (bottom of the brace plane), `rim_mm` (solid rim width), `thickness_mm` |
| `cavity.lining` | `thickness_mm`, `flow_resistivity_pas_m2` (10000 is a typical polyester or fiberglass batt; 20000 is denser) |
| `cavity.unlined_background_q` | Background modal Q without lining, default 30 |
| `driver.ts`, `driver.position {x_mm, z_mm}` | Woofer data and cone centre on the front wall |
| `outlet` | `{type: port, face, positions [{x_mm, z_mm}], inner_diameter_mm, outer_diameter_mm, length_mm, qp}` or `{type: passive_radiator, face, position, radiator, added_mass_g}`; omit for a sealed chamber |
| `enclosure` | `net_volume_l`, `tuning_hz`, `ql`, `qp` (same figures as `lf_box`) |
| `drive` | `voltage_rms`, `series_resistance_ohm`, optional `terminal_transfer` reference |
| `method.kind` | `rectangular` or `fvm` |
| `method.mesh_mm` | List of cell sizes for `fvm`, coarse to fine; two or more meshes produce `mesh_convergence` |
| `method.max_mode_hz` | Modal basis upper limit, default 1800 |
| `frequencies` | Optional grid; default 20 to 100 Hz log plus 100 Hz to `max_mode_hz` linear |
| `field_sections` | `{frequencies_hz: [...], x_mm}` pressure sections through the plane x (default through the first outlet) |

## Output (`results`)

- `bases[]`: per basis the method, mode count, `first_modes_hz`, `modes[]` (frequency, lined Q, cone and outlet couplings), maximum cone deviation in 150 to 1000 Hz, maximum outlet leakage above 300 Hz, cells and modeled air volume for FVM, `pressure_envelope_rms_pa` (maximum over all cells per frequency) and its maximum.
- `cone_deviation_db`, `outlet_relative_db`, `cavity_spl_db` versus `lumped_spl_db`, `driver_z_ohm`, `box_pressure_at_cone_pa`, `pressure_envelope_rms_pa` of the finest basis on `f_hz`.
- `unlined_comparison`: the same figures with the lining removed.
- `mesh_convergence`: relative change of the first ten modes, maximum change of cone deviation and outlet leakage between the two finest meshes.
- `field_sections[]`: cell coordinates and pressure in the section plane at each requested frequency.

Feed `results.pressure_envelope_rms_pa` (with `frequency_path: results.f_hz`) to `plate_structure` as the panel load. Scale it to your drive voltage: the envelope is linear in voltage.
