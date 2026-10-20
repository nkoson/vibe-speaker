# lf_box: low-frequency box model

Lumped electro-mechanical-acoustic model of one cone driver in a sealed, vented, aperiodic, passive-radiator or bandpass enclosure, optionally as a coupled isobaric pair. Returns response, impedance, excursion, port air speed or radiator excursion and losses at every drive voltage you ask for. It reports numbers only; deciding whether an excursion or a port speed is acceptable is the reader's job.

**None of the loadings beyond sealed and vented has an alignment table behind it.** No bandpass, isobaric, aperiodic or cardioid alignment family was obtained from any source. Those loadings are solved as the circuit you describe, and the result document says so rather than implying a tabulated alignment was used.

## Run

```
python framework/simulations/lf_box/run.py --input params.json --out results/ [--name lf_box_c01]
```

Writes `results/<name>.json`. Exit code 2 and a `status: input_error` document when the parameters cannot be used.

## Input

| Key | Required | Meaning |
|---|---|---|
| `driver.ts` | yes | `fs_hz`, `vas_l`, `qms`, `qes`, `re_ohm`, `sd_cm2`; optional `le_mh`, `xmax_mm` (peak, one section), `xmax_standard` (see below), `displacement_limits` (see below), `mms_g`, `bl_tm` (published values used only as a consistency check) |
| `driver.ts.xmax_standard` | with `xmax_mm` | **Which definition the figure came from**, one of `geometric`, `aes2_1984`, `iec_62458`, `aes2_2012` or `not_stated`. Four definitions are in circulation and only the last two measure the same thing, so the field is an enumeration: free text is an input error, and a blank is recorded as `not_stated` rather than assumed |
| `driver.ts.displacement_limits` | no | The IEC 62458 parameter-based limits `xbl_mm`, `xc_mm`, `xl_mm`, `xd_mm`, and AES2-2012 clause 5.5's performance-based `x_aes2_2012_mm`. When any are given the **smallest** becomes the excursion ceiling and the app names the mechanism that binds, the definition behind it, and whether the set mixes parameter-based with performance-based figures |
| `driver.isobaric` | no | `true`, or `{wiring: "series" \| "parallel"}`. Transforms the driver record into its coupled-pair equivalent **before** the box maths runs: `Mms` doubles, `Cms` halves, `Vas` halves, `fs` and `Qts` are unchanged and reference efficiency falls 3 dB |
| `enclosure.type` | yes | `sealed`, `vented`, `aperiodic`, `passive_radiator` or `bandpass` |
| `enclosure.net_volume_l` | yes for vented/PR | Net air volume after driver, brace and port displacement. A sealed box may instead give `qtc` and let the app derive the volume |
| `enclosure.tuning_hz` | vented/PR | Box tuning |
| `enclosure.ql`, `enclosure.qp` | no | Leakage Q (default 10) and duct loss Q (default 20) |
| `enclosure.port.diameter_mm`, `enclosure.port.count` | vented | Straight round duct(s) used for length and air speed |
| `enclosure.port.throat_diameter_mm`, `flare_radius_mm`, `length_mm`, `edge_radius_mm` | no | Flared-duct geometry. When `flare_radius_mm` is given the app reports the normalised flare rate and the tuning the flared duct actually produces, from the **throat** dimensions |
| `enclosure.internal_dimensions_mm` | no | `[l, w, h]` of the air space. Sets the first axial standing wave, which is the upper bound of the lumped model and appears in the validity block |
| `alignment` | no | One object or a list: `{target: "B4" \| "BL4" \| "QB3", ql \| ql_values, a2}`. Solves Small's lossy quartic and reports what box the driver would need |
| `thermal` | no | `{coil_temperature_c, reference_c, copper_coefficient_per_c}`. Scales `Re` and recomputes everything, so the alignment can be read cold and hot |
| `analysis.kp` | no | Small's programme constant for the displacement-limited rating, default 3.0 |
| `enclosure.radiator` | PR | `fp_hz`, `vap_l`, `mmp_g`, `qmp`, `sd_cm2`; optional `enclosure.added_mass_g` overrides the derived tuning mass |
| `enclosure.rav_sweep_pa_s_per_m3` | aperiodic | **At least two** acoustic resistances for the damped vent. `RAV` has no published relation to stuffing density or vent-covering material, so a single value is refused: the app sweeps and reports the sealed and vented limits beside the sweep |
| `enclosure.rear`, `enclosure.front` | bandpass | Each `{volume_l, ql, vent: {tuning_hz, diameter_mm, count, qp, into}}`. A sealed rear chamber with one front vent is the fourth-order box; venting the rear as well, or nesting a further chamber behind a front vent with `into`, gives the sixth; both give the eighth. Order is counted from the topology as `2 (1 + vents)` |
| `drive.voltages_rms` | no | List of drive voltages, default `[2.83]`. The first entry is the base for limit scaling |
| `drive.series_resistance_ohm` | no | Cable or coil resistance in series with the driver |
| `drive.space` | no | `half` (2 pi, default) or `full` (4 pi) |
| `frequencies` | no | `{min_hz, max_hz, points, spacing, extra_hz}` or `{values_hz: [...]}`; default 10 to 1500 Hz, 480 log points |
| `terminal_transfer` | no | `{file, frequency_path, path}` pointing at a complex terminal transfer from `crossover_network` or `board_nodal`, applied to the drive voltage |
| `analysis.reference_band_hz` | no | Band whose mean level anchors the cutoff statistics, default `[150, 300]` |
| `analysis.cutoff_thresholds_db` | no | Default `[-3, -6, -10]` |
| `analysis.stress_band_hz` | no | Band searched for maximum excursion and port speed, default grid start to 300 Hz |
| `limits` | no | `xmax_mm`, `max_port_air_speed_ms`, `radiator_xmax_mm`, `power_w`, `nominal_impedance_ohm`. For each the app reports the voltage and SPL curve at which that limit is reached by linear scaling. These are your numbers echoed through the model, not the app's opinion |

