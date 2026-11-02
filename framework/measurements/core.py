"""Explicit units, time origin, windowing and comparison primitives."""
from dataclasses import dataclass, field
import numpy as np
from scipy import signal
from scipy.integrate import cumulative_trapezoid


class MeasurementError(ValueError):
    pass


def vector(value, name, minimum=2):
    a = np.asarray(value, dtype=float)
    if a.ndim != 1 or len(a) < minimum or not np.all(np.isfinite(a)):
        raise MeasurementError(f'{name} must be a finite vector with at least {minimum} values')
    return a


@dataclass
class Measurement:
    name: str
    quantity: str
    frequency: np.ndarray
    magnitude: np.ndarray
    phase: np.ndarray | None = None
    metadata: dict = field(default_factory=dict)
    samples: np.ndarray | None = None
    sample_interval: float | None = None
    start_time: float | None = None
    calibration: list = field(default_factory=list)

    def __post_init__(self):
        if self.quantity not in ('spl', 'impedance', 'transfer'):
            raise MeasurementError('quantity must be spl, impedance or transfer')
        self.frequency = vector(self.frequency, 'frequency')
        self.magnitude = vector(self.magnitude, 'magnitude')
        if len(self.frequency) != len(self.magnitude) or np.any(self.frequency <= 0) or np.any(np.diff(self.frequency) <= 0):
            raise MeasurementError('frequency/magnitude lengths must match; positive frequencies must increase strictly')
        if self.quantity == 'impedance' and np.any(self.magnitude < 0):
            raise MeasurementError('impedance magnitude cannot be negative')
        if self.phase is not None:
            self.phase = vector(self.phase, 'phase')
            if len(self.phase) != len(self.frequency):
                raise MeasurementError('phase length mismatch')
        if self.samples is not None:
            self.samples = vector(self.samples, 'impulse')
            if not self.sample_interval or self.sample_interval <= 0 or not np.isfinite(self.sample_interval):
                raise MeasurementError('invalid impulse sample interval')
            if self.start_time is None or not np.isfinite(self.start_time):
                raise MeasurementError('impulse needs a finite start time')

    def amplitude(self):
        if self.quantity == 'impedance':
            return self.magnitude
        return 10 ** (self.magnitude / 20) * (20e-6 if self.quantity == 'spl' else 1)

    def complex_response(self):
        if self.phase is None:
            raise MeasurementError('complex response requires phase; missing phase is not zero phase')
        return self.amplitude() * np.exp(1j * np.deg2rad(self.phase))


def smooth_power(f, magnitude_db, fraction):
    """Uniform log-frequency mean of power over exactly 1/fraction octave.

    Display-only smoothing, not REW's proprietary smoothing algorithm. Integrate
    piecewise-linear power on log2(f); don't average phase or change stored data.
    """
    f = vector(f, 'frequency'); y = vector(magnitude_db, 'magnitude')
    if len(f) != len(y) or np.any(f <= 0) or np.any(np.diff(f) <= 0):
        raise MeasurementError('invalid smoothing grid')
    if fraction == 0:
        return y.copy()
    if not np.isfinite(fraction) or fraction <= 0:
        raise MeasurementError('smoothing fraction must be positive or zero')
    x = np.log2(f); ref = np.max(y); power = 10 ** ((y-ref)/10)
    integ = np.r_[0., cumulative_trapezoid(power, x)]
    def integral_at(q):
        i = np.clip(np.searchsorted(x, q, side='right')-1, 0, len(x)-2)
        dx = q-x[i]
        return integ[i] + power[i]*dx + .5*(power[i+1]-power[i])/(x[i+1]-x[i])*dx**2
    lo = np.maximum(x[0], x-.5/fraction); hi = np.minimum(x[-1], x+.5/fraction)
    return ref + 10*np.log10(np.maximum((integral_at(hi)-integral_at(lo))/(hi-lo), 1e-300))


