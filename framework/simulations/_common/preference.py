"""CTA-2034-A curve assembly and the Olive preference predictors.

Two different levels of confidence live here and they must not be conflated.

The **curve-assembly geometry** - which angles go in which group, and the sound-power ring weights -
comes from one open-source reimplementation of ANSI/CTA-2034-A, not from the standard text, which is
paywalled and was not read. Two of its details are known to differ from the literal standard and are
exposed as options with the standard's literal reading as the default.

The **four predictors and the regression that combines them** were read at first hand in Harman's own
patent (US 8,311,232 B2), which states the definitions, the bands and the coefficients, and they agree
exactly with what was previously recorded. The formulas are therefore not hedged here.

What remains hedged is the ORBIT: a metric computed from an incomplete orbit is an approximation and
is labelled as one, and it is never a CTA-2034-A figure. And a metric is meaningless without the curve
it was computed from, so every one is named with that curve - NBD_ON, SM_PIR - and never bare.
"""
import math

import numpy as np

from .cli import InputError

# Relative solid-angle weight of each 10-degree ring, on axis to 90 degrees, as published. The
# 90-degree ring carries about 32 times the weight of the on-axis point, which is the quantitative
# reason on-axis flatness barely moves sound power.
RING_WEIGHTS = [0.0304, 0.2378, 0.4501, 0.6227, 0.7535, 0.8479, 0.9131, 0.9554, 0.9791, 0.9867]

LISTENING_WINDOW = [("H", a) for a in (-30, -20, -10, 10, 20, 30)] + [("V", a) for a in (-10, 10)] + [("H", 0)]

EARLY_REFLECTION_GROUPS = {
    "floor_bounce": [("V", a) for a in (-20, -30, -40)],
    "ceiling_bounce": [("V", a) for a in (40, 50, 60)],
    "front_wall": [("H", a) for a in (0, -10, 10, -20, 20, -30, 30)],
    "side_wall": [("H", a) for a in (-80, -70, -60, -50, -40, 40, 50, 60, 70, 80)],
}
# The literal standard specifies only +/-90 and 180 degrees for the rear wall; the reimplementation
# uses the whole +/-90 to +/-170 fan. Early reflections, the in-room curve and the early-reflections
# DI all differ between tools because of it.
REAR_WALL = {
    "standard": [("H", -90), ("H", 90), ("H", 180)],
    "reimplementation": [("H", a) for a in (-170, -160, -150, -140, -130, -120, -110, -100, -90,
                                            90, 100, 110, 120, 130, 140, 150, 160, 170, 180)],
}

PIR_WEIGHTS = {"listening_window": 0.12, "early_reflections": 0.44, "sound_power": 0.44}

# Olive's generalized model over seventy loudspeakers, read in the patent at first hand.
PREFERENCE_COEFFICIENTS = {"constant": 12.69, "nbd_on": -2.49, "nbd_pir": -2.99, "lfx": -4.31, "sm_pir": 2.32}

# The relative contribution of each term, as the patent states them. On-axis wiggle and bass
# extension together carry nearly two thirds of the score.
TERM_CONTRIBUTIONS_PERCENT = {"nbd_on": 31.5, "lfx": 30.5, "nbd_pir": 20.5, "sm_pir": 17.5}

# The seven curves the patent defines NBD, SM and AAD over. LFX and LFQ are defined on sound power
# only, which is why an on-axis f3 is not LFX.
CURVE_CODES = {
    "on_axis": "ON", "listening_window": "LW", "early_reflections": "ER", "predicted_in_room": "PIR",
    "sound_power": "SP", "early_reflections_di": "ERDI", "sound_power_di": "SPDI",
}
CURVES_FOR_LFX = ("sound_power",)
AAD_BAND_HZ = (100.0, 16000.0)
AAD_REFERENCE_BAND_HZ = (200.0, 400.0)

NBD_BAND_HZ = (100.0, 12000.0)
SM_BAND_HZ = (100.0, 16000.0)
LFX_UPPER_HZ = 300.0
LW_REFERENCE_BAND_HZ = (300.0, 10000.0)


def curve_code(name):
    """The patent's short code for a curve, or a code derived from the caller's own name for one of its own."""
    key = str(name or "").lower()
    if key in CURVE_CODES:
        return CURVE_CODES[key], True
    derived = "".join(ch for ch in str(name or "curve").upper() if ch.isalnum()) or "CURVE"
    return derived, False


