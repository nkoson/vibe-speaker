"""Complex response import and explicit two-plane angular interpolation."""
import re
import numpy as np
from . import cli


def read_table(path, quantity="pressure", phase_assumption=None):
    """Read numeric whitespace/semicolon/comma exports; header lines precede data."""
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        text = line.strip()
        if not text or text.startswith(("#", "*", ";")):
            continue
        try:
            row = [float(v) for v in re.split(r"[\s,;]+", text)]
        except ValueError:
            if rows:
                raise cli.InputError(f"nonnumeric row within response data: {path}")
            continue
        if len(row) not in (2, 3):
            raise cli.InputError("response rows need Hz, magnitude, optional phase degrees")
        rows.append(row)
    if len(rows) < 2 or len({len(r) for r in rows}) != 1:
        raise cli.InputError("response needs at least two rows with consistent columns")
    data = np.asarray(rows)
    f = data[:, 0]
    if np.any(~np.isfinite(data)) or np.any(f <= 0) or np.any(np.diff(f) <= 0):
        raise cli.InputError("response frequencies must be positive, finite and strictly increasing")
    magnitude = 20e-6 * 10**(data[:, 1]/20) if quantity == "pressure" else data[:, 1]
    if np.any(magnitude < 0):
        raise cli.InputError("impedance magnitudes must be nonnegative")
    if data.shape[1] == 3:
        z = magnitude*np.exp(1j*np.deg2rad(data[:, 2]))
        phase_basis = "supplied"
    elif phase_assumption == "zero":
        z = magnitude.astype(complex)
        phase_basis = "assumed_zero"
    elif phase_assumption == "minimum_phase":
        from .acoustics import minimum_phase
        z = minimum_phase(f, f, 20*np.log10(np.maximum(magnitude, 1e-30)))
        phase_basis = "reconstructed_minimum_phase"
    else:
        raise cli.InputError("two-column data needs phase_assumption: zero or minimum_phase")
    return f, z, phase_basis


def resample(f, fp, values, delay_s=0., extrapolation="error"):
    outside = (f < fp[0]) | (f > fp[-1])
    if extrapolation not in ("error", "hold", "zero"):
        raise cli.InputError("extrapolation needs error, hold or zero")
    if extrapolation == "error" and np.any(outside):
        raise cli.InputError("requested frequencies exceed the response data band")
    out = cli.interp_complex(f, fp, values, delay_s=delay_s)
    if extrapolation == "zero":
        out[outside] = 0
    return out


def plane_values(plane, grid_f, f, angles):
    """Cartesian angular interpolation preserves signed nulls; no hidden mirroring."""
    aa = np.asarray(plane["angles_deg"], float)
    data = np.asarray(plane["real"], float)+1j*np.asarray(plane["imag"], float)
    ff, target = np.broadcast_arrays(f, angles)
    if (np.any(target < aa[0]-1e-7) or np.any(target > aa[-1]+1e-7)
            or np.any(ff < grid_f[0]) or np.any(ff > grid_f[-1])):
        raise cli.InputError("measured polar data does not cover the requested direction/frequency")
    unique_f, frequency_index = np.unique(ff.ravel(), return_inverse=True)
    values = np.stack([resample(unique_f, grid_f, row) for row in data])
    flat = target.ravel()
    right = np.clip(np.searchsorted(aa, flat, side="right"), 1, len(aa)-1)
    left = right-1
    fraction = (flat-aa[left])/(aa[right]-aa[left])
    return (values[left, frequency_index]*(1-fraction)+values[right, frequency_index]*fraction).reshape(ff.shape)


def measured_directivity(model, f, h, v):
    """Interpolate great-circle measurements; diagonals use declared transverse weights."""
    f, h, v = np.broadcast_arrays(f, h, v)
    theta = np.rad2deg(np.arccos(np.clip(np.cos(h)*np.cos(v), -1, 1)))
    lateral = np.sin(h)*np.cos(v)
    vertical = np.sin(v)
    horizontal = plane_values(model["horizontal"], np.asarray(model["frequency_hz"]), f,
                              theta*np.where(lateral < -1e-12, -1, 1))
    if model.get("axial_symmetry"):
        return horizontal
    elevation = plane_values(model["vertical"], np.asarray(model["frequency_hz"]), f,
                             theta*np.where(vertical < -1e-12, -1, 1))
    denominator = lateral**2+vertical**2
    weight = np.divide(lateral**2, denominator, out=np.ones_like(denominator), where=denominator > 1e-20)
    return weight*horizontal+(1-weight)*elevation


def full_sphere(model):
    for key in ("horizontal",) if model.get("axial_symmetry") else ("horizontal", "vertical"):
        a = model[key]["angles_deg"]
        if min(a) > -180 or max(a) < 180:
            return False
    return True
