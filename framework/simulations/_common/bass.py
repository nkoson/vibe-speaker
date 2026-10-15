"""Bass alignment, efficiency, displacement and vent arithmetic shared by lf_box and the validation harness.

Small's lossy vented recipe, his efficiency and displacement-limited power ratings, and the vent
physics that a vented alignment is only half of. Everything here is closed-form arithmetic over
Thiele/Small parameters; nothing decides whether a number is acceptable.
"""
import math

import numpy as np

from .cli import InputError, C, RHO, MU

# Fourth-order vented prototypes: a1, a2, a3 of s^4 + a1 s^3 + a2 s^2 + a3 s + 1, normalised to f0.
PROTOTYPES = {
    "B4": (2.6131, 3.4142, 2.6131),
    "BL4": (3.20108, 4.39155, 3.12394),
}

# Small's measured loss ranges, as priors on the split 1/QB = 1/QL + 1/QA + 1/QP.
LOSS_PRIORS = {
    "leakage_ql": {"range": [5.0, 20.0], "note": "leakage losses, dominant; 1973 measurements of commercial cabinets"},
    "absorption_qa": {"range": [30.0, 100.0], "note": "100 or more unlined, 30 to 80 with typical wall lining, lower with heavy lining"},
    "vent_qp": {"range": [20.0, 100.0], "note": "50 to 100 unobstructed, need not fall below 20 when obstructed by cloth or lining"},
}

# Small's programme constant for the vented displacement-limited rating, with the span his own
# figures cover across the C4/B4/QB3 families and between passband-limited and wideband drive.
KP_DEFAULT = 3.0
KP_RANGE = (0.3, 5.0)

# Reference efficiency to half-space sensitivity: 112.02 + 10 log10(eta0) dB at 1 W, 1 m.
SENSITIVITY_OFFSET_DB = 112.02

# The four Xmax definitions in circulation. Only the last two measure the same thing, so a figure
# without its definition is not a quantity: it is one of three incomparable quantities.
XMAX_DEFINITIONS = {
    "geometric": dict(
        standard="geometric, no standard",
        comparable_group="construction_dimension",
        definition="a construction dimension - half the difference between coil height and gap height, or the "
                   "manufacturer's own linear-travel figure. No distortion criterion stands behind it.",
        caution="measured 10-percent-distortion excursion differs from the geometric figure by roughly a factor of two "
                "in both directions, so this is not a conservative substitute for a measured limit."),
    "aes2_1984": dict(
        standard="AES2-1984",
        comparable_group="aes2_1984",
        definition="the peak displacement at which motor linearity deviates by 10 %, measured in free air at fs by "
                   "current distortion or by deviation of displacement against current, with the method stated by the "
                   "manufacturer.",
        caution="Klippel's four objections: no clear definition, multiple or infinite values, suspension nonlinearity "
                "only, and failure at assessing motor linearity. One simulated driver yields 0.6 mm, no answer at all, "
                "or three simultaneous answers at 1.5, 8 and 13.5 mm depending on which criterion is applied."),
    "iec_62458": dict(
        standard="IEC 62458 performance-based",
        comparable_group="two_tone_10_percent",
        definition="the peak displacement at which either the total harmonic distortion or the n-th order modulation "
                   "distortion (n = 2 or 3) first exceeds 10 % in the radiated pressure, in free air, under two tones "
                   "at f1 = fs and f2 = 8.5 fs with amplitude ratio 4:1.",
        caution="8.5 fs is also where IEC 62458 defines the inductive limit xL, so the procedure and the parameter-based "
                "limits are probing the same upper-frequency mechanism from the acoustic and the electrical side."),
    "aes2_2012": dict(
        standard="AES2-2012 clause 5.5",
        comparable_group="two_tone_10_percent",
        definition="maximum useful displacement: the peak displacement at which NEITHER the total harmonic distortion "
                   "NOR the second- or third-order modulation distortion exceeds 10 %, two tones at f1 = fs and "
                   "f2 = 8.5 fs in a 4:1 amplitude ratio, microphone in the near field, displacement read with a laser "
                   "displacement sensor.",
        caution="AES2-2012 notes that its definition differs from IEC 60268-5 but expects no difficulty, since the "
                "limiting distortion figure is only 10 %. It is the definition a professional drive-unit datasheet "
                "will have been measured against."),
    "not_stated": dict(
        standard="not stated",
        comparable_group="unknown",
        definition="the part record does not say which definition this figure came from.",
        caution="not comparable with any other driver's Xmax and not usable as an excursion ceiling without an "
                "assumption. Record the definition in the part record rather than leaving the field blank."),
}