Mass can only be added to a radiator, so the bare part's own in-box resonance is the highest tuning it can reach in a given volume; `results.radiator.maximum_tuning_hz` reports it. Asking for a higher `tuning_hz`, or supplying a negative `added_mass_g`, is an input error rather than a curve, because the alignment cannot be built. To see what the part does with no mass fitted, set `added_mass_g: 0` and read `results.radiator.actual_tuning_hz`.

## Output (`results`)

- `f_hz`: frequency vector.
- `derived_driver`: Sd, Cms, Mms, Rms, Bl, Qts, EBP; `published_consistency` relative errors when published Mms or Bl were given.
- `vent`: area, effective and physical duct length (vented). `radiator`: `required_added_mass_g`, `realizable`, `maximum_tuning_hz`, `total_moving_mass_g`, `null_hz`, `tuning_sensitivity_hz_per_g`, `added_mass_used_g` and `actual_tuning_hz` (PR). `system_resonance_hz`, `qtc` (sealed).
- `curves[]`: one entry per drive voltage — and, for an aperiodic sweep, one per drive voltage and `RAV`, each carrying the `rav_pa_s_per_m3` it was computed at — with `spl_db`, `pressure_pa` and `cone_pressure_pa` (complex records), `outlet_pressure_pa`, `z_ohm` (complex record: real, imag, magnitude, phase_deg), `excursion_peak_mm`, `port_air_speed_peak_ms` or `radiator_excursion_peak_mm`, `copper_loss_w`, `current_rms_a` and `statistics`.
- `curves[].statistics`: reference level, sustained cutoffs `f3`, `f6`, `f10` with a `bound` flag (`resolved`, `left_censored` = never fell below the threshold within the grid, `no_sustained_pass`), impedance minimum and maximum with their frequencies, maximum excursion, port speed and copper loss inside the stress band.
- `linear_scaling_to_limits[]`: for each supplied limit the drive voltage at which it is reached, the limiting frequency and the SPL curve at that voltage. The excursion limit defaults to the **binding** displacement limit, and `limit_basis` says which one it was.
- `efficiency`: Small's reference efficiency `eta_0 = 9.6e-10 fs^3 Vas / Qes` with the 1 W / 1 m half-space sensitivity it implies, the modelled level beside it, and `ceiling`: the lossless vented limit `eta_0(max) = 3.9e-6 f3^3 VB` with the candidate's margin below it. Real systems land 2 to 3 dB under that ceiling. Compute this **before** promising a sensitivity at a given extension in a given cabinet size.
- `displacement_limit`: the excursion ceiling actually used, which limit bound, the mechanism it names, and the standard it came from.
- `displacement_limited_output`: `VD = SD xmax`, `P_AR = kP f3^4 VD^2` acoustic into 2 pi, the SPL at 1 m and `P_ER` from it — with the same three figures recomputed at `kP = 0.3` and `kP = 5`, which is the span Small's own figures cover, and the caveats that go with them.
- `vent_physics` (vented): the Reynolds number at the reported peak velocity against the `Re = 50,000` degradation threshold, which of that and the legacy 10 m/s rule **binds for this diameter**, Small's minimum vent area `SV >= 0.8 fB VD`, the flare correction, and the `>= 0.2 Dmin` edge-radius requirement.
- `solved_alignments[]` (when `alignment` was given): per target and `QL`, the quartic's positive real roots with the one selected and the rule that selected it, `h = fB/fS`, `alpha`, `f3/fS`, the net volume and tuning the driver would need, and the **required `QT` beside the driver's actual `Qts`**.
- `loss_split`: the `1/QB = 1/QL + 1/QA + 1/QP` decomposition with Small's measured ranges as priors, and whether the chosen `QL` sits inside what they allow.
- `sealed_alignment` (sealed): the passband peak and `f3/fc` the total Q fixes — the trade that "extended" and "tight" are words for.
- `thermal_scenario` (when `thermal` was given): cold and hot `Re`, the ratio and the compression in dB.
- `isobaric` (when the flag was set): the single driver and the pair side by side, the exchange rate as a table — **half the box, the same maximum output, 3 dB less efficient, twice the power handling, two drivers** — and the reference efficiencies it was derived from. The lower-distortion claim is plausible and unmeasured, so it is named as something a candidate may not claim.
- `bandpass` (bandpass): the computed `order` and how it was counted, every chamber's compliance and leak resistance, every port with its geometry and whether it reaches the room, `port_resonances` with each port's first pipe resonance `f ~= c / (2 L_eff)` on the end-corrected length, the `lumped_limit_hz` `c / (4 L_eff)` where the lumped-mass port model already under-states the port flow by 3.9 dB, and the statement that **an electrical low-pass is in practice mandatory** above them, and `exchange` — the −3 and −6 dB passband widths in octaves against the midband gain over the driver's own reference sensitivity, so the gain is never read as free output.
- `aperiodic` (aperiodic): the resistance used, and `sweep` with every `RAV`'s cutoffs, excursion and impedance minimum beside the **sealed limit** (`RAV` infinite) and the **vented limit** (`RAV` zero) computed from the same box. The block is labelled `EXPLORATORY`: the two limits are rigorous and everything between them is a free parameter with no published value.