def metric_name(metric, curve):
    """NBD_ON, SM_PIR and so on. A metric without its curve is not a quantity."""
    code, _ = curve_code(curve)
    return f"{metric}_{code}"


def spin_angles():
    """The 70-point two-plane orbit: 36 horizontal and 34 vertical, the duplicated 0 and 180 dropped."""
    horizontal = [("H", a) for a in range(0, 360, 10)]
    vertical = [("V", a) for a in range(0, 360, 10) if a not in (0, 180)]
    return horizontal + vertical


def signed(angle_deg):
    """An orbit angle in 0..350 as the signed angle in -170..180 that the curve sets are written in."""
    a = angle_deg % 360
    return a - 360 if a > 180 else a


def ring_index(angle_deg):
    """Ring of an orbit angle: the polar angle from the forward axis, folded about the equator."""
    polar = abs(signed(angle_deg))
    index = int(round(polar / 10))
    return index if index <= 9 else 18 - index


def ring_weight(angle_deg, double_90=False):
    index = ring_index(angle_deg)
    weight = RING_WEIGHTS[index]
    return weight * 2 if (double_90 and index == 9) else weight


def rms_pressure(curves):
    """Pressure-domain RMS of a set of magnitude curves, as the standard's spatial averages are defined."""
    stack = np.abs(np.asarray(curves, float))
    return np.sqrt(np.mean(stack ** 2, axis=0))


def weighted_rms_pressure(curves, weights):
    stack = np.abs(np.asarray(curves, float))
    w = np.asarray(weights, float)
    return np.sqrt(np.sum(w[:, None] * stack ** 2, axis=0) / np.sum(w))


def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-30))


def nbd(f, spl_db, band_hz=NBD_BAND_HZ, samples_per_band=10):
    """Narrow band deviation: the mean over half-octave bands of the mean absolute deviation inside each.

    It measures wiggle at the scale of a half octave and is blind to a slow trend across the
    spectrum, which is exactly why a monotonic tilt costs almost nothing and a 1 dB wiggle inside
    one half-octave costs directly.
    """
    f = np.asarray(f, float)
    y = np.asarray(spl_db, float)
    deviations = []
    bands = []
    lo = float(band_hz[0])
    step = math.sqrt(2.0)
    while lo * step <= float(band_hz[1]) * (1 + 1e-9):
        hi = lo * step
        if lo >= f.min() and hi <= f.max():
            grid = np.geomspace(lo, hi, samples_per_band)
            sampled = np.interp(np.log(grid), np.log(f), y)
            deviation = float(np.mean(np.abs(sampled - sampled.mean())))
            deviations.append(deviation)
            bands.append(dict(low_hz=lo, high_hz=hi, mean_absolute_deviation_db=deviation))
        lo = hi
    if not deviations:
        return None
    return dict(value=float(np.mean(deviations)), band_hz=list(band_hz), bands=bands, band_count=len(bands),
                samples_per_band=samples_per_band, metric="NBD",
                definition="the mean over half-octave bands of the mean absolute deviation inside each band, as stated "
                           "in the patent. Defined over any of the seven curves, so it is only a quantity when named "
                           "with one.")


def smoothness(f, spl_db, band_hz=SM_BAND_HZ):
    """SM: the r^2 of a straight-line fit of level against log frequency.

    Because the line is allowed to slope, SM polices scatter and not tilt, and a design with a large
    total tilt can score well; it is the weakest and most easily gamed of the four predictors.
    """
    f = np.asarray(f, float)
    y = np.asarray(spl_db, float)
    inside = (f >= band_hz[0]) & (f <= band_hz[1])
    if np.count_nonzero(inside) < 3:
        return None
    x = np.log10(f[inside])
    yy = y[inside]
    slope, intercept = np.polyfit(x, yy, 1)
    residual = yy - (slope * x + intercept)
    total = yy - yy.mean()
    denominator = float(np.sum(total ** 2))
    r2 = 1.0 - float(np.sum(residual ** 2)) / denominator if denominator > 0 else None
    return dict(value=r2, band_hz=list(band_hz), slope_db_per_decade=float(slope), intercept_db=float(intercept),
                residual_rms_db=float(np.sqrt(np.mean(residual ** 2))), metric="SM",
                definition="the r^2 of a straight-line fit of level against log frequency. Because the line may slope, "
                           "SM polices scatter and not tilt, and it is defined over any of the seven curves.")