# Isobaric loading, derived in alternative-loadings.md section 2 from the Thiele/Small definitions:
# both suspensions resist the same displacement so stiffnesses add, and both masses move together.
ISOBARIC_EXCHANGE = {
    "box_volume_for_a_given_alignment": "halved",
    "fs_qts_alignment_family_f3_over_fs": "unchanged",
    "reference_efficiency": "halved, -3 dB",
    "thermal_power_handling": "doubled",
    "displacement_limited_output_vd": "unchanged",
    "drivers_cost_mass": "doubled",
    "conclusion": "efficiency falls 3 dB and power handling doubles, so the maximum output is the same as one driver. "
                  "Isobaric loading buys box volume with money and amplifier power and with nothing else.",
    "not_carried": "the lower-distortion claim is plausible - two motors' asymmetries partially cancel face to face - "
                   "but no measurement supporting it was obtained, so it is not a benefit a candidate may claim.",
}


def prototype(target, a2=None):
    """The a1, a2, a3 of a named fourth-order prototype. QB3 takes its free a2 from the caller."""
    name = str(target).upper()
    if name in PROTOTYPES:
        return PROTOTYPES[name]
    if name == "QB3":
        if a2 is None:
            raise InputError("the QB3 family needs alignment.a2; it is the free coefficient of the family")
        a2 = float(a2)
        if a2 <= 2 + math.sqrt(2):
            raise InputError(f"QB3 needs a2 > 2 + sqrt(2) = {2 + math.sqrt(2):.4f}, got {a2:g}")
        a1 = math.sqrt(2 * a2)
        return a1, a2, (a2 * a2 + 2) / (2 * a1)
    raise InputError(f"unknown alignment target '{target}'; known targets are B4, BL4 and QB3")


def f3_over_f0(a1, a2, a3):
    """Half-power frequency of s^4/(s^4 + a1 s^3 + a2 s^2 + a3 s + 1), in units of f0.

    |G|^2 = x^8 / ((x^4 - a2 x^2 + 1)^2 + (a3 x - a1 x^3)^2); solved by bisection on the
    monotone-in-the-passband crossing of |G|^2 = 1/2.
    """
    def excess(x):
        real = x ** 4 - a2 * x * x + 1
        imag = a3 * x - a1 * x ** 3
        return x ** 8 - .5 * (real * real + imag * imag)

    lo, hi = 1e-4, 1.0
    while excess(hi) < 0 and hi < 1e4:
        hi *= 1.2
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if excess(mid) < 0:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def second_order_peaking(qt):
    """Passband peak of s^2 T^2 / (s^2 T^2 + s T / Qt + 1), which depends on Qt alone.

    Exactly Qt / sqrt(1 - 1/(4 Qt^2)) where that is real; below Qt = 0.5 the response has no peak.
    """
    qt = float(qt)
    if qt <= 0.5:
        return dict(qt=qt, peak_db=0.0, peaks=False)
    return dict(qt=qt, peak_db=20 * math.log10(qt / math.sqrt(1 - 1 / (4 * qt * qt))), peaks=True)


def second_order_f3_ratio(qt):
    """f3 / fc of the same second-order high-pass: the positive root of x^4 - (2 - 1/Qt^2) x^2 - 1 = 0.

    |G|^2 = x^4 / ((1 - x^2)^2 + (x/Qt)^2) with x = f/fc; setting it to 1/2 gives the biquadratic above.
    """
    qt = float(qt)
    b = 2 - 1 / (qt * qt)
    return math.sqrt((-b + math.sqrt(b * b + 4)) / 2)


