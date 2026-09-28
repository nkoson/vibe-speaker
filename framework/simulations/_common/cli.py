"""Command-line and JSON plumbing shared by every simulation application.

Every application reads one JSON parameter document, computes, and writes one
JSON result document into the requested folder. Nothing here judges a result.
"""
import argparse
import datetime
import json
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np


class InputError(ValueError):
    """A parameter document that the simulation cannot use."""


# The environment every model is evaluated in. They are written into every result
# document so a curve can be re-derived, and compared, years later: one commercial
# solver shipped a lumped-element error across four builds, and the defence against
# that is a recorded version and a recorded constant, not trust.
RHO = 1.204
C = 343.0
P0 = 20e-6
MU = 1.825e-5

# Two statements that belong on every result document this repository writes, whatever the model.
# The first is the hole under every simulated figure here; the second is the way that hole is most
# often papered over, so it is stated as a prohibition rather than as a caveat.
UNIVERSAL_VALIDITY = [
    "No source consulted states the decibel or degree error between a simulated and a measured response, for any tool. "
    "The comparison is conventionally reported in the literature without a number at all, so every result here carries "
    "no error bar from the literature - only its declared assumptions and the validity range in this document.",
    "NEVER QUOTE NUMERICAL ACCURACY AS AGREEMENT WITH MEASUREMENT. A wave solver's numerical error against its own "
    "governing equation is published and excellent - better than 0.1 percent for analytic room modes - and it says "
    "nothing whatever about how far the answer sits from a microphone.",
]

CONSTANTS = {
    "speed_of_sound_m_s": C,
    "air_density_kg_m3": RHO,
    "dynamic_viscosity_pa_s": MU,
    "reference_pressure_pa": P0,
}


def to_jsonable(value):
    """Convert numpy scalars, arrays and complex values into plain JSON types."""
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        if np.iscomplexobj(value):
            return complex_record(value)
        return [to_jsonable(v) for v in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        v = float(value)
        return v if math.isfinite(v) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, Path):
        return str(value)
    return value


def complex_record(z):
    """Complex array as real/imag plus magnitude in dB and unwrapped phase in degrees."""
    z = np.asarray(z, complex)
    magnitude = np.abs(z)
    return {
        "real": to_jsonable(z.real),
        "imag": to_jsonable(z.imag),
        "magnitude": to_jsonable(magnitude),
        "magnitude_db": to_jsonable(20 * np.log10(np.maximum(magnitude, 1e-30))),
        "phase_deg": to_jsonable(np.rad2deg(np.unwrap(np.angle(z)))),
    }


def complex_from_record(record):
    """Inverse of complex_record: accept real/imag arrays or magnitude/phase arrays."""
    if isinstance(record, dict):
        if "real" in record and "imag" in record:
            return np.asarray(record["real"], float) + 1j * np.asarray(record["imag"], float)
        if "magnitude" in record and "phase_deg" in record:
            return np.asarray(record["magnitude"], float) * np.exp(1j * np.deg2rad(np.asarray(record["phase_deg"], float)))
        if "magnitude_db" in record and "phase_deg" in record:
            return 10 ** (np.asarray(record["magnitude_db"], float) / 20) * np.exp(1j * np.deg2rad(np.asarray(record["phase_deg"], float)))
    raise InputError("A complex array needs real/imag or magnitude/phase_deg arrays")


def frequency_grid(spec, default_min=10.0, default_max=20000.0, default_points=600, default_spacing="log"):
    """Build a frequency vector from a grid specification or an explicit list."""
    spec = spec or {}
    if "values_hz" in spec:
        f = np.asarray(spec["values_hz"], float)
    else:
        lo = float(spec.get("min_hz", default_min))
        hi = float(spec.get("max_hz", default_max))
        n = int(spec.get("points", default_points))
        if lo <= 0 or hi <= lo or n < 2:
            raise InputError("frequencies need 0 < min_hz < max_hz and at least two points")
        if spec.get("spacing", default_spacing) == "linear":
            f = np.linspace(lo, hi, n)
        else:
            f = np.geomspace(lo, hi, n)
    extra = spec.get("extra_hz")
    if extra:
        f = np.r_[f, np.asarray(extra, float)]
    f = np.unique(f)
    if np.any(~np.isfinite(f)) or np.any(f <= 0):
        raise InputError("frequencies must be positive finite numbers")
    return f


def require(document, *keys, label="input"):
    """Return the nested value or raise a readable error naming the missing key."""
    value = document
    path = label
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            raise InputError(f"{path} is missing '{key}'")
        value = value[key]
        path = f"{path}.{key}"
    return value


def positive(value, name, zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"{name} must be a finite number")
    if value < 0 or (value == 0 and not zero):
        raise InputError(f"{name} must be {'nonnegative' if zero else 'positive'}")
    return float(value)


def load_json(path):
    path = Path(path)
    if not path.exists():
        raise InputError(f"file not found: {path}")
    with open(path) as fp:
        return json.load(fp)


