# distributed_loading: Distributed line, horn and chamber loading

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py distributed_loading --input framework/simulations/distributed_loading/example.json --out results --name distributed_loading
```

Declare unique acoustic `nodes`. `ducts[]` connect node pairs using `length_m`, `area_m2`, optional `speed_m_s` and `attenuation_np_m`. Piecewise area segments represent tapers and folds. `chambers[]` add `volume_l` and optional leakage resistance at a node. `outlets[]` give a node, `radius_m`, physical position and optional end correction and series loss.

Each `drivers[]` record has `id`, `ts`, voltage, optional series resistance, and front/rear acoustic node identities. An omitted front node radiates directly; an attached node is loaded by the acoustic network. Multiple drivers retain their own current, excursion and acoustic incidence. Driver electrical grouping can be represented by the individual terminal drives derived from `board_nodal`.

A duct's nodal admittance is formed from its hyperbolic transmission matrix: diagonal `coth(gamma L)/Zc`, off-diagonal `-csch(gamma L)/Zc`, with `Zc=rho c/S`. Chambers add acoustic compliance, outlets add baffled-piston radiation impedance, and motors add their electromechanical Norton equivalent. This solves loading and radiated volume flows together.

Results include loaded impedance, current and excursion per motor; cone and terminus volume velocity; separate 1 m radiation contributions; complex pressure at the stated observers; and nodal residuals. Radiation uses a declared half-space monopole approximation and propagation at the actual outlet position.

Refine taper segmentation and compare the short-duct/lumped limit. The model retains longitudinal modes but not transverse duct modes, detailed bend scattering or nonlinear flow. Distributed porous attenuation and effective wave speed are supplied scenarios, rather than inferred from a material name. Use `nonlinear_driver` for the separate time-domain quadratic port-loss scenario.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
