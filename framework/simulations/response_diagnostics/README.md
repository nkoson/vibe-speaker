# response_diagnostics

`response` supplies `{file,path,frequency_path}` or inline `frequency_hz,real,imag`.
Outputs complex response, unwrapped phase and `group_delay_s`. `known_delay_s`
removes/restores known delay before phase differentiation. `phase_floor_db`
(default -80 relative to peak) masks zeros and their derivative neighbors.

Optional `minimum_phase: {lower_rolloff_db_oct,upper_rolloff_db_oct}` adds reconstructed
minimum and excess phase/group delay; extrapolated magnitude is an assumption.

`time_domain: {sample_rate_hz,fft_length,dc_real,extension,delay_s,nyquist_real}`
adds impulse, step and energy-time curves. `extension: error` is default; `zero` and
`hold` are explicit alternatives when positive FFT bins leave the data band.
DC must be supplied. Nyquist must be real for a real impulse; its discarded imaginary
part is reported. `delay_s` positions the circular reconstruction.

`impulse_samples` are discrete convolution coefficients;
`impulse_density_per_s=sample_rate_hz*impulse_samples`. Step is the cumulative sum
of coefficients. The result states its period, extrapolated bins and FFT roundtrip
error. These are not empirical accuracy or audibility assessments.

See [measured response processing](../../references/measured-response-processing.md).
