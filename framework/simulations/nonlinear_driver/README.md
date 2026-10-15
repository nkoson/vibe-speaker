# nonlinear_driver: Nonlinear motor, thermal and vented states

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py nonlinear_driver --input framework/simulations/nonlinear_driver/example.json --out results --name nonlinear_driver
```

`driver.ts` supplies the linear parameter set. `drive.tones[]` specifies frequencies, RMS voltages and phases. Set `duration_s`, `sample_rate_hz` and optional integrator `rtol`. Outputs include startup transients; compare a settled time interval when studying a steady tone.

`nonlinear` accepts ascending polynomial coefficients in SI units: `bl_x` (Tm versus metres), `stiffness_x` (secant N/m versus metres), `inductance_x` (H versus metres), `inductance_i_factor` (dimensionless versus amperes), and `mechanical_resistance_v` (Ns/m versus m/s). Optional `x_m_domain` and `current_a_domain` record the supported parameter domains and count samples outside them. Defaults are the supplied linear driver constants, not invented nonlinear behavior.

The electrical equation uses differential flux/current inductance and the velocity-induced flux term. Mechanical force includes the position-dependent force factor, restoring force and inductance coenergy gradient. Two thermal bodies use explicit heat capacities and thermal resistances, feeding copper resistance back into the electrical equation.

Choose free air, `sealed_volume_l`, or `vented` with `volume_l`, `port_area_m2`, `effective_port_length_m`, linear `port_resistance_pa_s_m3`, `quadratic_loss_pa_s2_m6` and optional leakage resistance. The vented states are chamber pressure and port volume velocity, with pressure loss `(R + C |Q|) Q`. Coefficients are declared inputs; this is not a universal port-noise threshold.

Results include displacement, current, pressure, temperatures, port velocity, FFT spectrum, drive crest factor and an electrical/mechanical/thermal energy balance. Differential inductance and dissipative resistance leaving their mathematical physical domain produce an input error. Refine integration and sampling separately from parameter scenarios. The output is not an endurance rating or an automatic distortion acceptance decision.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
