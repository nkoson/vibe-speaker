# Simulation applications

Thirty-five standalone Python programs. Each reads one JSON parameter file, computes a declared engineering model and writes one JSON result document into the folder you name. None of them decides whether a result is good, blocked or viable: they report curves, numbers and the assumptions behind them, and the reader (you, the language model running the design skills) judges.

```
python framework/simulations/<name>/run.py --input params.json --out <folder> [--name <result-name>]
```

Every folder holds `run.py`, a `README.md` with the full input and output contract, and an `example.json`. `examples/run_examples.py` runs the whole chain into `examples/out/` so you can read real result documents before writing your own inputs.

## Inventory

| App | Model | Typical question it answers |
|---|---|---|
| `polar_import` | Complex measured-plane ingestion with explicit timing, normalization, symmetry and coverage | How can measured angular data become a canonical source without duplicating propagation |
| `response_prepare` | Windowed impulse conversion, complex merging/arithmetic, delay fitting and coordinate digitization | What processing and calibration produced these response data |
| `enclosure_network` | General lumped chamber/vent/PR networks with individual motors | What do double-tuned reflex and vent/PR bandpass topologies predict for the specified geometry |
| `parameter_identification` | Bounded complex-impedance parameter estimation with rank/residual diagnostics | Which driver or passive-diaphragm parameters explain the supplied observations |
| `network_diagnostics` | Programme-integrated electrical stress and equivalent peak dissipation resistance | What powers/currents and reactive load follow from the stated programme and amplifier model |
| `response_diagnostics` | Linear normal/minimum/excess phase, group delay, impulse, step and energy-time response | What time behavior follows from the stated complex response and endpoint assumptions |
| `lf_box` | Lumped sealed, vented, aperiodic, passive-radiator or bandpass bass model at any drive voltages, optionally as an isobaric pair, with duct length, PR mass, excursion, port speed, cutoffs and voltage-to-limit scaling | Which woofer, loading, volume and tuning give the extension and output I want, and what limits it |
| `lf_uncertainty` | Monte Carlo spread of `lf_box` over driver and build tolerances | How robust is that alignment to production spread |
| `source_response` | One section's complex pressure per volt (bandwidth prior, digitized datasheet curve with minimum phase, box output, measured data) and load impedance, plus its directivity model and acoustic depth | Turn a driver's published data into the standard section file the other apps read |
| `directivity` | Piston, Gaussian horn, tabulated beamwidth and rectangular ribbon patterns and -6 dB beamwidths, plus the oblate-spheroidal waveguide contour and cutoff from its geometry | Do the woofer and the horn match in coverage at the intended crossover |
| `baffle_diffraction` | Finite-baffle shelf and edge-diffraction factor per source position, optional recess | How the front panel size and driver placement shape the response |
| `crossover_network` | Loaded series/shunt ladders per section: transfers, branch and total impedance, component stress, tolerance envelope, how the power divides between drivers and network, physical part count | What this crossover does to each driver and to the amplifier, and what it keeps and costs |
| `crossover_fit` | Bounded least-squares fit of marked component values to a target coherent response, with an optional element-ablation pass and stock quantization | Find values for my chosen topology, then ask which elements are earning their place and what real stock does to them |
| `board_nodal` | Netlist solve of the realized board with wires, terminal pairs and connection modes | Does the drawn board behave like the intended ladders, in linked and bi-amp modes, and what do the parts see |
| `whole_speaker` | Coherent sum of the sections at their positions with directivity, baffle and filters; polar maps, floor image, polarity and depth studies, same-band array criteria and the near/far-field border | The predicted system response on and off axis, and whether the distance it was computed at is a far field at all |
| `room_response` | Finite-order 3D rectangular-room image paths with source orientation, six wall coefficients and multiple receivers | How placement, toe-in and early reflections change physical listening-position pressure |
| `cavity_modes` | Internal standing waves of the bass chamber (analytical or FVM), lining damping, cone loading change, port leakage, pressure envelope | Are braces, lining and port placement doing their job inside the box |
| `plate_structure` | Panel bays as a mode band between pinned and clamped edges, measured material and damping-treatment data, and the BBC audibility criterion over a relative panel output | Which panel needs a brace, more thickness or damping, and which octave to worry about |
| `response_metrics` | Statistics of curves and differences between curves, including published reference points, plus NBD, SM, AAD, LFX and LFQ named with the curve each came from | Score a candidate and compare it with the reference speaker |
| `spinorama` | The full 70-point CTA-2034-A orbit: listening window, early reflections, sound power, predicted in-room, both directivity indices and the Olive preference score | How would the published listening research rank this candidate |
| `thermal_power` | Two-body lumped voice-coil thermal scenario: coil and magnet temperature, `Re(T)` and the compression it costs | What is the output after the coil is hot |
| `horn_loading` | Webster throat impedance of an exponential, hypex or conical horn, the `k rm` mouth criterion and Keele's constant-directivity mouth sizing | Does this horn load the driver and does its mouth deliver the pattern on the label |
| `horn_design` | Keele's closed-form horn design from Thiele/Small parameters: suitability, throat, rear cavity, band, HF corners, displacement-limited output, efficiency, mouth criteria and the OS waveguide | Can this driver work in a horn at this cutoff, and how big does every part of it have to be |
| `open_baffle` | Dipole equivalence frequency, `cos(theta)` pattern, cavity resonance and the 18 dB/octave excursion demand | What would a dipole cost in displacement to reach this level |
| `transmission_line` | Taper-factor length, mode series and the driver offset that suppresses a higher mode | How long is the line, and is it worth building instead of a reflex box |
| `assembly_geometry` | Shared metre-based solids, air, meshes and source transforms | How geometry and fabrication records map consistently across models |
| `exterior_bem` | Constant-panel exterior Helmholtz boundary collocation | How the specified surface geometry and velocity radiate |
| `room_modal` | Driven room modes with full complex wall-admittance coupling | LF room pressure, finite-aperture source loading and position effects |
| `room_rays` | Specular/diffuse reflected-energy transport in triangle rooms | Later reflection energy and geometry-dependent arrival distributions |
| `coupled_cabinet` | Structural panel modes coupled to cavity and exterior pressure | Cabinet motion/radiation with joint, mass and acoustic feedback |
| `distributed_loading` | Plane-wave acoustic networks coupled to individual motors | Lines, folded horns, chambers and separate cone/mouth output |
| `nonlinear_driver` | Time-domain motor, thermal and optional nonlinear port states | Level-dependent motion, current, spectra and energy balance |
| `electrothermal_network` | Programme-weighted self-consistent load resistance/heating | Steady-state hot network/source transfer and thermal residual |
| `network_fit` | General nodal-network numerical fit and stock trials | Target costs and constraint margins with actual component records |
| `system_scenarios` | Correlated draws and explicit model alternatives over a dependency chain | Changes in observables, unresolved counts and conditional distributions |

