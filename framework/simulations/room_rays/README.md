# room_rays: Polyhedral reflected-energy transport

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py room_rays --input framework/simulations/room_rays/example.json --out results --name room_rays
```

`room_surface` is a closed outward-oriented geometry mesh. Give `source_position_m`, `receivers_m`, `receiver_radius_m`, `rays`, `seed`, `max_bounces`, `duration_ms` and `time_step_ms`. The source defaults to omnidirectional pressure at 1 m, supplied as `pressure_at_1m_pa` or a complex `source_pressure` reference on the requested frequency grid.

`energy_absorption` and `scattering` set surface defaults. `surface_materials[]` can assign triangle indices, scalar or per-band energy absorption and scattering probability. Coefficients lie in [0,1]. `directivity` accepts the shared analytic or complex-grid source patterns; `source_normal` orients them. Initial directions use equal-area spherical sampling weighted by the directional pressure squared; diffuse reflections use cosine-weighted hemisphere sampling. Ray energy is reduced by each boundary loss. Receiver estimates use the sphere's projected area, not a coherent pressure sum.

The direct field is returned separately. `min_arrival_ms` excludes earlier reflected energy, enabling an explicit early-image/late-ray partition. Output `receivers[].reflected_mean_square_pa2` contains the reflected-energy estimate; arrival bins retain the same contributions. `transport` records absorbed/remaining power and escaped rays.

Compare ray counts, seeds, receiver radii, time and bounce limits. This is high-frequency incoherent transport, including specular and diffuse reflections and obstruction by the supplied triangles. It does not resolve LF phase interference. Furniture can be represented by correctly oriented internal obstacle surfaces only when the supplied containment/room topology is valid; the simple primitive example has no furniture. No reverberation-time or listening-quality verdict is inferred.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
