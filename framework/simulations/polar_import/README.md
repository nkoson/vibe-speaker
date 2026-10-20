# polar_import

Normalize complex H/V angular measurements into a canonical source for
`source_response` (`acoustic.kind: simulation`). Each `responses[]` record provides
`file`, `plane: H|V`, `angle_deg`. Files contain Hz, SPL dB, phase degrees.
Require `voltage_rms`, `distance_m`, and `phase_reference`:

- `intrinsic`: propagation already removed.
- `absolute`: remove actual measurement path delay.
- `reference_delay_removed`: remove actual path minus nominal distance delay.

Optional `source_position_m`, `rotation_center_m` use x lateral, y forward, z up.
`acquisition_delay_s` is separately removed. Input voltage must be the measured
terminal voltage. `baffle` defaults to `included`; importing a cabinet measurement
and multiplying another baffle transfer is invalid.

Every plane requires a common zero-degree curve. `mirror_missing` and
`axial_symmetry` are explicit assumptions. Two-column files require
`phase_assumption: zero|minimum_phase`. Such data cannot use geometric phase
removal. `frequencies` defaults to the common input band; extrapolation is rejected.
`gate_ms` records the acquisition limit. Outputs retain hashes, coverage, phase basis,
pressure per volt and `measured_planes` directivity. H/V diagonals use declared
complex interpolation; missing angular coverage produces an input error when used.

See [measured response processing](../../references/measured-response-processing.md).