Post-processing figures such as f3, f6, f10, ripple, sensitivity and band-within-tolerance are descriptive statistics of the computed curves. Their thresholds are parameters you pass; the apps report where the curve sits, not whether that is acceptable.

## Conventions

- **Section** is one band of a multi-band loudspeaker: one driver, its filter, its position and its
  directivity, taken together. A three-way loudspeaker has three sections. "Three-way" counts the
  bands and is the right word for the whole speaker; it is not a name for one of them, which is why
  the parameter files say `sections[]`. The term follows the manufacturers' own datasheets, where a
  coaxial driver is specified as an MF section and an HF section.
- Units in key names: `_hz`, `_mm`, `_m`, `_l` (litres), `_uf`, `_mh`, `_ohm`, `_db`, `_pa`, `_w`, `_rms`, `_peak`.
- Complex curves are records `{real, imag, magnitude, magnitude_db, phase_deg}` on the document's `results.f_hz` grid.
- Any curve in another result file can be referenced with `{"file": "path.json", "frequency_path": "results.f_hz", "path": "results.some.curve"}`. Relative paths resolve against the parameter file's folder. The curve is interpolated onto the consuming app's grid, so grids need not match, but keep source grids at least as wide as the consumer's.
- Result documents carry `simulation`, `version`, `status` (`computed` or `input_error`), `generated_utc`, the echoed `inputs`, `model_notes` (what the model does and does not include), `validity`, `constants` and `results`.
- **`validity`** states the band in which the model holds, where one is known, plus the application version: the lumped bound against the first internal standing wave, the piston `ka = 1` frequency, the gate-limited `f > 1 / t_gate` of any imported measurement, the maximum element size `h = c P / (10 f_max)` for a wave-based solve, and the assumptions that bound the rest. No source consulted gives a simulated-versus-measured error bar for any tool, so the validity range is the only honest bound this repository can publish.
- **`validity.universal`** distinguishes model assumptions, numerical verification and empirical agreement. `validation_evidence` links the generated benchmark catalogue; `curve_references` reports each input band, extrapolation policy and source validity. These are evidence records, not design decisions.
- **`constants`** records `c`, `rho0`, the dynamic viscosity of air and the reference pressure the document was computed with. Together with the version this is what lets a curve be re-derived, and compared, later: one commercial solver shipped a 10 to 20 percent lumped-element error across four builds before fixing it, and the defence against that is a recorded version and a recorded constant, not trust.
- A parameter document the app cannot use produces exit code 2 and a document with `status: input_error` and an `error` message naming the missing or invalid key.

