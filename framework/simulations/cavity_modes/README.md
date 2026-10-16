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
| `cavity.braces[].holes` | Optional circular apertures `[{x_mm, y_mm, diameter_mm}, ...]`, in cavity-local coordinates. Replaces the rectangular window in the FVM mask. An empty list is a solid partition; keep apertures open to avoid disconnected air domains. |
| `cavity.lining` | `thickness_mm`, `flow_resistivity_pas_m2` from the material's datasheet or a measurement. Measured values found: about 2300 for a light glass wool and 4300 for polyester fibre at 30 kg/m³; lighter loudspeaker fills are lower still ([cabinet construction](../../references/cabinet-construction.md) section 9.2). When omitted it defaults to 10000, which is denser than those measured fills. The Miki lining model is stated valid for `0.01 < f / σ < 1` |
| `cavity.unlined_background_q` | Background modal Q without lining, default 30 |
| `driver.ts`, `driver.position {x_mm, z_mm}` | Woofer data and cone centre on the front wall |
| `outlet` | `{type: port, face, positions [{x_mm, z_mm}], inner_diameter_mm, outer_diameter_mm, length_mm, qp}` or `{type: passive_radiator, face, position, radiator, added_mass_g}`; omit for a sealed chamber |
| `outlet.positions[].face` | Per-port override: `front`, `rear`, `left`, `right`. Side ports specify `y_mm` and `z_mm`; front/rear specify `x_mm` and `z_mm`. The model averages their modal coupling into one shared outlet flow state. |
| `outlet.internal_length_mm` | Physical protrusion from the inside wall to the duct's inner end. Defaults to `length_mm` for compatibility. `length_mm` remains the total acoustic duct length. |
| `outlet.inner_mouth_diameter_mm`, `inner_flare_outer_diameter_mm`, `inner_flare_length_mm` | Optional inner-mouth averaging disk and cylindrical flare-block occupancy. Duct impedance still uses the throat diameter and declared equivalent length; use `distributed_loading` to establish a tapered duct's equivalent. Defaults preserve straight-tube geometry. |
| `outlet.inner_end_correction_mm` | Explicit additional inlet length. Default is zero for the FVM basis with its static residual, which owns the inlet near-field inertia; the truncated analytical basis retains `0.61 × throat radius`. An explicit value overrides this choice. Do not add a lumped correction to inner-mouth loading already resolved by the field. The exterior piston radiation impedance remains separate. |
| `outlet.segments` | Optional constant-area acoustic segments, ordered from inside mouth to exterior: `[{length_mm, diameter_mm}, ...]`. Lengths must sum to `outlet.length_mm`. Cascaded reciprocal two-ports retain taper/duct propagation; declare a profile prior when a maker does not publish the internal contour. |
| `outlet.outer_mouth_diameter_mm` | Exterior radiation aperture diameter; defaults to throat diameter. This is the open mouth, not the mounting flange. |
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
- `excursion_peak_mm`, `port_air_speed_peak_ms`: direct drive-conditioned displacement and maximum plane-wave speed across the declared duct segments; do not recover these by dividing pressure curves near cone nulls. `port_model` records the segment lengths and end-correction ownership.
- `field_sections[]`: cell coordinates and pressure in the section plane at each requested frequency.

Feed `results.pressure_envelope_rms_pa` (with `frequency_path: results.f_hz`) to `plate_structure` as the panel load. Scale it to your drive voltage: the envelope is linear in voltage.

## Shared geometry and canonical source export

An optional `assembly` record/file uses the shared metre-based geometry schema. In FVM mode its air-minus-solid mask is evaluated in the cavity coordinate frame. Keep the assembly and `cavity` bounds/datum consistent, and inspect the reported air-volume refinement.

`results.pressure_per_volt_pa`, `outlet_pressure_per_volt_pa` and `z_ohm` are exported from a separate unity terminal-voltage solve with zero external series resistance. They are independent of the stress-drive settings and carry a source contract. Use cone pressure plus a separately positioned outlet, or an explicitly combined source, to retain one copy of each radiator. The supported frequency band follows the actual result grid.

`export_complex_field: true` adds FVM coordinates and complex pressure samples for spatial loading studies. This is distinct from the maximum-pressure envelope used by the older isolated-panel screen.

For tapered-port occupancy, optional `outlet.outer_segments` gives `{length_mm, diameter_mm}` segments from the inner mouth towards the outer mouth. Only the part inside the chamber is excluded from the FVM air domain. These outside diameters describe solid/duct displacement; they are separate from the acoustic `segments` bore diameters. A manufactured profile that is not fully dimensioned needs explicit profile sensitivity studies, not a claimed exact CFD geometry.

The uniform cavity mode includes the specified leakage loss `ql` for vented boxes as well as sealed/PR boxes. A zero-mode straight-port case recovers the leaky lumped model at low frequency; omitting that damping would silently turn `ql` into an ignored parameter.
