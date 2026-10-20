# parameter_identification

Bounded complex-impedance fitting with residuals and local identifiability diagnostics.
`initial` contains fitted parameter starts; `known` contains fixed values. Keys must
be disjoint. Every fitted key needs `[lower,upper]` in `bounds`; use physically
positive bounds for mass, compliance, damping and force factor.

For `mode: driver`, specify `sd_cm2` and physical parameters `mms_kg`,
`cms_m_per_n`, `rms_ns_m`, `bl_tm`, `re_ohm`, optional `le_h`.
`observations[]` contain a ZMA `file` or `frequency_hz`, `real`, `imag`.
Each can declare `added_mass_g` or `sealed_volume_l`. Free-air-only fitting requires
known Mms or Bl; multiple known loads can establish scale. The sealed-volume
identification model is ideal, rigid and unfilled.

`inductance_kind`: `constant`, `leach` (inductance_k, inductance_n),
`lr2` (le_h,l2_h,r2_ohm), `semi_inductance` (leb_mh,le_mh,ke,rss_ohm).
Optional `creep_beta`, `creep_transition_hz` add the logarithmic compliance law.
`ignore_phase` fits magnitudes only and reduces available information.

For `mode: radiator`, provide an explicit `enclosure_network` under `network`,
`radiator_id`, `driver_id`, and radiator fields in initial/known. Measured motor
impedance constrains the diaphragm through the specified chamber coupling.
Observation `added_mass_g` overrides the radiator's added mass.

Outputs retain every evaluated parameter set, predicted/observed impedance, residual,
optimizer termination, distances to bounds, scaled Jacobian singular values/rank,
and driver T/S values when applicable. No automatic fit-quality verdict is made.

See [driver identification](../../references/driver-impedance-identification.md).