## Data flow of one candidate

```
lf_box ──────────────┐
                     ├─> source_response (one file per section) ──┬─> crossover_fit ─> crossover_network ─┐
published curves ────┘                                        │                                       ├─> whole_speaker ──┬─> response_metrics
baffle_diffraction ───────────────────────────────────────────┴───────────────────────────────────────┘                   └─> spinorama ─> response_metrics (LFX)
cavity_modes ─> plate_structure                 schematic.py (tools) ─> board_nodal ─> whole_speaker (board transfers)
thermal_power ─> lf_box (thermal.coil_temperature_c) and crossover_network (thermal.coil_temperatures_c)
```

`horn_design`, `horn_loading`, `open_baffle` and `transmission_line` stand alone: they answer geometry questions about a loading before it is committed to, while `distributed_loading` supplies a connected motor/duct/outlet response where needed. Run `horn_design` first — it sizes a horn from the driver — and `horn_loading` afterwards, for the impedance of a contour already chosen.

## Tools (`framework/tools`)

- `plot_room_response.py`: room geometry, actual-seat curves, direct/room differences and spatial spread from `room_response`.
- `plot_curves.py`: curves or angle maps from any result file to PNG.
- `export_response.py`: complex CSV, FRD, ZMA or float WAV exports with provenance sidecars.
- `compare_reference_export.py`: frequency-aligned complex export differences without acceptance decisions.
- `cabinet_drawing.py`: cut list, chamber volume accounting and front, side-section and rear drawings from a cabinet description.
- `schematic.py`: ladder schematics (labels: reference, part name, value, loss and rating), pin-to-pin connection table and a starting `board_nodal` netlist from a `crossover_network` parameter file or a `crossover_fit` result. `tools/example_crossover.json` is a self-contained example with capacitor banks and resistor arrays.
- `build_pdf.py`: assembles Markdown documents with their images into one PDF, the final deliverable format.

## Setup

`python3 framework/bootstrap.py --tests` builds `.speaker-venv` with numpy, scipy, matplotlib, reportlab, pypdfium2 and pytest and verifies the apps. Tests: `.speaker-venv/bin/python -m pytest framework/tests -q`.

## Limits shared by every model

The original chain uses linear, small-signal physics with declared priors. Dedicated apps add nonlinear driver/port-loss states, room modes, reflected ray energy and joint-spring/cabinet coupling under their declared contracts; full aeroacoustic port noise and unmodeled material/motor behavior remain outside those calculations. Published data digitized from datasheets carries reading uncertainty. A computed curve is a prediction, never a measurement.