def sealed_alignment(qtc):
    """The shape figures a sealed alignment's total Q fixes, with the trade they describe."""
    peaking = second_order_peaking(qtc)
    return dict(peaking, f3_over_fc=second_order_f3_ratio(qtc),
                note="every increase in peaking buys bandwidth: Qtc = 2 reaches a third of an octave lower than Butterworth "
                     "and pays 6.3 dB of hump for it. Qtc = 0.5 is critical damping, 0.707 is maximally flat.")


def solve_alignment(target, ql, a2=None):
    """Small's lossy alignment recipe: solve r^4 - c1 r^3 + c2 r - 1 = 0 and report what follows.

    The quartic has several positive real roots — at QL = 7 the B4 roots are 0.0548, 1.0000 and
    18.237 — and only the one near unity is physical. The selection is by smallest |ln r|, and the
    rejected roots are reported so the choice is visible rather than lucky.
    """
    ql = float(ql)
    if ql <= 0:
        raise InputError("alignment.ql must be positive")
    a1, a2v, a3 = prototype(target, a2)
    c1, c2 = a1 * ql, a3 * ql
    roots = np.roots([1.0, -c1, 0.0, c2, -1.0])
    real = sorted(float(z.real) for z in roots if abs(z.imag) < 1e-8 * max(1.0, abs(z.real)) and z.real > 0)
    if not real:
        raise InputError(f"the lossy quartic for {target} at QL = {ql:g} has no positive real root")
    r = min(real, key=lambda x: abs(math.log(x)))
    h = r * r
    denominator = a3 * math.sqrt(h) * ql - 1
    if denominator <= 0:
        raise InputError(f"{target} at QL = {ql:g} gives a non-physical required QT; the losses are too heavy for this alignment")
    alpha = a2v * h - h * h - 1 - (a3 * math.sqrt(h) * ql - 1) / (ql * ql)
    if alpha <= 0:
        raise InputError(f"{target} at QL = {ql:g} gives a compliance ratio of {alpha:.4f}; no positive box volume solves it")
    ratio = f3_over_f0(a1, a2v, a3)
    return dict(target=str(target).upper(), ql=ql, prototype=dict(a1=a1, a2=a2v, a3=a3, f3_over_f0=ratio),
                quartic=dict(c1=c1, c2=c2, positive_real_roots=real, selected_root=r,
                             selection_rule="the positive real root nearest unity; the others are mathematical, not physical",
                             rejected_roots=[x for x in real if x != r]),
                h_fb_over_fs=h, alpha_vas_over_vb=alpha, f3_over_fs=math.sqrt(h) * ratio,
                required_qt=h * ql / denominator)


def alignment_for_driver(ts, target, ql, a2=None):
    """The solved alignment expressed as the box a given driver needs, beside the QT it actually has."""
    solution = solve_alignment(target, ql, a2)
    fs = float(ts["fs_hz"])
    vas = float(ts["vas_l"])
    qts = 1 / (1 / float(ts["qes"]) + 1 / float(ts["qms"]))
    solution.update(net_volume_l=vas / solution["alpha_vas_over_vb"], tuning_hz=fs * solution["h_fb_over_fs"],
                    f3_hz=fs * solution["f3_over_fs"], driver_qts=qts,
                    qt_excess=qts - solution["required_qt"],
                    qt_note="the alignment is reachable as solved only where the driver's total Q equals the required QT; "
                            "a higher Qts asks for a different member of the family, added series resistance or another driver")
    return solution


