# exterior_bem: Geometry-derived exterior radiation

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py exterior_bem --input framework/simulations/exterior_bem/example.json --out results --name exterior_bem
```

`surface` accepts a supported geometry object or `{assembly: {file}, object_id}`. The mesh describes a closed outward-oriented boundary. `drive.normal_velocity_m_s` is a uniform RMS boundary velocity; `drive.patches[]` overrides triangle indices with a scalar velocity or a complex referenced `velocity` curve. `drive.voltage_rms` gives the input basis for exported source fields.

Supply `observers_m`, or an `angular_grid` with `radius_m`, `horizontal_deg` and `vertical_deg`. A source export is most useful with a reference sphere outside the object and angular grids containing zero and the intended full-space coverage. Pressure uses the e^(jwt), outgoing exp(-jkr) convention.

The solver uses a single-layer potential with constant triangle densities. The exterior normal derivative is collocated at centroids, including the -1/2 jump. It solves `(-I/2 + K') sigma = -j omega rho velocity`, then evaluates `p = S sigma` at the observers. Off-diagonal integration uses panel centroid quadrature. This is a low-order BEM: refine mesh, frequency and observer distance independently. Interior resonances can degrade conditioning; the result reports condition numbers and algebraic residuals rather than hiding them.

Outputs include complex pressure, density, surface geometry, element/wavelength ratios and residuals. Angular runs also export a reference-sphere-delay-removed `pressure_per_volt_pa` and a `complex_grid` directivity, with a source contract marking included geometry diffraction. Combine this pressure with a separately justified driver impedance using `source_response` kind `simulation`; omit another baffle correction.

The pulsating-sphere benchmark tests normalization and convergence. A small linear-system residual is not a mesh-error bound. The boundary velocity is prescribed; driver/throat mechanics are separate inputs. Closed coarse meshes can represent cabinets, recesses and horn bodies, but a feature absent from the mesh is absent from the computation.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
