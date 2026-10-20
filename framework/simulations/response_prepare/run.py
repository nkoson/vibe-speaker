#!/usr/bin/env python3
"""Window impulses, combine complex responses, and digitize supplied graph coordinates."""
import sys
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.optimize import least_squares
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, response_data
NAME = "response_prepare"
VERSION = "1.2"


def curve(record, f, base_dir):
    if "reference" in record:
        p = cli.curve_from_reference({"extrapolation": "error", **record["reference"]}, base_dir, f)
    elif "file" in record:
        fp, p, _ = response_data.read_table(cli.resolve_path(record["file"], base_dir),
                                          record.get("quantity", "pressure"), record.get("phase_assumption"))
        p = response_data.resample(f, fp, p, float(record.get("known_delay_s", 0)))
    else:
        fp = np.asarray(record["frequency_hz"], float)
        p = cli.complex_from_record(record)
        p = response_data.resample(f, fp, p, float(record.get("known_delay_s", 0)))
    scale = float(record.get("scale", 1))*10**(float(record.get("gain_db", 0))/20)
    scale *= float(record.get("polarity", 1))
    if "nearfield_radius_m" in record:
        scale *= cli.positive(record["nearfield_radius_m"], "nearfield_radius_m")/(2*cli.positive(record["farfield_distance_m"], "farfield_distance_m"))
    return p*scale*np.exp(-2j*np.pi*f*float(record.get("delay_s", 0)))


def impulse(params, base_dir):
    spec = params["impulse"]
    if "wav_file" in spec:
        fs, data = wavfile.read(cli.resolve_path(spec["wav_file"], base_dir))
        if np.issubdtype(data.dtype, np.integer):
            if data.dtype == np.uint8:
                data = (data.astype(float)-128)/128
            else:
                data = data.astype(float)/2**(8*data.dtype.itemsize-1)
        if data.ndim > 1:
            data = data[:, int(spec.get("channel", 0))]
    else:
        fs = cli.positive(spec.get("sample_rate_hz"), "sample_rate_hz")
        data = np.asarray(spec["samples"], float)
    if data.ndim != 1 or len(data) < 2 or not np.all(np.isfinite(data)):
        raise cli.InputError("impulse samples must be a finite vector")
    fs = float(fs)
    reference = float(spec.get("reference_time_s", 0))
    t = np.arange(len(data))/fs
    window = params.get("window", {})
    start, stop = float(window.get("start_s", 0)), float(window.get("stop_s", t[-1]+1/fs))
    if not 0 <= start < stop <= len(data)/fs+1e-12:
        raise cli.InputError("window must lie inside the sampled impulse")
    sel = (t >= start) & (t < stop)
    n = int(params.get("fft_length", len(data)))
    if n < len(data):
        raise cli.InputError("fft_length cannot truncate input samples")
    w = np.zeros(len(data))
    kind = window.get("kind", "boxcar")
    if kind not in ("boxcar", "hann", "hamming", "blackman", "blackmanharris", "tukey"):
        raise cli.InputError("unsupported time window")
    taper = ("tukey", float(window.get("alpha", .25))) if kind == "tukey" else kind
    w[sel] = signal.get_window(taper, int(sel.sum()), fftbins=False)
    if "left_s" in window or "right_s" in window:
        left=cli.positive(window.get("left_s",0),"window.left_s",zero=True)
        right=cli.positive(window.get("right_s"),"window.right_s")
        if not 0 <= reference <= t[-1]:
            raise cli.InputError("two-sided window reference must lie inside the samples")
        w=np.zeros(len(data))
        for side,duration in (("left",left),("right",right)):
            if duration==0:continue
            phase=(reference-t)/duration if side=="left" else (t-reference)/duration
            inside=(phase>=0)&(phase<=1)
            window_kind=window.get(side+"_kind",kind)
            if window_kind not in ("boxcar","hann","hamming","blackman","blackmanharris","tukey"):
                raise cli.InputError("unsupported sided window")
            window_spec=("tukey",float(window.get("alpha",.25))) if window_kind=="tukey" else window_kind
            # A densely sampled half-window avoids shifting the acquisition time grid.
            half=signal.get_window(window_spec,8193,fftbins=False)[4096:]
            w[inside]=np.interp(phase[inside],np.linspace(0,1,len(half)),half)
        w[np.isclose(t,reference,atol=.1/fs)]=1
        start=max(0,reference-left);stop=min(len(data)/fs,reference+right)
    h = data*w*float(spec.get("calibration", 1))
    basis = spec.get("sample_basis", "discrete_impulse")
    if basis not in ("discrete_impulse", "continuous_impulse_density"):
        raise cli.InputError("unknown impulse sample_basis")
    spectrum = np.fft.rfft(h, n=n) / (fs if basis == "continuous_impulse_density" else 1)
    f = np.fft.rfftfreq(n, 1/fs)
    spectrum *= np.exp(2j*np.pi*f*reference)
    return dict(f_hz=f[1:], response=spectrum[1:], dc=spectrum[0], sample_rate_hz=fs,
                time_s=t, window=w, windowed_impulse=h, gate_duration_s=stop-start,
                gate_frequency_scale_hz=1/(stop-start), phase_reference_time_s=reference,
                sample_basis=basis)