`thermal_power` supplies a two-body thermal scenario, while `electrothermal_network` iterates programme-weighted electrical/temperature feedback and `nonlinear_driver` evaluates the supplied time-domain motor, suspension and port laws. Their contracts distinguish resistance drift, nonlinear compression and unknown physical parameters.

Model-specific contracts describe what each solver computes. New room, boundary, coupled-cabinet and nonlinear apps extend the original linear chain; their numerical scope and evidence are documented in `framework/references/simulation-methods.md`. Benchmark errors are conditional on the case, geometry, input data and numerical resolution. They are distinct from empirical uncertainty.

**The framework includes sealed/vented alignment tables.** The bandpass, isobaric, aperiodic and cardioid loadings are solved as equivalent circuits for the geometry given; no tabulated alignment family is implemented for them, so their results identify the supplied equivalent circuit.

## Reliable project execution

For loops and project helpers use `.speaker-venv/bin/python framework/tools/run_simulation.py <app> --input <name>.params.json --out <folder> --name <name>`, or import its `run_simulation` function. It runs without a cache, removes the old destination, checks exit status and document identity/status, and includes stderr on failure. The example chain uses the same helper. Input and output filenames must differ.

The shared app CLI also invalidates the old output before loading input and publishes JSON atomically. Invalid input produces `input_error`; an unexpected crash leaves no result to mistake for the old computation. Never accept output after a nonzero exit, even if a file exists. Run dependent apps in order and stop the project chain on failure. Do not launch concurrent writers for the same result path.

A custom cache must include transitive file contents and model code in its key. A cold replay of the frozen chain remains part of selection verification. Actual-source numerical invariants are in `framework/templates/simulation-audit.md`; they establish consistency, not measured accuracy.

## Connected advanced models

See the designer skill's [advanced workflow](../skills/speaker-designer/references/advanced-simulation.md). `cavity_modes` exports canonical cone/outlet/impedance sources; `exterior_bem` exports angular source fields; room apps share receiver coordinates and explicitly partition model/time bands. `assembly_geometry` feeds geometry and drawing records. `system_scenarios` replays these dependencies over common draws. `framework/tools/collect_objectives.py` collects objective observations and signed differences; selection remains with the agent.

## Result-contract migration

Current outputs replace design-acceptance flags with observables: array spacing has `spacing_limit_margin_hz`, radiating area has `criterion_margin`, the horn cutoff relation has `cutoff_minus_fs_qts_hz`, and vent edge geometry has `radius_minus_reference_mm`. Panel comparison reports `worst_margin_after_scatter_db`; orthotropic `mode_band` is null with a separate `isotropic_comparison`. Interpret these quantities in the evaluator, rather than converting a sign into a universal design verdict.

Complex interpolation defaults to magnitude/residual-phase interpolation, with explicit `delay_s` and optional `cartesian` compatibility mode. Curve references record extrapolation; `error`, `zero` and `hold` are explicit policies. Every CLI result records an implementation digest covering the simulation code and shared numerical library, plus the benchmark catalogue and source-reference diagnostics. Replaying an earlier candidate is useful after a convention or model update; retain both result bases for comparison.

## Additional passive analysis contracts

Linear T/S consumers share `inductance_model` and `creep` laws. Their definitions
and identification limits are in [driver impedance](../references/driver-impedance-identification.md).
`baffle_diffraction` also supports a convex-polygon angular edge-dipole model;
its included piston pattern replaces rather than duplicates section directivity.
`board_nodal` supports exact ideal transformers as well as finite coupled windings.
`network_fit` accepts explicitly requested spatial response targets, preference
regression objectives and EPDR constraints. These are numerical objectives and
signed margins; none chooses a speaker.

The frozen [reference exports](../benchmarks/README.md) contain independently
evaluated circuits and analytical fields. They are separate from measurements.
New raw-measurement workflows accept plain numeric files and WAV; proprietary
acquisition containers require export to these formats. Active DSP synthesis and
controller configuration are outside this passive framework.