def resolve_path(value, base_dir):
    path = Path(value)
    if not path.is_absolute():
        path = Path(base_dir) / path
    return path


def dotted(document, path):
    """Access nested keys through a dotted path such as results.curves.0.z_ohm."""
    value = document
    for part in path.split("."):
        if isinstance(value, list):
            value = value[int(part)]
        elif isinstance(value, dict):
            if part not in value:
                raise InputError(f"path '{path}' not found at '{part}'")
            value = value[part]
        else:
            raise InputError(f"path '{path}' cannot descend into a scalar at '{part}'")
    return value


def file_reference(spec, base_dir):
    """Load {"file": "...json", "path": "dotted.path"} and return the referenced value."""
    document = load_json(resolve_path(require(spec, "file", label="file reference"), base_dir))
    return dotted(document, spec["path"]) if spec.get("path") else document


def interp_complex(f_target, f_source, z_source):
    """Log-frequency Cartesian interpolation of a complex curve; holds the end values outside the source band."""
    f_target = np.asarray(f_target, float)
    f_source = np.asarray(f_source, float)
    z_source = np.asarray(z_source, complex)
    order = np.argsort(f_source)
    lf_s = np.log(f_source[order])
    lf_t = np.log(f_target)
    return np.interp(lf_t, lf_s, z_source.real[order]) + 1j * np.interp(lf_t, lf_s, z_source.imag[order])


def interp_real(f_target, f_source, y_source):
    f_target = np.asarray(f_target, float)
    f_source = np.asarray(f_source, float)
    order = np.argsort(f_source)
    return np.interp(np.log(f_target), np.log(f_source[order]), np.asarray(y_source, float)[order])


def curve_from_reference(spec, base_dir, f_target, kind="complex"):
    """Read a curve from another simulation's result file and interpolate it onto f_target.

    spec: {"file": path, "frequency_path": "results.f_hz", "path": "results.z_ohm"}
    The referenced value is a complex record (real/imag) or a real list.
    """
    document = load_json(resolve_path(require(spec, "file", label="curve reference"), base_dir))
    f_source = np.asarray(dotted(document, spec.get("frequency_path", "results.f_hz")), float)
    value = dotted(document, require(spec, "path", label="curve reference"))
    if kind == "complex":
        return interp_complex(f_target, f_source, complex_from_record(value))
    return interp_real(f_target, f_source, value)


def write_document(path, document):
    """Publish a complete JSON document atomically, never a partially written result."""
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as fp:
            temporary = Path(fp.name)
            json.dump(to_jsonable(document), fp, indent=1)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run(name, version, compute, description, notes, validity=()):
    """Parse the standard arguments, run compute(params, base_dir) and write the result document.

    compute returns a dict of results. The written document carries the
    simulation identity, the echoed inputs, the model notes, the validity block
    and the results. A compute that knows a numeric validity bound returns it
    under the reserved results key "validity"; it is lifted into the document.
    The validity block always carries UNIVERSAL_VALIDITY as well, because those
    two statements are true of every model here and a reader should not have to
    find them somewhere else.
    """
    parser = argparse.ArgumentParser(prog=name, description=description)
    parser.add_argument("--input", required=True, help="JSON parameter file, or - for stdin")
    parser.add_argument("--out", required=True, help="folder that receives the result JSON")
    parser.add_argument("--name", default=name, help="result file name without extension")
    args = parser.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    if Path(args.name).name != args.name or args.name in ("", ".", ".."):
        parser.error("--name must be a file stem, not a path")
    path = out_dir / f"{args.name}.json"
    if args.input != "-" and path.resolve() == Path(args.input).resolve():
        parser.error("input and result paths must differ")
    # Invalidate before parsing inputs or computing: either can fail unexpectedly.
    path.unlink(missing_ok=True)
    params = None
    started = datetime.datetime.now(datetime.timezone.utc)
    try:
        if args.input == "-":
            params = json.load(sys.stdin)
            base_dir = Path.cwd()
        else:
            params = load_json(args.input)
            base_dir = Path(args.input).resolve().parent
        results = compute(params, base_dir)
    except (InputError, json.JSONDecodeError) as exc:
        document = {"simulation": name, "version": version, "status": "input_error", "error": str(exc), "inputs": params}
        write_document(path, document)
        print(f"input error: {exc}", file=sys.stderr)
        print(path)
        return 2
    computed_validity = results.pop("validity", None) if isinstance(results, dict) else None
    document = {
        "simulation": name,
        "version": version,
        "status": "computed",
        "generated_utc": started.isoformat(timespec="seconds"),
        "inputs": params,
        "model_notes": list(notes),
        "validity": {"app_version": version, "statements": list(validity),
                      "universal": list(UNIVERSAL_VALIDITY), **(computed_validity or {})},
        "constants": dict(CONSTANTS),
        "results": results,
    }
    write_document(path, document)
    print(path)
    return 0