def loss_split(qb):
    """The measured ranges behind a chosen QB, and the total the priors bracket.

    Small lumps vent, absorption and leakage into one frequency-invariant leakage resistance whose
    QL equals the total measured QB; this reports what the three priors allow so a QB choice is
    visible rather than implicit.
    """
    # The lossiest corner of the priors is the lowest QB, and the least lossy corner the highest.
    lowest = 1 / sum(1 / v["range"][0] for v in LOSS_PRIORS.values())
    highest = 1 / sum(1 / v["range"][1] for v in LOSS_PRIORS.values())
    return dict(qb_used=float(qb), priors=LOSS_PRIORS, qb_from_priors_min=float(lowest), qb_from_priors_max=float(highest),
                qb_inside_priors=bool(lowest <= qb <= highest),
                note="1/QB = 1/QL + 1/QA + 1/QP. QL = 7 is Small's own mid-range chart value, from 1973 measurements "
                     "of then-current commercial cabinets, not a physical constant.")


def reference_efficiency(ts):
    """Small's half-space reference efficiency eta_0 = 9.6e-10 fs^3 Vas / Qes, with Vas in litres."""
    fs, vas, qes = float(ts["fs_hz"]), float(ts["vas_l"]), float(ts["qes"])
    eta = 9.6e-10 * fs ** 3 * vas / qes
    return dict(eta_0=eta, eta_0_percent=100 * eta, sensitivity_1w_1m_half_space_db=SENSITIVITY_OFFSET_DB + 10 * math.log10(eta),
                constant="9.6e-10 for Vas in litres, which carries an implicit c = 345 m/s; renderings at 343 and 346 differ by about 2 percent",
                note="half space (Small). Thiele's full-space value is half of it. The 2.83 V sensitivity equals the 1 W figure "
                     "only at 8 ohms; scale by 10 log10(8 / Re) otherwise.")


def efficiency_ceiling(f3_hz, net_volume_l, eta_0=None):
    """The lossless vented efficiency-bandwidth-volume limit eta_0(max) = 3.9e-6 f3^3 VB, VB in m^3."""
    if not f3_hz or not net_volume_l:
        return None
    ceiling = 3.9e-6 * float(f3_hz) ** 3 * float(net_volume_l) / 1000
    out = dict(f3_hz=float(f3_hz), net_volume_l=float(net_volume_l), eta_0_max=ceiling, eta_0_max_percent=100 * ceiling,
               sensitivity_ceiling_1w_1m_db=SENSITIVITY_OFFSET_DB + 10 * math.log10(ceiling),
               occurs_near_alpha=0.6,
               note="typical real systems land 2 to 3 dB (40 to 50 percent) below the limit because of driver mechanical "
                    "losses, finite QL and non-optimal alignments")
    if eta_0:
        out["margin_below_ceiling_db"] = 10 * math.log10(ceiling / eta_0)
    return out


def xmax_definition(name):
    """The record of one Xmax definition, or the not_stated record when a part record left it blank."""
    key = str(name or "not_stated").lower()
    if key not in XMAX_DEFINITIONS:
        raise InputError(f"unknown Xmax definition '{name}'; the field takes one of {sorted(XMAX_DEFINITIONS)}")
    return dict(XMAX_DEFINITIONS[key], name=key)


