"""Observable differences between complex curves, without acceptance decisions."""
import numpy as np
from . import cli


def compare(f, actual, reference, floor_fraction=1e-6):
    f = np.asarray(f, float)
    a, r = np.asarray(actual, complex), np.asarray(reference, complex)
    if (f.ndim != 1 or len(f) < 2 or a.shape != f.shape or r.shape != f.shape
            or np.any(np.diff(f) <= 0) or np.any(f <= 0)
            or not np.all(np.isfinite(a)) or not np.all(np.isfinite(r))):
        raise cli.InputError("comparison needs matching finite complex curves on increasing positive frequencies")
    fraction = cli.positive(floor_fraction, "floor_fraction")
    floor = max(float(abs(r).max()) * fraction, 1e-30)
    error = abs(a-r) / np.maximum(abs(r), floor)
    db = 20*np.log10(np.maximum(abs(a), floor)/np.maximum(abs(r), floor))
    phase_mask = (abs(a) > floor) & (abs(r) > floor)
    phase = np.full(len(f), np.nan)
    phase[phase_mask] = np.rad2deg(np.angle(a[phase_mask]/r[phase_mask]))
    x = np.log(f)
    rms = lambda y: float(np.sqrt(np.trapezoid(y*y, x)/(x[-1]-x[0])))
    return dict(f_hz=f, magnitude_difference_db=db, phase_difference_deg=phase,
                relative_complex_error=error, absolute_complex_error=abs(a-r),
                rms_magnitude_difference_db=rms(db), max_magnitude_difference_db=float(abs(db).max()),
                rms_relative_complex_error=rms(error), max_relative_complex_error=float(error.max()),
                phase_excluded_count=int((~phase_mask).sum()), denominator_floor=floor)
