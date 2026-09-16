# Simulation applications

Eighteen standalone Python programs. Each reads one JSON parameter file, computes one linear engineering model and writes one JSON result document into the folder you name. None of them decides whether a result is good, blocked or viable: they report curves, numbers and the assumptions behind them, and the reader (you, the language model running the design skills) judges.

```
python framework/simulations/<name>/run.py --input params.json --out <folder> [--name <result-name>]
```

Every folder holds `run.py`, a `README.md` with the full input and output contract, and an `example.json`. `examples/run_examples.py` runs the whole chain into `examples/out/` so you can read real result documents before writing your own inputs.

## Inventory

| App | Model | Typical question it answers |
|---|---|---|
| `lf_box` | Lumped sealed, vented, aperiodic, passive-radiator or bandpass bass model at any drive voltages, optionally as an isobaric pair, with duct length, PR mass, excursion, port speed, cutoffs and voltage-to-limit scaling | Which woofer, loading, volume and tuning give the extension and output I want, and what limits it |
| `lf_uncertainty` | Monte Carlo spread of `lf_box` over driver and build tolerances | How robust is that alignment to production spread |
| `source_response` | One section's complex pressure per volt (bandwidth prior, digitized datasheet curve with minimum phase, box output, measured data) and load impedance, plus its directivity model and acoustic depth | Turn a driver's published data into the standard section file the other apps read |
| `directivity` | Piston, Gaussian horn, tabulated beamwidth and rectangular ribbon patterns and -6 dB beamwidths, plus the oblate-spheroidal waveguide contour and cutoff from its geometry | Do the woofer and the horn match in coverage at the intended crossover |
| `baffle_diffraction` | Finite-baffle shelf and edge-diffraction factor per source position, optional recess | How the front panel size and driver placement shape the response |
| `crossover_network` | Loaded series/shunt ladders per section: transfers, branch and total impedance, component stress, tolerance envelope | What this crossover does to each driver and to the amplifier |
| `crossover_fit` | Bounded least-squares fit of marked component values to a target coherent response | Find values for my chosen topology that flatten the system |
| `board_nodal` | Netlist solve of the realized board with wires, terminal pairs and connection modes | Does the drawn board behave like the intended ladders, in linked and bi-amp modes, and what do the parts see |
| `whole_speaker` | Coherent sum of the sections at their positions with directivity, baffle and filters; polar maps, floor image, polarity and depth studies, same-band array criteria and the near/far-field border | The predicted system response on and off axis, and whether the distance it was computed at is a far field at all |
| `cavity_modes` | Internal standing waves of the bass chamber (analytical or FVM), lining damping, cone loading change, port leakage, pressure envelope | Are braces, lining and port placement doing their job inside the box |
| `plate_structure` | Panel bays as a mode band between pinned and clamped edges, measured material and damping-treatment data, and the BBC audibility criterion over a relative panel output | Which panel needs a brace, more thickness or damping, and which octave to worry about |
| `response_metrics` | Statistics of curves and differences between curves, including published reference points, plus NBD, SM, AAD, LFX and LFQ named with the curve each came from | Score a candidate and compare it with the reference speaker |
| `spinorama` | The full 70-point CTA-2034-A orbit: listening window, early reflections, sound power, predicted in-room, both directivity indices and the Olive preference score | How would the published listening research rank this candidate |
| `thermal_power` | Two-body lumped voice-coil thermal scenario: coil and magnet temperature, `Re(T)` and the compression it costs | What is the output after the coil is hot |
| `horn_loading` | Webster throat impedance of an exponential, hypex or conical horn, the `k rm` mouth criterion and Keele's constant-directivity mouth sizing | Does this horn load the driver and does its mouth deliver the pattern on the label |
| `horn_design` | Keele's closed-form horn design from Thiele/Small parameters: suitability, throat, rear cavity, band, HF corners, displacement-limited output, efficiency, mouth criteria and the OS waveguide | Can this driver work in a horn at this cutoff, and how big does every part of it have to be |
| `open_baffle` | Dipole equivalence frequency, `cos(theta)` pattern, cavity resonance and the 18 dB/octave excursion demand | What would a dipole cost in displacement to reach this level |
| `transmission_line` | Taper-factor length, mode series and the driver offset that suppresses a higher mode | How long is the line, and is it worth building instead of a reflex box |

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
- **`validity.universal`** carries the two statements that are true of every model here, on every document: that no source states the error between a simulated and a measured response for any tool, and that **numerical accuracy must never be quoted as agreement with measurement**. A solver's error against its own governing equation is published and excellent; it says nothing about how far the answer sits from a microphone.
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

`horn_design`, `horn_loading`, `open_baffle` and `transmission_line` stand alone: they answer geometry questions about a loading before it is committed to, and nothing downstream consumes their results. Run `horn_design` first — it sizes a horn from the driver — and `horn_loading` afterwards, for the impedance of a contour already chosen.

## Tools (`framework/tools`)

- `plot_curves.py`: curves or angle maps from any result file to PNG.
- `cabinet_drawing.py`: cut list, chamber volume accounting and front, side-section and rear drawings from a cabinet description.
- `schematic.py`: ladder schematics (labels: reference, part name, value, loss and rating), pin-to-pin connection table and a starting `board_nodal` netlist from a `crossover_network` parameter file or a `crossover_fit` result. `tools/example_crossover.json` is a self-contained example with capacitor banks and resistor arrays.
- `build_pdf.py`: assembles Markdown documents with their images into one PDF, the final deliverable format.

## Setup

`python3 framework/bootstrap.py --tests` builds `.speaker-venv` with numpy, scipy, matplotlib, reportlab, pypdfium2 and pytest and verifies the apps. Tests: `.speaker-venv/bin/python -m pytest framework/tests -q`.

## Limits shared by every model

Linear, small-signal physics with declared priors. No distortion, port noise, breakup, room or joint behaviour is simulated. Published data digitized from datasheets carries reading uncertainty. A computed curve is a prediction, never a measurement.

Thermal behaviour is the one exception, and a narrow one: `thermal_power` models voice-coil heating as a two-body lumped system over declared priors, and `lf_box` and `crossover_network` accept a coil temperature as a scenario. That is resistance drift and nothing else — nonlinear compression, which is instantaneous rather than thermal, is in none of them.

**No source consulted states the decibel or degree error between a simulated and a measured response, for any tool.** That was searched for deliberately, and the shape of the absence is informative: numerical accuracy against the governing equation is published and excellent, while agreement with measurement is reported qualitatively even in review literature. The two are different quantities and must never be substituted for one another. Every result here therefore carries no error bar from the literature, only the model's declared assumptions and the validity band in its own document. Record the version and re-run anything produced by a version later found wrong.

**Alignment tables exist for sealed and vented boxes and for nothing else.** The bandpass, isobaric, aperiodic and cardioid loadings are solved as equivalent circuits for the geometry given; no tabulated alignment family was obtained for any of them, and no result document may imply one was used.