def windowed_response(m, left_ms, right_ms, reference_ms=0., kind='tukey', taper=.25, fft_length=None):
    """Custom two-sided gate; never move t=0 or automatically centre individual peaks."""
    if m.samples is None or m.quantity == 'impedance':
        raise MeasurementError('IR processing needs an acoustic/transfer impulse')
    if not np.isfinite([left_ms, right_ms, reference_ms, taper]).all() or left_ms < 0 or right_ms <= 0 or not 0 < taper <= 1:
        raise MeasurementError('invalid gate durations, reference or taper')
    if kind not in ('tukey', 'hann', 'rectangular'):
        raise MeasurementError('unknown window')
    if m.metadata.get('ir_processing_unsupported'):
        raise MeasurementError('IR processing unsupported: ' + '; '.join(m.metadata['ir_processing_unsupported']))
    t = m.start_time + np.arange(len(m.samples))*m.sample_interval
    ref = reference_ms/1000; left = left_ms/1000; right = right_ms/1000
    if ref-left < t[0]-1e-12 or ref+right > t[-1]+m.sample_interval+1e-12:
        raise MeasurementError('requested gate extends beyond recorded impulse')
    u = np.where(t < ref, (ref-t)/max(left, 1e-300), (t-ref)/right)
    w = np.zeros_like(t); inside = u <= 1
    if kind == 'rectangular':
        w[inside] = 1
    elif kind == 'hann':
        w[inside] = .5*(1+np.cos(np.pi*u[inside]))
    else:
        w[inside] = 1
        edge = inside & (u > 1-taper)
        w[edge] = .5*(1+np.cos(np.pi*(u[edge]-(1-taper))/taper))
    n = int(fft_length or 2**int(np.ceil(np.log2(len(t)))))
    if n < len(t) or n > 2**24:
        raise MeasurementError('FFT length must retain every impulse sample and be <= 2^24')
    f = np.fft.rfftfreq(n, m.sample_interval)
    h = np.fft.rfft(m.samples*w, n)*np.exp(-2j*np.pi*f*m.start_time)
    # REW sampled IR is peak-referenced; convert to RMS before its SPL offset.
    if 'ir_scale_to_rms' not in m.metadata:
        raise MeasurementError('IR scaling is missing; supply a calibrated impulse scale')
    h *= float(m.metadata['ir_scale_to_rms'])
    total_gain=np.zeros_like(f);total_phase=np.zeros_like(f)
    for cal in m.calibration:
        cf = np.asarray(cal['frequency_hz']); gain = np.interp(f, cf, cal['gain_db'])
        phase = np.interp(f, cf, np.unwrap(np.deg2rad(cal['phase_deg'])))
        total_gain+=gain;total_phase+=phase
    if m.metadata.get('limit_cal_boost_20db'):
        total_gain=np.maximum(total_gain,-20)
    h /= 10**(total_gain/20)*np.exp(1j*total_phase)
    keep = (f >= m.frequency[0]) & (f <= m.frequency[-1]) & (f > 0)
    f = f[keep]; h = h[keep]
    reference = 20e-6 if m.quantity == 'spl' else 1
    db = 20*np.log10(np.maximum(abs(h)/reference, 1e-300))
    metadata = {**m.metadata, 'processing': {'mode':'custom_ir', 'left_ms':left_ms,
        'right_ms':right_ms, 'reference_ms':reference_ms, 'window':kind, 'taper_fraction_each_side':taper,
        'fft_length':n, 'resolution_scale_hz':1/(left+right), 'right_window_scale_hz':1/right,
        'time_origin_changed':False, 'fdw_applied':False,
        'calibration_interpolation':'linear Hz gain and unwrapped phase; endpoint held outside calibration band',
        'calibration_applied':'embedded gain and phase once'}}
    return Measurement(m.name, m.quantity, f, db, np.rad2deg(np.angle(h)), metadata,
                       m.samples, m.sample_interval, m.start_time, m.calibration)


