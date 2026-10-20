# network_fit: General-netlist numerical fitting

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py network_fit --input framework/simulations/network_fit/example.json --out results --name network_fit
```

`network` uses the `board_nodal` contract, including explicit mutual coils and finite transformers. `variables[]` identify exact component IDs, optional numerical keys, positive bounds and optional stock records. A stock record carries the actual value plus DCR/ESR, SKU, rating, size and price together.

`target.transfers[]` defines load transfer targets by band and dB. Alternatively/additionally a `system` in the whole-speaker form associates each source section with a `load_id`; `target.spl_db`, band and vertical angles then define an acoustic objective. `constraints[]` specify `input_impedance_ohm`, `terminal_voltage_rms` or `component_power_w`, band and numerical minimum/maximum.

Choose `optimizer: slsqp` (default) or `differential_evolution` with a seeded population containing the incumbent. The optimizer evaluates the nodal solver, preserving every evaluated point and the initial point. `max_evaluations` bounds continuous work, and `max_stock_trials` bounds joint stock enumeration. The latter exposes total trial identities; an incomplete enumeration is a finite search, not proof about other combinations.

Results contain all trial values, objective costs, signed constraint margins, load minima, stock records and optimizer termination text. `numerical_minimum_index` identifies the lowest objective among evaluated points inside the supplied numerical domain, or among all trials if none lie in it. `numerical_domain_count` makes that distinction explicit. It is not a speaker selection or a component recommendation.

Inspect actual realized stress/protection and complete response families before selecting a design. Mathematical constraints describe the caller's search domain; their relevance and values belong to the agent's interpretation of the user brief and component evidence.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.

`target.spl_db` may also reference a real target curve using `{file, frequency_path, path}`. Optional `target.weights[]` entries `{band_hz, weight}` weight acoustic residuals within named bands, as in `crossover_fit`. These weights do not relax the explicit electrical constraints.

An `acoustic_relative_db` constraint uses the on-axis acoustic sum relative to its mean in `reference_band_hz` (default300-3000Hz). Include zero degrees in the target angles. Setting a minimum over a low-frequency band can enforce a required extension margin during fitting; verify sustained cutoff on the final dense grid and stock realization afterward.

`spatial_targets[]` adds `{curve,target_db,band_hz,weight,shape_only}`. Curve names:
`on_axis`, `listening_window`, `early_reflections`, `sound_power`,
`predicted_in_room`, `sound_power_di`, `early_reflections_di`. Targets may be scalars
or real curve references. Complete angular source coverage is required.
`spatial_options` records the same rear-wall/ring-weight choices as `spinorama`.
Every trial retains spatial curves, objective contributions and removed level
offsets. These weights define a numeric residual, not the importance of a design
objective unless the caller explicitly assigns it.

`preference_objective_weight` explicitly subtracts that weight times the existing
preference regression from the objective. It requires resolved LF extension and
the predictor frequency bands. No component/spatial target is added implicitly.
An `epdr_ohm` constraint returns a signed margin under the declared class-B model.
See [passive network diagnostics](../../references/passive-network-diagnostics.md).
