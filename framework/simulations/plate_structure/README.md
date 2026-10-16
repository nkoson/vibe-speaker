# plate_structure: panel modes, damping and audibility

Treats each unperforated panel bay of the cabinet as a thin plate and drives it with a uniform pressure spectrum, typically the cavity pressure envelope from `cavity_modes` scaled to the drive voltage. Reports **where the modes land as a band**, the measured damping a named treatment buys, displacement and velocity spectra, and the BBC's measured audibility criterion against a relative panel output.

This app is an isolated-panel screening model. Its isotropic restraint comparison and volume-velocity proxy describe that approximation. `coupled_cabinet` supplies a separate coupled panel/cavity/exterior calculation with declared spring and mass properties.

## Run

```
python framework/simulations/plate_structure/run.py --input params.json --out results/ [--name panels_c01]
```

## Input

| Key | Meaning |
|---|---|
| `material` | `name` from the material table (`birch_ply_9mm`, `birch_ply_17mm`, `mahogany_ply_10mm`, `blockboard_12mm`, `chipboard_16mm`, `chipboard_18mm`, `hardboard_10mm`, `oak_along_grain`, `oak_across_grain`, `beech_along_grain`, `deal_along_grain`, `grp_random_50`, `carbon_honeycomb`, `mdf`, `particleboard`, `osb`) and/or explicit `youngs_modulus_pa`, `density_kg_m3`; plus `thickness_mm` (a named board of a stated thickness supplies its own, and an explicit value overrides it), `poisson_ratio` (.3), optional `orthotropic {E_parallel_pa, E_perpendicular_pa, G_inplane_pa, nu_parallel_perp}` evaluated in both grain orientations |
| `material.treatments` | Named damping treatments from the BBC's measured table (`none`, `mutacell_1`, `mutacell_2`, `mutacell_4`, `roofing_felt_1`, `bostik_1`, `bostik_2`, `bostik_3`, `aquaplas_1`, `mutacell_steel`, `roofing_felt_2_steel`, `celotex_1`). Each contributes its measured loss factor to the response, so the damping choice becomes a curve |
| `material.loss_factors` | Explicit loss factors, used instead of or alongside the treatments; defaults to .015, .03, .08 only when no treatment is named |
| `audibility.cone` | `{file, frequency_path, excursion_path, sd_cm2}` or `{constant_excursion_mm_peak, sd_cm2}`. Turns the cone's excursion curve into a volume velocity so each panel's output can be compared with it against the criterion |
| `panels[]` | `name`, `a_mm`, `b_mm` (bay dimensions between supports), `count`, optional `thickness_factor`, `note` |
| `auto_bays` | `{inside_width_mm, inside_depth_mm, inside_height_mm, brace_z_mm: [...], brace_thickness_mm, rear_bays}` generates side bays between braces, bottom, top and rear bays |
| `pressure` | `{constant_pa}` or `{file, frequency_path, path, scale}` RMS spectrum; `scale` converts a 2.83 V envelope to your drive (10 for 28.3 V) |
| `frequencies` | Base grid, default 20 to 1500 Hz, 121 log points; exact natural frequencies are added |
| `mode_order` | Modes per direction, default 7 |

## Output (`results`)

- `panels[].mode_band`: the fundamental as a **band** — `pinned_hz` from the exact closed form `lambda = pi^2 (1 + (a/b)^2)`, `clamped_hz` from Leissa's tabulated values interpolated at the panel's aspect ratio, the ratio between them and the band in octaves. Worked on the BBC's own LS3/6 side panel this gives 196 to 393 Hz, and the BBC measured that cabinet's dominant panel output near **150 Hz — below even the pinned bound**, because a real panel carries the driver's reaction mass on compliant joints. Use the band to know which octave to worry about, rather than assuming an exact notch frequency.
- `panels[].audibility`: the margin the criterion demands at each edge of that band. A resonance at 150 Hz needs 13 dB below the direct sound, one at 1 kHz needs 30 dB, and that 17 dB is why moving a panel mode up in frequency while raising its `Q` makes matters worse — which is what the BBC measured when they doubled a cabinet's wall thickness.
- `panels[]`: dimensions, `natural_modes_hz` with `mode_indices`, `first_mode_hz` (the pinned bound, labelled as such), `static_center_mm_at_max_pressure`, `static_sampled_max_mm`, and `loss_variants[]` with the treatment that set each loss factor, `center_displacement_rms_mm`, `modal_bound_rms_mm`, `sampled_max_rms_mm`, `velocity_bound_rms_m_s`, `volume_velocity_rms_m3_s` and their peaks.
- `panels[].loss_variants[].audibility` (when `audibility.cone` was given): the panel's output relative to the cone as a volume-velocity ratio, the criterion curve, the margin between them and the worst margin with its frequency. A volume-velocity ratio is **not** the BBC's measured panel-to-direct pressure ratio: it holds while both radiators are small compared with a wavelength and flatters the panel above that.
- `audibility_criterion`: the curve itself on the analysis grid, its shape in words, the `+/- 1 dB` scatter and the fact that **it has no theoretical backing whatsoever** — the BBC say so, and add that there is no obvious reason it should slope downwards.
- `damping`: every named treatment with its measured `Q`, loss factor, thickness and **loss factor per millimetre**, the full table ranked by that figure, and the caveat that neither absolute values nor a universal ranking is established for arbitrary substrates and bond conditions.
- `material`: the resolved material with its source, the BBC's figure of merit `sqrt(E rho)/Q`, and the orthotropy note where the material is plywood or timber.
- `clamped_square_higher_modes`: Leissa's 35.99, 73.41, 108.3, 131.6, 132.3, 165.2. The pair at 131.6 and 132.3 is why "the panel resonance" is a simplification above the first mode or two.
- `summary`: lowest first mode, the lowest mode band with the panel it belongs to, the worst panel by peak modal bound at the nominal loss factor, the maximum peak bound and static deflection.

Typical reading: the panel whose mode band sits in the 100 to 400 Hz region where the criterion tightens fastest is the one to brace or damp first, and the damping table says what each treatment costs in thickness to get there.

## Orthotropic results

For orthotropic material the app reports its orientation-dependent Navier modes and `band_coverage`, with an explicitly separate `isotropic_comparison`. `mode_band` and the aggregate isotropic-band summary are null for that case, because the isotropic restraint table is not an orthotropic bracket. `coupled_cabinet` adds declared joint springs, attached masses and acoustic feedback where those mechanisms affect the design.
