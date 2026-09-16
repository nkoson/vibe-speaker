#!/usr/bin/env python3
"""Descriptive statistics of response curves and differences between them, for evaluation and reference comparison."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, preference  # noqa: E402

NAME = "response_metrics"
VERSION = "1.2"
NOTES = [
    "Every figure is a property of the supplied curves on the stated bands; thresholds and tolerances are parameters you set, and the app only reports where the curve sits against them.",
    "Curves are resampled to a common log grid; a published curve given as points is interpolated between them and held outside its range.",
    "NBD, SM and AAD are computed on whatever curve you supply. The DEFINITIONS are not in doubt - they were read at first hand in Harman's patent - and what is approximate is the CURVE SET: a CTA-2034-A figure needs a complete 70-point orbit, which is what the spinorama application is for.",
    "Every metric is named with the curve it came from, as NBD_ON or SM_PIR. NBD, SM and AAD are each defined over any of the seven curves, so a bare NBD names nothing; name a curve's kind with curves[].curve to have the patent's own code used for it.",
    "LFX is defined on the sound power curve against the listening-window mean, so it needs both curves named. An on-axis f3 is not LFX and is usually the more flattering of the two.",
    "A preference score is deliberately not computed here. Two of its four terms are directivity measurements, and neither exists without the orbit.",
]
VALIDITY = [
    "These are statistics of the curves handed in. They inherit whatever the curves are worth, including the model assumptions and the reading uncertainty of any digitised datasheet curve behind them.",
    "NBD, SM, AAD and LFX are computed from the published definitions, which are confirmed at first hand. They are not CTA-2034-A figures here, because the curve set they are defined over is not available to this application - the hedge is the orbit, not the formula.",
    "A peak-to-peak ripple figure over a decade cannot tell a slow tilt from a narrow notch. NBD and SM exist because those two cost very differently and the ripple figure gives them the same number.",
]


def _smooth(f, y, octaves):
    if not octaves:
        return y
    out = np.empty_like(y)
    half = octaves / 2
    for i, fi in enumerate(f):
        sel = (f >= fi / 2 ** half) & (f <= fi * 2 ** half)
        out[i] = np.mean(y[sel])
    return out


def _load_curve(spec, f, base_dir):
    if "points" in spec:
        table = np.asarray(spec["points"], float)
        return np.interp(np.log(f), np.log(table[:, 0]), table[:, 1])
    ref = dict(spec)
    ref.setdefault("frequency_path", "results.f_hz")
    document = cli.load_json(cli.resolve_path(ref["file"], base_dir))
    fs = np.asarray(cli.dotted(document, ref["frequency_path"]), float)
    y = cli.dotted(document, ref["path"])
    if isinstance(y, dict):
        y = y.get("magnitude_db")
        if y is None:
            raise cli.InputError("referenced curve is complex without magnitude_db")
    return cli.interp_real(f, fs, y), (float(fs.min()), float(fs.max()))


def _stats(f, y, analysis):
    out = {}
    sens = analysis.get("sensitivity_band_hz", [500.0, 10000.0])
    inside = (f >= sens[0]) & (f <= sens[1])
    if np.any(inside):
        out["sensitivity_band_hz"] = list(sens)
        out["mean_in_sensitivity_band_db"] = float(np.mean(y[inside]))
        out["median_in_sensitivity_band_db"] = float(np.median(y[inside]))
    for band in analysis.get("ripple_bands_hz", [[100.0, 16000.0]]):
        sel = (f >= band[0]) & (f <= band[1])
        if np.any(sel):
            key = f"{int(band[0])}_{int(band[1])}"
            out[f"ripple_{key}_db"] = float(np.ptp(y[sel]))
            out[f"std_{key}_db"] = float(np.std(y[sel]))
            out[f"slope_{key}_db_per_octave"] = float(np.polyfit(np.log2(f[sel]), y[sel], 1)[0])
    ref_band = analysis.get("reference_band_hz", [150.0, 300.0])
    if np.any((f >= ref_band[0]) & (f <= ref_band[1])):
        cut = {}
        for level in analysis.get("cutoff_thresholds_db", [-3.0, -6.0, -10.0]):
            value, bound, reference = acoustics.sustained_cutoff(f, y, level, tuple(ref_band))
            cut[f"f{abs(int(level))}"] = dict(value_hz=value, bound=bound)
            cut["reference_level_db"] = float(reference)
        out["low_cutoffs"] = cut
    tol = analysis.get("band_tolerance_db")
    if tol and np.any(inside):
        out["band_within_tolerance"] = acoustics.band_within(f, y - out["mean_in_sensitivity_band_db"], float(tol), sens)
    hi = analysis.get("upper_reference_hz")
    if hi and f.min() <= hi <= f.max() and np.any(inside):
        out[f"level_at_{int(hi)}_relative_db"] = float(np.interp(np.log(hi), np.log(f), y) - out["mean_in_sensitivity_band_db"])
    octaves = analysis.get("octave_band_means", True)
    if octaves and np.any(inside):
        rows = []
        centre = 31.25
        while centre <= f.max():
            sel = (f >= centre / np.sqrt(2)) & (f <= centre * np.sqrt(2))
            if np.any(sel):
                rows.append(dict(centre_hz=centre, mean_db=float(np.mean(y[sel])), relative_db=float(np.mean(y[sel]) - out["mean_in_sensitivity_band_db"])))
            centre *= 2
        out["octave_bands"] = rows
    return out


APPROXIMATION_LABEL = ("approximation: computed from one supplied curve, not from a CTA-2034-A 70-point orbit. "
                       "Do not report it as a CTA-2034-A or Olive figure.")


def compute(params, base_dir):
    analysis = params.get("analysis") or {}
    f = cli.frequency_grid(params.get("frequencies"), 20.0, 20000.0, 600)
    smoothing = float(analysis.get("smoothing_octaves", 0.0))
    curves = {}
    rows = []
    for spec in cli.require(params, "curves"):
        loaded = _load_curve(spec, f, base_dir)
        coverage = None
        if isinstance(loaded, tuple):
            y, coverage = loaded
        else:
            y = loaded
        y = _smooth(f, y, smoothing) + float(spec.get("offset_db", 0.0))
        curves[spec["name"]] = y
        metrics = preference.curve_metrics(f, y, spec.get("standard_conformance", APPROXIMATION_LABEL),
                                           tuple(analysis.get("nbd_band_hz", preference.NBD_BAND_HZ)),
                                           tuple(analysis.get("sm_band_hz", preference.SM_BAND_HZ)),
                                           curve=spec.get("curve", spec["name"]))
        rows.append(dict(name=spec["name"], source_coverage_hz=coverage, spl_db=y,
                         statistics=_stats(f, y, analysis), preference_metrics=metrics))
    comparisons = []
    for comp in params.get("comparisons", []):
        a, b = curves[comp["a"]], curves[comp["b"]]
        band = comp.get("band_hz", [float(f.min()), float(f.max())])
        sel = (f >= band[0]) & (f <= band[1])
        offset = 0.0
        if comp.get("align", "none") == "mean_in_band":
            offset = float(np.mean(b[sel]) - np.mean(a[sel]))
        diff = a + offset - b
        octave_rows = []
        centre = 31.25
        while centre <= band[1]:
            osel = (f >= centre / np.sqrt(2)) & (f <= centre * np.sqrt(2)) & sel
            if np.any(osel):
                octave_rows.append(dict(centre_hz=centre, mean_difference_db=float(np.mean(diff[osel]))))
            centre *= 2
        comparisons.append(dict(a=comp["a"], b=comp["b"], band_hz=list(band), alignment_offset_applied_to_a_db=offset, difference_db=diff,
                                rms_difference_db=float(np.sqrt(np.mean(diff[sel] ** 2))), max_abs_difference_db=float(np.max(np.abs(diff[sel]))),
                                max_abs_difference_hz=float(f[sel][np.argmax(np.abs(diff[sel]))]), mean_difference_db=float(np.mean(diff[sel])),
                                octave_band_differences=octave_rows,
                                fraction_of_band_within_db={str(t): float(np.mean(np.abs(diff[sel]) <= t)) for t in comp.get("within_db", [1.0, 2.0, 3.0])}))
    results = dict(f_hz=f, smoothing_octaves=smoothing, curves=rows, comparisons=comparisons, validity=dict(statements=list(VALIDITY)))
    spec = analysis.get("lfx")
    if spec:
        power = cli.require(spec, "sound_power_curve", label="analysis.lfx")
        window = cli.require(spec, "listening_window_curve", label="analysis.lfx")
        for name in (power, window):
            if name not in curves:
                raise cli.InputError(f"analysis.lfx names a curve '{name}' that is not in curves[]")
        value = preference.lfx(f, curves[power], curves[window],
                               float(spec.get("upper_hz", preference.LFX_UPPER_HZ)),
                               tuple(spec.get("reference_band_hz", preference.LW_REFERENCE_BAND_HZ)))
        if value:
            results["lfq"] = dict(preference.lfq(f, curves[window], value["frequency_hz"],
                                                 float(spec.get("upper_hz", preference.LFX_UPPER_HZ))) or {},
                                  listening_window_curve=window)
        results["lfx"] = dict(value or {}, name="LFX", defined_on="sound_power",
                              sound_power_curve=power, listening_window_curve=window,
                              standard_conformance=spec.get("standard_conformance", APPROXIMATION_LABEL),
                              note="LFX carries no penalty for Q, group delay or distortion, so it rewards a boomy high-Q "
                                   "alignment exactly as much as a clean one; never use it alone as a bass objective.")
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Descriptive statistics and differences of response curves", NOTES, VALIDITY))
