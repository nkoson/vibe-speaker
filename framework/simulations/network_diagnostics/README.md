# network_diagnostics

`network` is a `board_nodal` input. `programme` supplies `voltage_rms`,
`spectrum: pink|white` or `relative_psd` on the network grid, optional `band_hz`,
and `crest_factor`. Multiple active sources require `reference_voltage_rms` to
define a common scaling of their relative amplitudes/phases.

Returns frequency-dependent complex load/EPDR and programme-integrated component
and load power, voltage and current RMS. Peak quantities use the caller's declared
**output** crest factor; PSD alone cannot determine output peaks. Ratings are
echoed for interpretation, never used to choose parts.

See [passive network diagnostics](../../references/passive-network-diagnostics.md).
