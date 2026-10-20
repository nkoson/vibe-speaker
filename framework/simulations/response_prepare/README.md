# response_prepare

Operations: `ir_to_fr`, `merge`, `sum`, `average`, `product`, `difference`, `ratio`,
`rms`, `maximum`, `minimum_phase`, `time_align`, `digitize`.

Most operations use `frequencies` and `responses[]`. A response is either a
`reference: {file,path,frequency_path}`, a `file` containing Hz/SPL/phase, or
`frequency_hz`, `real`, `imag` arrays. Optional gain/scale, polarity and `delay_s`
are explicit. `known_delay_s` removes/restores delay during interpolation.
Extrapolation is rejected. `nearfield_radius_m` plus `farfield_distance_m` applies
the low-ka piston scale before summation. Correct measurement voltage and cabinet
factors before blending. `smoothing_octaves` performs complex band averaging.

`merge` takes low/high responses and `blend_band_hz`; blending is linear in complex
pressure with log-frequency weights. `match_overlap` fits gain/delay within
`match_gain_bounds_db` and `match_delay_bounds_s`, returning its residual.
`time_align` takes individual A/B and combined measurements plus `delay_bounds_s`;
it returns all local numerical delay solutions and costs, not a selected acoustic
centre. Magnitude-only alignment can have multiple solutions.

`ir_to_fr` takes `impulse: {samples,sample_rate_hz}` or `{wav_file,channel}`.
Set `sample_basis: discrete_impulse|continuous_impulse_density`,
`calibration`, `reference_time_s`, optional `fft_length`, and
`window: {start_s,stop_s,kind,alpha}`. Supported windows: boxcar, Hann, Hamming,
Blackman, Blackman-Harris and Tukey. WAV integer samples are normalized to full scale;
conversion to Pa or a transfer requires the supplied calibration.
Returns positive-frequency complex response, DC separately, window and gated samples.

Alternatively `window.left_s` and `window.right_s` define independent half-windows
around `reference_time_s`, with optional `left_kind` and `right_kind`. The gate
retains the original time grid. `digitize` also accepts `axes.value_scale: log`
for logarithmic impedance axes.

`digitize` converts supplied `pixel_points` using
`axes: {x_pixels,frequency_hz,y_pixels,values,frequency_scale}`.
This coordinate transform does not identify a curve automatically or supply measured phase.

See [measured response processing](../../references/measured-response-processing.md).