Complex records everywhere follow `{real, imag, magnitude, magnitude_db, phase_deg}`. Feed `results.curves.0.z_ohm` to `crossover_network` as a load through a `{file, frequency_path: "results.f_hz", path: "results.curves.0.z_ohm"}` reference, and `results.curves.0.cone_pressure_pa` or `pressure_pa` to `source_response`.

## Typical use in the design loop

0. Read `efficiency` and `efficiency.ceiling` first. A sensitivity target the efficiency law cannot support is a finding about the driver complement, and no box or network recovers it.
1. Ask `alignment` what box the driver wants before describing one, then sweep a few volumes and tunings to see extension, excursion and port speed at the intended drive.
2. Use `linear_scaling_to_limits` to read what output the alignment supports before excursion or port speed reach the figures you consider acceptable.
3. Pass the impedance and the cone pressure to the crossover and whole-speaker apps.

## Series resistance and downstream sources

`drive.series_resistance_ohm` affects pressure, excursion and current at the stated source voltage. The reported `z_ohm` is the driver load and excludes that external resistance. Applying a crossover coil to that impedance while reusing source-voltage pressure containing the same coil allowance repeats the loss. Use a zero-external-resistance LF source run, or `source_response.acoustic.voltage_basis: driver_terminal` to remove the allowance; then model physical wiring and coil DCR once in the network. Keep allowance runs for alignment screening and stress runs at their stated drive.

## Extended linear driver laws and chamber networks

`driver.ts.inductance_model` supports `constant {le_mh}`, `leach {k,n}`,
`lr2 {le_mh,l2_mh,r2_ohm}` and
`semi_inductance {leb_mh,le_mh,ke,rss_ohm}`; absent parallel branches are open.
`driver.ts.creep` supplies `beta`, optional `transition_hz` (default 1.5 fs),
`c0_m_per_n` and `r0_ns_m`. Read
[driver impedance](../../references/driver-impedance-identification.md) before
substituting fitted parameters for conventional T/S values. Isobaric equivalents
scale these laws consistently. Heating changes Re and Qes together to retain Bl.

`alignment.target: C4` adds a fourth-order Chebyshev prototype with explicit
`ripple_db` (default 0.5); high-frequency gain is normalized to unity. It uses the
same lossy quartic as the existing prototypes and still reports required versus
actual driver Q. It is not an automatic alignment choice.

Use [enclosure_network](../enclosure_network/README.md) for double-tuned reflex,
PR bandpass, general chamber incidences, separate absorption/leakage or multiple
individually driven motors.