def lfx(f, sound_power_db, listening_window_db, upper_hz=LFX_UPPER_HZ, reference_band_hz=LW_REFERENCE_BAND_HZ):
    """log10 of the lowest frequency below 300 Hz where the sound power is 6 dB under the listening-window mean.

    Defined on the sound power curve, not on the axial one, so an on-axis f3 is not LFX and is
    usually the more flattering of the two. It carries no penalty for Q, group delay or distortion,
    so it rewards a boomy high-Q alignment exactly as much as a clean one.
    """
    f = np.asarray(f, float)
    sp = np.asarray(sound_power_db, float)
    lw = np.asarray(listening_window_db, float)
    inside = (f >= reference_band_hz[0]) & (f <= reference_band_hz[1])
    if not np.any(inside):
        return None
    reference = float(np.mean(lw[inside]))
    threshold = reference - 6.0
    below = np.flatnonzero((f < upper_hz) & (sp < threshold))
    if not len(below):
        return dict(value=math.log10(upper_hz), frequency_hz=upper_hz, bound="defaulted_to_300_hz",
                    listening_window_reference_db=reference, threshold_db=threshold)
    j = int(below[-1])
    if j + 1 >= len(f):
        crossing = float(f[j])
    else:
        crossing = float(np.exp(np.interp(threshold, sp[j:j + 2], np.log(f[j:j + 2]))))
    return dict(value=math.log10(crossing), frequency_hz=crossing, bound="resolved",
                listening_window_reference_db=reference, threshold_db=threshold,
                octave_worth_preference_points=4.31 * math.log10(2))


def lfq(f, listening_window_db, lfx_frequency_hz, upper_hz=LFX_UPPER_HZ):
    """LFQ: the mean absolute deviation of the listening-window curve between LFX and 300 Hz.

    The patent computes it and the generalized regression gives it zero weight. It is here so that a
    published score that used it can be recognised for what it is.
    """
    f = np.asarray(f, float)
    lw = np.asarray(listening_window_db, float)
    inside = (f >= float(lfx_frequency_hz)) & (f <= float(upper_hz))
    if not np.any(inside):
        return None
    band = lw[inside]
    return dict(value=float(np.mean(np.abs(band - band.mean()))), metric="LFQ",
                band_hz=[float(lfx_frequency_hz), float(upper_hz)], defined_on="listening_window",
                weight_in_generalized_model=0.0,
                note="computed in the patent, zero weight in the published generalized regression.")


def aad(f, spl_db, band_hz=AAD_BAND_HZ, reference_band_hz=AAD_REFERENCE_BAND_HZ, bands_per_octave=20):
    """AAD: mean absolute deviation from the 200 to 400 Hz mean level, over 1/20-octave bands.

    It appears in the patent's earlier model form and not in the generalized four-term model. It is
    computed here so that an older published score using AAD is recognisable rather than mistaken for
    NBD, which is a different quantity over different bands.
    """
    f = np.asarray(f, float)
    y = np.asarray(spl_db, float)
    reference_inside = (f >= reference_band_hz[0]) & (f <= reference_band_hz[1])
    if not np.any(reference_inside):
        return None
    reference = float(np.mean(y[reference_inside]))
    step = 2 ** (1 / bands_per_octave)
    deviations = []
    lo = float(band_hz[0])
    while lo * step <= float(band_hz[1]) * (1 + 1e-9):
        hi = lo * step
        if lo >= f.min() and hi <= f.max():
            grid = np.geomspace(lo, hi, 5)
            deviations.append(abs(float(np.mean(np.interp(np.log(grid), np.log(f), y))) - reference))
        lo = hi
    if not deviations:
        return None
    return dict(value=float(np.mean(deviations)), metric="AAD", band_hz=list(band_hz),
                reference_band_hz=list(reference_band_hz), bands_per_octave=bands_per_octave,
                band_count=len(deviations), weight_in_generalized_model=0.0,
                note="the patent's earlier model form calls this ADDON. It is not a term of the generalized four-term "
                     "model and must not be reported as NBD.")