def impulse_diagnostics(m):
    if m.samples is None:
        return None
    t = m.start_time+np.arange(len(m.samples))*m.sample_interval
    envelope = abs(signal.hilbert(m.samples))
    peak = int(np.argmax(abs(m.samples))); ref = max(float(envelope.max()), 1e-300)
    peaks, _ = signal.find_peaks(envelope, distance=max(1, int(.0002/m.sample_interval)))
    candidates = [i for i in peaks if t[i] > t[peak]+.0005]
    candidates = sorted(candidates, key=lambda i: envelope[i], reverse=True)[:12]
    return {'peak_time_s':float(t[peak]), 'sample_rate_hz':1/m.sample_interval,
            'duration_s':len(t)*m.sample_interval,
            'later_envelope_peaks':[{'time_s':float(t[i]), 'after_main_peak_ms':float((t[i]-t[peak])*1000),
                                     'relative_db':float(20*np.log10(max(envelope[i]/ref,1e-300)))}for i in candidates],
            'interpretation':'Candidate reflections or ringing; source geometry and window comparisons distinguish them.'}


def compare(a, b, operation, common_timing=None):
    if a.quantity != b.quantity:
        raise MeasurementError('comparison quantities differ')
    lo=max(a.frequency[0],b.frequency[0]);hi=min(a.frequency[-1],b.frequency[-1])
    if lo>=hi:
        raise MeasurementError('responses have no overlapping frequency range')
    f=np.unique(np.r_[a.frequency[(a.frequency>=lo)&(a.frequency<=hi)], b.frequency[(b.frequency>=lo)&(b.frequency<=hi)]])
    # Interpolate log magnitude and unwrapped phase; no extrapolation or fitted offsets.
    def interp(m):
        mag=np.interp(np.log(f),np.log(m.frequency),m.magnitude)
        amp=mag if m.quantity=='impedance' else 10**(mag/20)*(20e-6 if m.quantity=='spl' else 1)
        ph=None if m.phase is None else np.interp(f,m.frequency,np.unwrap(np.deg2rad(m.phase)))
        return mag,amp,ph
    am,aa,ap=interp(a);bm,ba,bp=interp(b)
    out={'frequency_hz':f.tolist(),'operation':operation,'level_alignment_db':0.,'common_timing_basis':common_timing}
    if operation=='difference':
        out.update(values=(bm-am).tolist(), units='ohm' if a.quantity=='impedance' else 'dB',meaning='B minus A')
    elif operation=='bounds':
        if a.quantity=='impedance':raise MeasurementError('acoustic sum bounds require acoustic responses')
        ref=20e-6 if a.quantity=='spl' else 1
        out.update(upper_db=(20*np.log10(np.maximum(aa+ba,1e-300)/ref)).tolist(),
                   lower_db=(20*np.log10(np.maximum(abs(aa-ba),1e-300)/ref)).tolist(),
                   meaning='Triangle-inequality bounds, not an actual summed response')
    elif operation in ('sum','ratio'):
        if not common_timing or ap is None or bp is None:
            raise MeasurementError('complex arithmetic needs phase and an explicit common-timing basis; use bounds/difference otherwise')
        for m in (a,b):
            if m.metadata.get('processing',{}).get('mode')=='saved' and (m.metadata.get('saved_smoothing_octave_fraction') or 0)>0:
                raise MeasurementError('use unsmoothed complex data for sum/ratio, then smooth the result; saved response is smoothed')
        ah=aa*np.exp(1j*ap);bh=ba*np.exp(1j*bp)
        if operation=='ratio' and np.any(aa<=max(aa.max()*1e-12,1e-300)):
            raise MeasurementError('ratio denominator has a deep null; restrict the comparison band')
        h=ah+bh if operation=='sum' else bh/ah
        ref=20e-6 if a.quantity=='spl' and operation=='sum' else 1
        out.update(real=h.real.tolist(),imag=h.imag.tolist(),phase_deg=np.rad2deg(np.angle(h)).tolist(),
                   values=(abs(h) if a.quantity=='impedance' and operation=='sum' else 20*np.log10(np.maximum(abs(h)/ref,1e-300))).tolist(),
                   units='ohm' if a.quantity=='impedance' and operation=='sum' else 'dB')
    else:
        raise MeasurementError('unknown comparison operation')
    return out
