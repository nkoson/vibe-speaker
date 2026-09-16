"""published_shape modes of source_response: multiply keeps both shapes, replace keeps only the published one."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

SIM = Path(__file__).resolve().parents[1] / "simulations"
sys.path.insert(0, str(SIM))
spec = importlib.util.spec_from_file_location("source_response_run", SIM / "source_response" / "run.py")
source_response = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source_response)

F = np.geomspace(20., 5000., 400)
BLEND = (150., 300.)


def lumped(f, corner_hz=400.):
    """A flat source with a first-order roll-off standing in for voice-coil inductance."""
    return 1. / (1. + 1j * f / corner_hz)


def published(corner_hz=400.):
    """The same roll-off as a datasheet curve, in dB relative to its own midband."""
    f = np.geomspace(60., 4000., 60)
    return {"points": [[float(x), float(20 * np.log10(abs(1. / (1. + 1j * x / corner_hz))))] for x in f]}


def applied(mode):
    p = lumped(F)
    shape = source_response._shape_above(published(), F, BLEND)
    if mode == "replace":
        shape = shape / source_response._shape_above(
            source_response._own_shape_record(F, p), F, BLEND)
    return p * shape


def relative_db(curve, reference_hz=200.):
    db = 20 * np.log10(np.abs(curve))
    return db - np.interp(np.log(reference_hz), np.log(F), db)


def test_replace_reproduces_the_published_slope_and_multiply_doubles_it():
    target = relative_db(lumped(F))
    at_2k = np.interp(np.log(2000.), np.log(F), target)
    replace = np.interp(np.log(2000.), np.log(F), relative_db(applied("replace")))
    multiply = np.interp(np.log(2000.), np.log(F), relative_db(applied("multiply")))
    assert abs(replace - at_2k) < 0.3, (replace, at_2k)
    # multiply keeps both roll-offs; the reconstruction of a sparse published curve costs a decibel or two
    assert abs(multiply - 2 * at_2k) < 2.0, (multiply, at_2k)


def test_both_modes_leave_the_band_below_the_blend_untouched():
    below = F < BLEND[0]
    for mode in ("multiply", "replace"):
        error_db = 20 * np.log10(np.abs(applied(mode))[below] / np.abs(lumped(F))[below])
        assert np.max(np.abs(error_db)) < 0.05, (mode, np.max(np.abs(error_db)))


def test_unknown_mode_is_an_input_error():
    from _common import cli
    params = {"acoustic": {"kind": "lf_box", "reference": {"file": "x.json"},
                           "published_shape": dict(published(), mode="scale")},
              "impedance": {"kind": "resistive", "r_ohm": 8}}
    try:
        source_response.compute(params, Path("."))
    except cli.InputError as error:
        assert "mode" in str(error)
    except Exception as error:  # the reference file is never reached
        raise AssertionError(f"expected an InputError about mode, got {error!r}")
    else:
        raise AssertionError("expected an InputError about mode")