def binding_displacement_limit(ts):
    """The smallest displacement limit on record, with the definition the figure came from.

    Klippel's published example has xL = 2.28 mm against xC = 4.28 mm and xD = 15.9 mm: inductance
    binds, and a design sized against a geometric Xmax or a suspension figure would be distorting at
    half its allowed excursion. Which limit binds is only half the answer: the definitions are not
    interchangeable, so the binding figure is reported with its definition and with the comparability
    group it belongs to.
    """
    # each limit with the definition it comes from and the KIND of measurement it is: the IEC 62458
    # limits are extracted from measured nonlinear parameters, the AES2 figure from radiated
    # distortion, and the smallest of a set containing both is a comparison across two kinds
    labels = {
        "xbl_mm": ("xBl, Bl(x) at 82 % of rest", "iec_62458", "parameter_based"),
        "xc_mm": ("xC, Cms(x) at 75 % of rest", "iec_62458", "parameter_based"),
        "xl_mm": ("xL, voice-coil impedance measured with the cone clamped deviating 10 % at 8.5 fs", "iec_62458",
                  "parameter_based"),
        "xd_mm": ("xD, Doppler d2 at 10 %", "iec_62458", "parameter_based"),
        "x_aes2_2012_mm": ("maximum useful displacement: the two-tone 10 % distortion figure a professional "
                           "drive-unit datasheet is measured against", "aes2_2012", "performance_based"),
    }
    limits = {k: float(v) for k, v in (ts.get("displacement_limits") or {}).items() if k in labels and v}
    # the field is validated wherever it appears, so a free-text entry is an error at the parts
    # record rather than a figure that quietly means nothing
    published = dict(xmax_mm=float(ts["xmax_mm"]), definition=xmax_definition(ts.get("xmax_standard"))) \
        if ts.get("xmax_mm") else None
    if limits:
        key = min(limits, key=limits.get)
        mechanism, definition, kind = labels[key]
        groups = sorted({XMAX_DEFINITIONS[labels[k][1]]["comparable_group"] for k in limits})
        kinds = sorted({labels[k][2] for k in limits})
        return dict(xmax_mm=limits[key], binding_limit=key, binding_mechanism=mechanism, limits_mm=limits,
                    published_xmax=published, measurement_kind=kind,
                    standard="IEC 62458 parameter-based limits" if definition == "iec_62458" else "AES2-2012 clause 5.5",
                    definition=xmax_definition(definition), definition_groups_present=groups,
                    definition_kinds_present=kinds,
                    definitions_mixed=len(groups) > 1 or len(kinds) > 1,
                    note="the binding mechanism is whichever limit is smallest; a geometric XLIN = L - H is not one of them. "
                         "The IEC 62458 limits are parameter-based and the AES2-2012 figure is performance-based, so a set "
                         "containing both is a comparison across two kinds of measurement and says so in definitions_mixed.")
    if ts.get("xmax_mm"):
        definition = xmax_definition(ts.get("xmax_standard"))
        return dict(xmax_mm=float(ts["xmax_mm"]), binding_limit="published_xmax", binding_mechanism=None, limits_mm={},
                    standard=definition["standard"], definition=definition,
                    definition_groups_present=[definition["comparable_group"]],
                    definition_kinds_present=["published"], definitions_mixed=False,
                    note="a single published Xmax. Four definitions are in circulation - geometric, AES2-1984, the IEC 62458 "
                         "performance-based procedure and AES2-2012 clause 5.5 - and only the last two measure the same thing, "
                         "so a figure whose definition is not_stated cannot be compared with another driver's. Measured "
                         "10-percent-distortion excursion has been found to differ from the manufacturer's geometric figure "
                         "by roughly a factor of two in both directions.")
    return None


def displacement_limited_output(sd_cm2, xmax_mm, f3_hz, eta_0=None, kp=KP_DEFAULT):
    """Small's vented displacement-limited rating P_AR = kP f3^4 VD^2, with the SPL and P_ER it implies."""
    if not f3_hz or not xmax_mm:
        return None
    vd = float(sd_cm2) * 1e-4 * float(xmax_mm) * 1e-3
    def rating(k):
        p = k * float(f3_hz) ** 4 * vd * vd
        return dict(kp=float(k), p_ar_w_acoustic=p, spl_db_at_1m_half_space=SENSITIVITY_OFFSET_DB + 10 * math.log10(p),
                    p_er_w_electrical=(p / eta_0) if eta_0 else None)
    out = dict(vd_m3=vd, vd_l=vd * 1000, xmax_mm=float(xmax_mm), f3_hz=float(f3_hz), **rating(kp))
    out["kp_range_used_by_small"] = list(KP_RANGE)
    out["range_over_kp"] = [rating(KP_RANGE[0]), rating(KP_RANGE[1])]
    out["caveats"] = [
        "kP = 3.0 is Small's recommendation for normal programme material regardless of alignment; his own figures span "
        "roughly 0.3 to 5 across the C4/B4/QB3 families and between passband-limited and wideband drive, which is the "
        "12 dB spread reported in range_over_kp.",
        "The rating assumes programme that does not drive the system hard below cutoff, and it is vulnerable to subsonic content.",
        "The reduced kP form is derived for the vented box; applied to a sealed alignment it is an analogy, not Small's rating.",
        "A linear model cannot see force-factor modulation, reported at up to 50 percent in compact long-stroke drivers, "
        "or an Sd that varies with excursion (one published example swings 105 to 55 cm2, a 6 dB sensitivity change). "
        "Both make a simulated maximum SPL an optimistic ceiling rather than an estimate.",
    ]
    return out


