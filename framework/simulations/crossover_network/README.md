# crossover_network: loaded passive ladders

Solves each section's passive filter as an exact series/shunt ladder terminated by the real driver impedance, then combines the sections in parallel at the input terminals. Reports the terminal transfer of every section, the branch and total input impedance, the voltage, current and dissipation of every component at the stated input voltage, and an optional tolerance envelope. When the section's source file is given it also returns the acoustic pressure per input volt for `whole_speaker`.

## Run

```
python framework/simulations/crossover_network/run.py --input params.json --out results/ [--name xo_c01]
```

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 10 to 40000 Hz, 800 log points; use the same grid as the source files |
| `input_voltage_rms` | Drive at the speaker terminals for stress figures, default 2.83 |
| `tolerances` | `draws` (0 = off), `seed`, relative half-widths `C`, `L`, `R` (defaults .05, .03, .02); a leaf may carry its own `tolerance_fraction` |
| `sections[]` | One entry per section, see below |

### Section

| Key | Meaning |
|---|---|
| `name` | Label |
| `source` | `{file}` of a `source_response` result; supplies load impedance (`results.z_ohm`) and pressure per volt (`results.pressure_per_volt_pa`). Override paths with `impedance_path` and `pressure_path` |
| `load` | Inline impedance model (same kinds as `source_response`) or `{file, frequency_path, path}` reference; overrides the source impedance |
| `polarity` | +1 or -1 at the driver terminals |
| `wire_loop_ohm` | Internal wiring resistance placed in series ahead of the filter |
| `elements[]` | Ordered from the input terminals toward the driver. Each has `id`, `position` (`series` or `shunt`) and an element description |

### Element descriptions

- `{"type": "L", "value_mh", "dcr_ohm"}`: DCR defaults to 0.10 + 0.16 sqrt(L) ohm when absent and is reported as `dcr_ohm_assumed`.
- `{"type": "C", "value_uf", "esr_ohm"}`: ESR defaults to 0.01 ohm.
- `{"type": "R", "value_ohm"}`.
- `{"type": "series", "parts": [...]}` and `{"type": "parallel", "parts": [...]}` combine parts (a Zobel is a series R and C in a shunt position; a parallel notch is a parallel L, C and R in a series position; a capacitor bank is `parallel` of several `C`).

Attenuator: a series `R` followed by a shunt `R`. Baffle-step shelf: series `parallel` of `L` and `R`.

Optional pass-through fields on any leaf, ignored by the solver but used by `tools/schematic.py` and the documents: `part` (manufacturer and series, for example "Jantzen Cross-Cap") and `rating` (`voltage_v` for capacitors, `power_w` for resistors, `current_rms_a` for coils). Fill them when the values are quantized to real stock so the schematic labels carry the part and its specification.

## Output (`results`)

- `f_hz`, `input_voltage_rms`, `input_z_ohm` (complex record), `input_current_rms_a`, `total_component_dissipation_w`.
- `statistics`: input impedance minimum and maximum in 20 to 20000 Hz with frequencies, maximum total dissipation, component count.
- `sections[]`: `transfer` (driver terminal voltage per input volt, complex, polarity included), `branch_input_z_ohm`, `load_z_ohm`, `terminal_voltage_rms`, `load_power_w`, `acoustic_pressure_per_input_volt_pa` and `acoustic_spl_db_at_input_voltage` when a source was given, `components[]` (**one row per physical part**: value, loss used or assumed, and the maximum voltage, current and dissipation that part alone carries, each with its frequency), `component_curves[]` (**one curve set per element group**, so a Zobel or a capacitor bank appears once) and `tolerance` percentiles when draws were requested.
- `colocated_sum_spl_db_at_input_voltage`: the coherent sum with every section at one point, a quick look only.

Reading the stress figures: dissipation and voltage are reported at `input_voltage_rms` on a single frequency, which is a robustness probe rather than an operating point, and a component rating only applies to the mounting its datasheet assumed. `framework/references/crossover-design.md` covers both.