def preference_score(nbd_on, nbd_pir, lfx_value, sm_pir):
    """Preference = 12.69 - 2.49 NBD_ON - 2.99 NBD_PIR - 4.31 LFX + 2.32 SM_PIR."""
    c = PREFERENCE_COEFFICIENTS
    terms = dict(constant=c["constant"], nbd_on=c["nbd_on"] * nbd_on, nbd_pir=c["nbd_pir"] * nbd_pir,
                 lfx=c["lfx"] * lfx_value, sm_pir=c["sm_pir"] * sm_pir)
    return dict(score=float(sum(terms.values())), terms=terms, coefficients=c,
                contributions_percent=dict(TERM_CONTRIBUTIONS_PERCENT),
                inputs=dict(nbd_on=float(nbd_on), nbd_pir=float(nbd_pir), lfx=float(lfx_value), sm_pir=float(sm_pir)),
                equation="Preference = 12.69 - 2.49 NBD_ON - 2.99 NBD_PIR - 4.31 LFX + 2.32 SM_PIR, read at first hand "
                         "in Harman's patent US 8,311,232 B2",
                contributions_note="the patent states the relative contributions as NBD_ON 31.5 %, LFX 30.5 %, "
                                   "NBD_PIR 20.5 % and SM_PIR 17.5 %, so a reader can see which term moved a score. "
                                   "One octave of extension is worth 4.31 log10(2) = 1.30 points.")


def curve_metrics(f, spl_db, conformance, nbd_band=NBD_BAND_HZ, sm_band=SM_BAND_HZ, curve=None):
    """NBD and SM of one curve, each named with that curve, plus the label saying what the curve is.

    NBD, SM and AAD are each defined over any of ON, LW, ER, PIR, SP, ERDI and SPDI, so a bare NBD
    names nothing. Every metric here carries its own name and the code of the curve it came from.
    """
    code, known = curve_code(curve)
    out = dict(standard_conformance=conformance, curve=curve, curve_code=code,
               curve_is_a_cta_curve=known,
               nbd=nbd(f, spl_db, nbd_band), smoothness=smoothness(f, spl_db, sm_band),
               aad=aad(f, spl_db))
    for key, metric in (("nbd", "NBD"), ("smoothness", "SM"), ("aad", "AAD")):
        if out[key]:
            out[key]["name"] = f"{metric}_{code}"
    out["names"] = [out[key]["name"] for key in ("nbd", "smoothness", "aad") if out[key]]
    if not known:
        out["curve_note"] = ("this curve is not one of the seven the predictors are defined over, so its metrics are "
                             "named after the curve supplied and are not comparable with a published NBD or SM.")
    return out


def assemble(f, pressure_by_angle, rear_wall="standard", double_90_degree_weight=False):
    """The CTA-2034-A curve family from a complete 70-point orbit of complex or magnitude pressures.

    pressure_by_angle maps ("H"|"V", signed degrees) to a pressure magnitude array on f.
    Raises InputError naming every missing point rather than silently averaging a partial orbit.
    """
    if rear_wall not in REAR_WALL:
        raise InputError(f"options.rear_wall must be one of {sorted(REAR_WALL)}")
    required = [(plane, signed(a)) for plane, a in spin_angles()]
    missing = [p for p in required if p not in pressure_by_angle]
    if missing:
        raise InputError(f"the orbit is incomplete: {len(missing)} of {len(required)} points are missing, "
                         f"starting with {missing[:6]}")
    groups = dict(EARLY_REFLECTION_GROUPS, rear_wall=REAR_WALL[rear_wall])
    window = rms_pressure([pressure_by_angle[p] for p in LISTENING_WINDOW])
    group_curves = {name: rms_pressure([pressure_by_angle[p] for p in points]) for name, points in groups.items()}
    early = rms_pressure(list(group_curves.values()))
    weights = [ring_weight(a, double_90_degree_weight) for _, a in required]
    power = weighted_rms_pressure([pressure_by_angle[p] for p in required], weights)
    pir = np.sqrt(PIR_WEIGHTS["listening_window"] * window ** 2 + PIR_WEIGHTS["early_reflections"] * early ** 2 +
                  PIR_WEIGHTS["sound_power"] * power ** 2)
    return dict(on_axis=np.abs(pressure_by_angle[("H", 0)]), listening_window=window, early_reflections=early,
                early_reflection_groups=group_curves, sound_power=power, predicted_in_room=pir,
                sound_power_di_db=db(window) - db(power), early_reflections_di_db=db(window) - db(early),
                point_count=len(required), ring_weights_used=weights)
