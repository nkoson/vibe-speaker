# coupled_cabinet: Coupled panels, cavity and exterior field

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py coupled_cabinet --input framework/simulations/coupled_cabinet/example.json --out results --name coupled_cabinet
```

`cabinet.dimensions_m` describes a rectangular thin-shell acoustic domain. `cabinet.material` supplies `thickness_m`, `density_kg_m3`, `youngs_modulus_pa`, optional `poisson_ratio`, `loss_factor` and `orthotropic` constants in the plate app's form. Named face overrides under `cabinet.panels` can add `edge_rotational_stiffness` at `u_min/u_max/v_min/v_max` and `added_masses` with local `position_m` and `mass_kg`.

`panel_mode_order`, `acoustic_mode_order` and `surface_divisions` are separate refinement variables. `source.position_m` and scalar/referenced volume velocity drive the internal air. `observers_m` locates exterior pressure samples. `exterior_feedback` defaults true; `coupling_scale` permits controlled coupling/decoupling studies.

Sine plate modes produce mass and stiffness operators. Edge rotational springs contribute modal stiffness; attached point masses contribute modal mass. A cosine cavity basis supplies the air operator. Integrating mode shapes over shared surface patches gives pressure-force/acceleration coupling. Exterior BEM maps boundary velocity to pressure load; that pressure feeds back into the structural equation. The block system solves cavity and structural motion together, and the resulting velocities radiate through the same boundary model.

Outputs include modal displacement, complex surface velocity, exterior pressure, coupling matrices, rigid-cavity frequencies and residuals. Compare against the zero-coupling result and refine all three discretizations. This is a reduced rectangular cabinet model, not a general solid-element stress solver: apertures, curved joints, multilayer shear and arbitrary brace compliance need suitable modal/property representations. The old isolated-panel volume-velocity audibility proxy remains a separate screening output.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