Downstream: `whole_speaker` reads `results.sections.N.transfer` through `{"file": "xo.json", "frequency_path": "results.f_hz", "path": "results.sections.0.transfer"}`; `lf_box` accepts the same as `terminal_transfer` to see excursion through the filter.

## Reading the load, the heat and the parts

- `sections[].compensation_audit` reports the residual impedance variation of the compensated driver over plus and minus one octave around each crossover you name, against the roughly 1 ohm / 10 percent target, and the **equalised effective resistance the filter actually works into** — which is the figure that belongs in a component formula, never the nominal rating on the label. It applies only elements carrying `"role": "compensation"`, because a shunt capacitor in a low-pass ladder and a Zobel across the driver are both shunt elements and only one of them is compensation. Where nothing is declared, `compensation_declared` is false and the figures describe the bare driver — which is itself the finding, since sensitivity to the load grows with filter order.
- `sections[].insertion_loss` separates two things the transfer curve conflates: `resistive_loss_db`, measured against the same ladder with coil DCR, capacitor ESR and the wire loop removed, is what the real parts cost; `passband_loss_db` is the total level the network takes off in that section's passband.
- `sections[].coil_temperature_cases[]` scales the driver's own `Re` by `1 + 0.0039 (T - T0)` and recomputes. A hot driver takes a larger share of the terminal voltage, so the electrical transfer usually **rises** while the driver's sensitivity falls with `Bl/Re`; read it together with `thermal_power` and `lf_box`'s `thermal_scenario`, never apart. Needs `sections[].re_ohm`.
- `sections[].inductor_ratings[]` says, per coil, what current it carries and what its saturation rating is. **For a cored coil the answer is usually "not published", and that is settled rather than a search still to be done:** the supplier states in its own technical FAQ that it has not measured power handling or saturation points at all, and considers the measurement inconclusive for deciding crossover suitability. The field carries the string `not published` rather than a blank, because a blank invites a later assumption. Where the core is known the row names its failure mode — an air core does not saturate at all, a ferrite core saturates earlier and its inductance collapses abruptly, a powder core saturates later and more softly — and `frequency_rule` reports the only threshold anyone published: the vendor's own practice of ferromagnetic cores below about **1.2 kHz** and air cores above, checked against the section's passband. A cored coil above that is a choice the candidate notes have to argue for. The model treats every coil as linear at every level.
- A composite element's stress is distributed to its members: a series group shares its current and divides its voltage, a parallel group shares its voltage and divides its current, and the leaf powers sum to the group's power exactly. So a capacitor in a Zobel carries its own ESR loss rather than the resistor's, and a coil inside a parallel notch carries its own branch current rather than the notch's. Read `components[].max_dissipation_w` against the part's own rating; for what the board dissipates as a whole use `total_component_dissipation_w`, which is summed per group per frequency.
- `power_split` gives each branch's share of the input power. It is computed at a flat drive voltage, which is not programme material: for sizing per-branch current ratings the equal-power frequency between the low band and everything above it lies between 250 and 350 Hz on typical programme, and that figure belongs to the programme, not to this network.

## Extra input keys

| Key | Meaning |
|---|---|
| `sections[].re_ohm` | The driver's cold DC coil resistance, needed for the coil-temperature cases. Omit it for a ribbon behind a transformer, where copper drift does not scale the transformed impedance |
| `sections[].passband_hz` | Band the insertion-loss passband figures are taken over, and the band each coil's 1.2 kHz core-type check is made against |
| `sections[].compensation_audit` | `{crossover_hz: number or list, octaves: 1.0}` |
| `sections[].elements[].role` | `"compensation"` marks a Zobel or a notch so the audit can find it |
| `sections[].elements[].core`, `saturation_current_a` | Coil core material (`air`, `ferrite`, a powder core, or any ferromagnetic description) and its published saturation current, where one exists |
| `thermal` | `{coil_temperatures_c: [20, 100], reference_c: 20, copper_coefficient_per_c: 0.0039}` |
| `power_split_band_hz` | Band the integrated power split is taken over, default 20 to 20000 Hz |
