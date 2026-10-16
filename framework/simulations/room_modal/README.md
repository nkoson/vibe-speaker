# room_modal: Driven low-frequency room waves

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py room_modal --input framework/simulations/room_modal/example.json --out results --name room_modal
```

`room.dimensions_m` defines a rectangular room. `mode_order` includes cosine indices zero through that order on each axis (default 4, computational range 1–10). `modal_loss_factor` adds declared basis damping. `receivers_m` and `sources[].position_m` use room coordinates.

A source supplies `volume_velocity_m3_s` or a complex `volume_velocity` file reference. A finite source can provide `radius_m`, `normal` and `aperture_samples`; its modal coupling is disk-averaged. Alternatively a source with `driver.ts`, `radius_m`, `voltage_rms` and optional `sealed_volume_l` solves motor current and motion jointly with room pressure. Finite aperture avoids treating motor feedback as a singular point evaluation.

Each wall (`x_min`, `x_max`, `y_min`, `y_max`, `z_min`, `z_max`) is rigid unless specified under `room.walls`. Supply `resistance_pa_s_m` and `reactance_pa_s_m`, or a complex `impedance` reference. These are specific acoustic impedances, not absorption coefficients.

Orthonormal cosine modes give `K - k² I + j omega rho Σ(Y_wall B_wall)`. Full wall-overlap matrices retain mode coupling; they are not diagonal modal-Q replacements. Source terms are `j omega rho Phi(source) Q`. An attached motor contributes its acoustic admittance to the matrix, giving room-pressure feedback on the source.

Outputs include complex receiver pressure, rigid-basis frequencies, modal coefficients, motor currents/excursions/impedance and linear residuals. Increase basis order to assess truncation independently of frequency spacing. A perfectly lossless pole sampled exactly is a singular mathematical input. Wall impedance and source aperture assumptions determine the physical scenario. This model addresses rectangular rooms; use triangulated ray geometry for high-frequency energy in other room shapes.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