def reynolds(velocity_ms, diameter_m):
    """Re = rho v D / mu at the stated air speed and duct diameter."""
    return RHO * float(velocity_ms) * float(diameter_m) / MU


def velocity_at_reynolds(re, diameter_m):
    return float(re) * MU / (RHO * float(diameter_m))


def vent_physics(vent, fb_hz, net_volume_l, peak_velocity_ms=None, vd_m3=None, port=None,
                 legacy_limit_ms=10.0, degradation_re=50000.0):
    """Reynolds number, Small's minimum vent area, flare correction and the edge-radius requirement.

    The legacy 10 m/s rule and the Re = 50,000 degradation threshold coincide only near a 100 mm
    port: in a 50 mm port 10 m/s is only Re ~ 33,000 while Re = 50,000 needs about 15 m/s. Both are
    reported, and so is which of the two binds for the port in hand.
    """
    port = port or {}
    d = float(vent["diameter_mm"]) / 1000
    out = dict(diameter_m=d, legacy_velocity_limit_ms=legacy_limit_ms, degradation_reynolds=degradation_re,
               velocity_at_degradation_reynolds_ms=velocity_at_reynolds(degradation_re, d),
               reynolds_at_legacy_limit=reynolds(legacy_limit_ms, d),
               wall_reynolds=100000.0)
    out["binding_threshold"] = "legacy_10_ms" if out["velocity_at_degradation_reynolds_ms"] > legacy_limit_ms else "reynolds_50000"
    out["threshold_note"] = ("compression correlates with Reynolds number rather than with any single geometry; three "
                             "deliberately different subwoofers degraded near Re = 50,000 and reached a wall by about "
                             "100,000. The 10 m/s rule is corroborated by hot-wire measurement of the jet-formation "
                             "transition, but it is diameter-blind.")
    if peak_velocity_ms is not None:
        out["peak_velocity_ms"] = float(peak_velocity_ms)
        out["reynolds_at_peak"] = reynolds(peak_velocity_ms, d)
        out["reynolds_fraction_of_degradation"] = out["reynolds_at_peak"] / degradation_re
    if vd_m3:
        required_area = 0.8 * float(fb_hz) * float(vd_m3)
        out["small_minimum_vent"] = dict(
            required_area_m2=required_area, actual_area_m2=float(vent["area_m2"]),
            required_single_diameter_m=math.sqrt(float(fb_hz) * float(vd_m3)),
            area_margin_ratio=float(vent["area_m2"]) / required_area if required_area > 0 else None,
            derivation="SV >= 0.8 fB VD, from limiting peak vent velocity at maximum rated programme power to 4.5 percent of c",
            note="Small states it should be regarded as a general guide only, not as a rigid rule, and the underlying "
                 "5-percent-of-c experimental limit assumes a smooth vent with reasonably rounded edges")
    flare_radius = port.get("flare_radius_mm")
    if flare_radius:
        throat_d = float(port.get("throat_diameter_mm", vent["diameter_mm"])) / 1000
        length = float(port.get("length_mm", vent["physical_length_mm"])) / 1000
        amin = int(vent["count"]) * math.pi * (throat_d / 2) ** 2
        nfr = length / (2 * float(flare_radius) / 1000)
        aeff = (1 + 0.576 * nfr) * amin
        leff = length + throat_d
        tuned = C / (2 * math.pi) * math.sqrt(aeff / (leff * float(net_volume_l) / 1000))
        out["flare"] = dict(normalised_flare_rate=nfr, throat_diameter_m=throat_d, throat_area_m2=amin,
                            effective_area_m2=aeff, effective_length_m=leff, tuning_hz=tuned,
                            requested_tuning_hz=float(fb_hz), tuning_ratio=tuned / float(fb_hz),
                            best_single_flare_rate=0.5,
                            note="Aeff = (1 + 0.576 NFR) Amin and Leff = Lact + Dmin, both from the THROAT dimensions; the "
                                 "conventional mouth-radius end correction overestimates the reactive air mass. The fit has "
                                 "r^2 = 0.98 and predicted tuning within 2 percent for the six test ports. NFR near 1.0 gives "
                                 "the lowest distortion at low SPL, near 0.5 at moderate SPL, near 0 at very high SPL.")
    edge_radius = port.get("edge_radius_mm")
    dmin = float(port.get("throat_diameter_mm", vent["diameter_mm"]))
    out["edge_radius"] = dict(required_mm=0.2 * dmin, stated_mm=float(edge_radius) if edge_radius else None,
                              radius_minus_reference_mm=None if edge_radius is None else float(edge_radius)-0.2*dmin,
                              note="every port edge should carry a blend radius of at least 20 percent of the minimum "
                                   "diameter: the entrance-loss coefficient is about 0.05 for r/D >= 0.2 against 0.5 for a "
                                   "square edge. Both ends count, because the signal oscillates and both ends are entrances.")
    return out