def compute(params, base_dir):
    operation = params.get("operation", "merge")
    if operation == "ir_to_fr":
        return impulse(params, base_dir)
    if operation == "digitize":
        p = np.asarray(params["pixel_points"], float)
        x0, x1 = params["axes"]["x_pixels"]
        f0, f1 = params["axes"]["frequency_hz"]
        y0, y1 = params["axes"]["y_pixels"]
        d0, d1 = params["axes"]["values"]
        if p.ndim != 2 or p.shape[1] != 2 or x0 == x1 or y0 == y1 or min(f0, f1) <= 0:
            raise cli.InputError("digitization needs valid pixel pairs and nondegenerate axes")
        u = (p[:, 0]-x0)/(x1-x0)
        f = np.exp(np.log(f0)+u*np.log(f1/f0)) if params["axes"].get("frequency_scale", "log") == "log" else f0+u*(f1-f0)
        fraction=(p[:, 1]-y0)/(y1-y0)
        if params["axes"].get("value_scale","linear")=="log":
            if min(d0,d1)<=0:raise cli.InputError("logarithmic values require positive endpoints")
            values=np.exp(np.log(d0)+fraction*np.log(d1/d0))
        else:
            values = d0+fraction*(d1-d0)
        order = np.argsort(f)
        if np.any(np.diff(f[order]) <= 0):
            raise cli.InputError("digitized frequencies must be unique")
        return dict(f_hz=f[order], values=values[order], evidence="digitized supplied coordinates; phase is not measured")
    f = cli.frequency_grid(params.get("frequencies"))
    records = cli.require(params, "responses")
    if not records:
        raise cli.InputError("responses cannot be empty")
    curves = np.stack([curve(r, f, base_dir) for r in records])
    extra = {}
    if operation in ("volume_velocity_to_pressure", "pressure_to_volume_velocity"):
        if len(curves) != 1:
            raise cli.InputError("radiation conversion needs exactly one response")
        distance = cli.positive(params.get("distance_m"), "distance_m")
        space = params.get("radiation_space")
        if space not in ("full", "half"):
            raise cli.InputError("radiation_space must explicitly be full or half")
        phase = params.get("phase_reference")
        if phase not in ("absolute", "intrinsic"):
            raise cli.InputError("phase_reference must explicitly be absolute or intrinsic")
        omega = 2*np.pi*f
        factor = 1j*omega*cli.RHO / ((4 if space == "full" else 2)*np.pi*distance)
        if phase == "absolute":
            factor *= np.exp(-1j*omega*distance/cli.C)
        response = curves[0]*factor if operation == "volume_velocity_to_pressure" else curves[0]/factor
        extra["radiation_conversion"] = dict(
            distance_m=distance, radiation_space=space, phase_reference=phase,
            output_units="Pa" if operation == "volume_velocity_to_pressure" else "m3/s",
            scope="Equivalent compact-source far field; half space assumes an infinite rigid plane. "
                  "Inverting calibrated pressure yields equivalent flow, not measured cone motion.")
    elif operation == "merge":
        if len(curves) != 2:
            raise cli.InputError("merge needs low and high responses; sum cone/outlets beforehand")
        low, high = curves
        a, b = params["blend_band_hz"]
        if not f[0] <= a < b <= f[-1]:
            raise cli.InputError("blend band must lie inside the response grid")
        weight = np.clip(np.log(f/a)/np.log(b/a), 0, 1)
        if params.get("match_overlap"):
            sel = (f >= a) & (f <= b)
            if sel.sum() < 3:
                raise cli.InputError("overlap fitting needs at least three samples")
            delay_bounds = params.get("match_delay_bounds_s", [-.001, .001])
            gain_bounds = params.get("match_gain_bounds_db", [-20, 20])
            scale = max(abs(high[sel]).max(), 1e-30)
            def residual(x):
                delta = (low[sel]*10**(x[0]/20)*np.exp(-2j*np.pi*f[sel]*x[1])-high[sel])/scale
                return np.r_[delta.real, delta.imag]
            fits = [least_squares(residual, [np.clip(0, *gain_bounds), start],
                                  bounds=([gain_bounds[0], delay_bounds[0]], [gain_bounds[1], delay_bounds[1]]),
                                  x_scale=[1, max(delay_bounds[1]-delay_bounds[0], 1e-9)])
                    for start in np.linspace(*delay_bounds, 7)]
            fitted = min(fits, key=lambda r: np.dot(r.fun, r.fun))
            low = low*10**(fitted.x[0]/20)*np.exp(-2j*np.pi*f*fitted.x[1])
            extra["overlap_fit"] = dict(gain_db=fitted.x[0], delay_s=fitted.x[1],
                                        normalized_squared_residual=float(np.dot(fitted.fun, fitted.fun)),
                                        interpretation="numerical calibration estimate; not an acceptance decision")
        domain = params.get("blend_domain", "complex")
        if domain == "complex":
            response = low*(1-weight)+high*weight
        elif domain == "log_magnitude_phase":
            if np.any(abs(low) < 1e-30) or np.any(abs(high) < 1e-30):
                raise cli.InputError("log-magnitude/phase merging cannot include a response null")
            # Relative unwrapped phase retains endpoint delay conventions without
            # independently choosing incompatible phase branches for each input.
            ratio = high/low
            response = low*np.exp(weight*(np.log(abs(ratio))+1j*np.unwrap(np.angle(ratio))))
        else:
            raise cli.InputError("blend_domain must be complex or log_magnitude_phase")
        extra["high_weight"] = weight
        extra["blend_domain"] = domain
    elif operation == "sum":
        response = curves.sum(axis=0)
    elif operation == "average":
        response = curves.mean(axis=0)
    elif operation == "product":
        response = curves.prod(axis=0)
    elif operation in ("difference", "ratio"):
        if len(curves) != 2:
            raise cli.InputError("difference/ratio needs two responses")
        if operation == "ratio" and np.any(abs(curves[1]) < 1e-30):
            raise cli.InputError("ratio denominator contains zero")
        response = curves[0]-curves[1] if operation == "difference" else curves[0]/curves[1]
    elif operation in ("rms", "maximum"):
        magnitude = np.sqrt(np.mean(abs(curves)**2, axis=0)) if operation == "rms" else abs(curves).max(axis=0)
        return dict(f_hz=f, magnitude=magnitude, phase_basis="undefined for incoherent magnitude operation")
    elif operation == "minimum_phase":
        response = acoustics.minimum_phase(f, f, acoustics.db(curves[0]),
                                           params.get("lower_rolloff_db_oct", 0), params.get("upper_rolloff_db_oct", 0))
        extra["phase_basis"] = "reconstructed_minimum_phase"
    elif operation == "time_align":
        if len(curves) != 3:
            raise cli.InputError("time_align needs individual A, individual B and measured combined response")
        bounds = params["delay_bounds_s"]
        scale = max(abs(curves[2]).max(), 1e-30)
        def residual(delay):
            return (abs(curves[0]+curves[1]*np.exp(-2j*np.pi*f*delay[0]))-abs(curves[2]))/scale
        trials = [least_squares(residual, [start], bounds=([bounds[0]], [bounds[1]]), diff_step=1e-4)
                  for start in np.linspace(*bounds, 21)]
        return dict(f_hz=f, trials=[dict(delay_s=t.x[0], squared_residual=float(t.fun@t.fun)) for t in trials],
                    numerical_minimum_index=int(np.argmin([t.fun@t.fun for t in trials])),
                    interpretation="delay estimates can be ambiguous; the agent interprets residuals and bounds")
    else:
        raise cli.InputError("unknown response operation")
    if params.get("smoothing_octaves"):
        width = cli.positive(params["smoothing_octaves"], "smoothing_octaves")
        response = np.array([response[abs(np.log2(f/x)) <= width/2].mean() for x in f])
        extra["smoothing"] = "complex box average on a logarithmic frequency band"
    return dict(f_hz=f, response=response, magnitude_db=acoustics.db(response), **extra)


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, __doc__, [
        "Response processing preserves explicit phase and scaling; incoherent operations do not invent complex phase.",
        "See framework/references/measured-response-processing.md. Imported/digitized data retains acquisition uncertainty."]))