def isobaric_pair(ts, wiring="series"):
    """Transform a driver record into its coupled-pair equivalent before any box maths runs.

    Mms doubles and Cms halves, so fs is unchanged and Vas halves; Qts is unchanged for both wirings.
    In series RE and Bl both double, in parallel RE halves and Bl is unchanged, and Qes comes out the
    same either way. Reference efficiency, which goes as fs^3 Vas / Qes, therefore halves: 3 dB.

    The transform is arithmetic from definitions this repository already holds, written out in
    alternative-loadings.md section 2. It is not quoted from a primary source, so the unit test that
    re-derives it is part of the deliverable.
    """
    if wiring not in ("series", "parallel"):
        raise InputError(f"driver.isobaric.wiring must be series or parallel, got '{wiring}'")
    factor = 2.0 if wiring == "series" else 0.5
    pair = dict(ts)
    pair["vas_l"] = float(ts["vas_l"]) / 2
    pair["re_ohm"] = float(ts["re_ohm"]) * factor
    if ts.get("le_mh"):
        pair["le_mh"] = float(ts["le_mh"]) * factor
    if ts.get("mms_g"):
        pair["mms_g"] = float(ts["mms_g"]) * 2
    if ts.get("bl_tm"):
        pair["bl_tm"] = float(ts["bl_tm"]) * (2.0 if wiring == "series" else 1.0)
    report = dict(
        wiring=wiring, drivers=2, exchange=dict(ISOBARIC_EXCHANGE),
        single_driver=dict(fs_hz=float(ts["fs_hz"]), vas_l=float(ts["vas_l"]), re_ohm=float(ts["re_ohm"]),
                           qes=float(ts["qes"]), qms=float(ts["qms"]), sd_cm2=float(ts["sd_cm2"])),
        pair=dict(fs_hz=float(pair["fs_hz"]), vas_l=pair["vas_l"], re_ohm=pair["re_ohm"],
                  qes=float(pair["qes"]), qms=float(pair["qms"]), sd_cm2=float(pair["sd_cm2"])),
        efficiency_change_db=-3.0102999566398116,
        note="the box that follows is sized for the pair's halved Vas. Drive voltage is not comparable between the two "
             "wirings: series doubles the nominal impedance and parallel halves it, so quote power, not volts.")
    single = reference_efficiency(ts)
    both = reference_efficiency(pair)
    report["reference_efficiency"] = dict(single_eta_0=single["eta_0"], pair_eta_0=both["eta_0"],
                                          ratio=both["eta_0"] / single["eta_0"],
                                          sensitivity_change_db=both["sensitivity_1w_1m_half_space_db"] -
                                          single["sensitivity_1w_1m_half_space_db"])
    return pair, report
