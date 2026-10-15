"""Closed-form horn and waveguide design from parameters a datasheet actually carries.

Everything here is arithmetic, and each line settles a decision: whether a driver suits a horn at
all, how big the throat and the rear cavity have to be, the band the driver can work over, where the
top rolls off, how much acoustic output the displacement allows, and how big the mouth has to be for
the pattern. Keele's recasting of the classical equations into Thiele/Small parameters is the source
for the first six; the oblate-spheroidal contour and its cutoff convention are Kolbrek's and Geddes'.

What is deliberately NOT here is a Webster throat-impedance solver over flare contours. Geddes, at
first hand: virtually any shape connecting a given throat and mouth area yields approximately the
same impedance, within a dB or so, in the long-wavelength region where the horn equation is valid -
and outside that region the equation cannot predict the wavefront at all. A solver that distinguishes
exponential from hypex from conical computes a 1 dB distinction with an equation that has stopped
being valid where the distinction would matter.
"""
import math

import numpy as np

from .cli import InputError, RHO, C

KEELE_K = 2.54e4  # metre-degree-hertz for the constant-directivity relation; empirical, not physics

PAR_CONSTANT = 3 * math.pi * RHO * C * C / 2  # about 6.7e5 in SI, the displacement-limited output constant


def keele_design(ts, fc_hz, front_cavity_l=None):
    """Keele's low-frequency horn design set from Thiele/Small parameters. SI throughout, Vas in m^3.

        suitability      fs Qts < fc          else no cavity volume can annul the reactance
        throat area      ST = 2 pi fs Qts Vas / c
        rear cavity      VB = Vas / (fc/(fs Qts) - 1)
        usable band      fHS/fLS = 1/Qts^2    with fHS = fs/Qts and fLS = Qts fs
        HF corners       fHM = 2 fs/Qts, fHVC = RE/(pi LE), fHC = 2 Qts fs (Vas/VFC)
        max output       PAR = 6.7e5 fc^2 VD^2 / (fs Qts Vas)
        efficiency       eta = 2 RE RET/(RE+RET)^2, peaking at 50 % when RET = RE
    """
    fs = float(ts["fs_hz"])
    qts = float(ts.get("qts") or 1 / (1 / float(ts["qes"]) + 1 / float(ts["qms"])))
    vas = float(ts["vas_l"]) / 1000
    sd = float(ts["sd_cm2"]) * 1e-4
    re = float(ts["re_ohm"])
    fc = float(fc_hz)
    if min(fs, qts, vas, sd, re, fc) <= 0:
        raise InputError("a horn design needs positive fs, Qts, Vas, Sd, Re and cutoff frequency")
    fls = qts * fs
    fhs = fs / qts
    suitable = fls < fc
    out = dict(
        cutoff_hz=fc, fs_hz=fs, qts=qts, vas_l=vas * 1000, sd_cm2=sd * 1e4,
        suitability=dict(fs_qts=fls, cutoff_hz=fc, cutoff_minus_fs_qts_hz=fc-fls,
                         margin_ratio=fc / fls,
                         rule="VB is finite and positive only when fLS = fs Qts < fc. A driver with fs Qts >= fc is not "
                              "suited to a horn at that cutoff: no cavity volume will annul the reactance. One line of "
                              "arithmetic; the sign describes this equation's finite-positive-cavity domain."),
        throat=dict(area_m2=2 * math.pi * fs * qts * vas / C,
                    area_cm2=2 * math.pi * fs * qts * vas / C * 1e4,
                    derivation="ST = 2 pi fs Qts Vas / c, the throat that makes the horn's reflected load resistance "
                               "equal RE and so maximises midband efficiency.",
                    caveat="this is the efficiency-optimal throat, NOT automatically the right throat. Keele's own "
                           "conclusion, credited to Small: traditional design fixes the throat to maximise efficiency, "
                           "and since many of the horn's other characteristics depend heavily on throat area, that "
                           "constraint removes one valuable degree of design freedom."),
        band=dict(resistance_controlled_low_hz=fls, resistance_controlled_high_hz=fhs,
                  ratio=fhs / fls, octaves=math.log2(fhs / fls), geometric_mean_hz=math.sqrt(fls * fhs),
                  law="fHS/fLS = 1/Qts^2. The width of the usable band goes as 1/Qts^2, so a low Qts - strong motor, "
                      "large magnet - is what buys bandwidth. Qts = 0.21 spans about 4.5 octaves, Qts = 0.45 under "
                      "five halves of that. This is physics, not preference."),
        hf_corners=dict(moving_mass_fhm_hz=2 * fhs,
                        rolloff="6 dB/octave above fHM, 12 above fHVC, 18 above fHC. The composite rolloff is a "
                                "combination of all three; the corners give the shape, not the curve."),
    )
    if suitable:
        vb = vas / (fc / fls - 1)
        out["rear_cavity"] = dict(
            volume_m3=vb, volume_l=vb * 1000, alpha_vas_over_vb=vas / vb,
            annulling_check_hz=fls * (1 + vas / vb),
            box_dominated_approximation_l=vas * fls / fc * 1000,
            throat_form_l=out["throat"]["area_m2"] * C / (2 * math.pi * fc) * 1000,
            derivation="VB = Vas / (fc/(fs Qts) - 1), from Klipsch reactance annulling: the driver in its closed rear "
                       "cavity has its lower resistance-controlled bound sitting at the horn cutoff, fLS (1 + Vas/VB) = fc.",
            size_warning="this is the equation that sets a bass horn's size, and the number is usually the reason the "
                         "design is abandoned: Keele's 12-inch example needs 32.6 litres of cavity BEHIND the driver, "
                         "plus the horn itself.")
    else:
        out["rear_cavity"] = dict(
            volume_l=None,
            reason=f"fs Qts = {fls:.2f} Hz is not below the {fc:g} Hz cutoff, so the reactance-annulling cavity has a "
                   "negative or infinite volume. This driver does not suit a horn at this cutoff.")
    if ts.get("le_mh"):
        out["hf_corners"]["voice_coil_fhvc_hz"] = re / (math.pi * float(ts["le_mh"]) * 1e-3)
    if front_cavity_l:
        out["hf_corners"]["front_cavity_fhc_hz"] = 2 * qts * fs * (vas * 1000 / float(front_cavity_l))
        out["hf_corners"]["front_cavity_l"] = float(front_cavity_l)
        out["hf_corners"]["front_cavity_note"] = ("the front cavity is the corner the designer controls: fHC is "
                                                  "inversely proportional to VFC, so the volume trapped between the "
                                                  "cone and the throat sets the top of the horn's passband.")
    xmax = ts.get("xmax_mm")
    vd = float(ts["vd_m3"]) if ts.get("vd_m3") else (sd * float(xmax) * 1e-3 if xmax else None)
    if vd:
        par = PAR_CONSTANT * fc * fc * vd * vd / (fs * qts * vas)
        out["max_acoustic_output"] = dict(
            vd_m3=vd, par_w_acoustic=par, constant=PAR_CONSTANT,
            spl_db_at_1m_half_space=112.02 + 10 * math.log10(par),
            down_to_hz=1.26 * fc,
            derivation="PAR = (3 pi rho0 c^2 / 2) fc^2 VD^2 / (fs Qts Vas), the displacement-limited output.",
            assumption="a well-designed finite exponential horn with optimum mouth size, whose low-frequency "
                       "efficiency is down no more than 0.3 dB from midband at 1.26 fc. PAR is the output available "
                       "down to that frequency. Thermal limits are a separate ceiling and are not in this equation.")
    if ts.get("bl_tm"):
        bl = float(ts["bl_tm"])
        ret = out["throat"]["area_m2"] * bl * bl / (RHO * C * sd * sd)
        out["efficiency"] = dict(
            ret_ohm=ret, re_ohm=re, eta=2 * re * ret / (re + ret) ** 2,
            eta_percent=200 * re * ret / (re + ret) ** 2, maximum_eta_percent=50.0,
            ret_over_re=ret / re,
            note="eta = 2 RE RET / (RE + RET)^2 with RET = ST Bl^2 / (rho0 c SD^2). It peaks at 50 % when RET = RE, "
                 "which is what the efficiency-optimal throat area arranges.")
    return out


def mouth_criteria(fc_hz, mouth_area_m2=None):
    """The k rm mouth criterion at cutoff, with both published optima and the note that they disagree."""
    fc = float(fc_hz)
    k_c = 2 * math.pi * fc / C
    out = dict(cutoff_hz=fc, criteria={},
               practice="k rm of 0.7 to 1 for bass horns and at least 1 for midrange and treble horns",
               disagreement="0.93 under a plane-wave assumption against 1.4 under a spherical-wave one: a factor of 1.5 "
                            "in mouth radius and 2.3 in area. The sources disagree and this arithmetic does not choose. "
                            "An undersized mouth reflects energy back down the horn and produces ripple.")
    if mouth_area_m2:
        out["mouth_radius_m"] = math.sqrt(float(mouth_area_m2) / math.pi)
        out["k_rm_at_cutoff"] = k_c * out["mouth_radius_m"]
    for label, target in (("plane_wave_0p93", 0.93), ("spherical_wave_1p4", 1.4)):
        radius = target / k_c
        row = dict(target_k_rm=target, required_radius_m=radius, required_area_m2=math.pi * radius * radius,
                   required_area_cm2=math.pi * radius * radius * 1e4)
        if mouth_area_m2:
            row["area_ratio_actual_over_required"] = float(mouth_area_m2) / (math.pi * radius * radius)
        out["criteria"][label] = row
    return out


def pattern_control_hz(coverage_deg, mouth_dimension_m):
    """Keele's constant-directivity relation: the frequency above which a mouth dimension holds its pattern."""
    coverage_deg = float(coverage_deg)
    mouth_dimension_m = float(mouth_dimension_m)
    if coverage_deg <= 0 or mouth_dimension_m <= 0:
        raise InputError("pattern control needs a positive coverage angle and mouth dimension")
    return KEELE_K / (coverage_deg * mouth_dimension_m)


def mouth_for_pattern(coverage_deg, frequency_hz):
    """The mouth dimension per plane that holds a coverage angle down to a frequency: d = K / (theta f)."""
    return KEELE_K / (float(coverage_deg) * float(frequency_hz))


def os_waveguide(throat_radius_mm, half_angle_deg, axial_positions_mm=None):
    """Oblate-spheroidal waveguide: the contour, and the cutoff the 0.2-of-asymptotic convention gives.

        r(x) = sqrt(rt^2 + tan^2(theta0) x^2)          fc = 0.2 c sin(theta0) / (pi rt)

    theta0 is HALF the included coverage angle. The OS waveguide has no sharp cutoff; this definition
    is the frequency at which throat resistance falls to 0.2 of its asymptotic value, so it means
    roughly what exponential-horn cutoff means and nothing more.
    """
    rt = float(throat_radius_mm) / 1000
    theta = float(half_angle_deg)
    if rt <= 0 or not 0 < theta < 90:
        raise InputError("an OS waveguide needs a positive throat radius and a half angle between 0 and 90 degrees")
    theta_rad = math.radians(theta)
    fc = 0.2 * C * math.sin(theta_rad) / (math.pi * rt)
    positions = np.asarray(axial_positions_mm if axial_positions_mm is not None else
                           np.linspace(0, 200, 21), float)
    radius = np.sqrt(rt ** 2 + math.tan(theta_rad) ** 2 * (positions / 1000) ** 2)
    return dict(
        throat_radius_mm=rt * 1000, half_angle_deg=theta, included_angle_deg=2 * theta,
        cutoff_hz=fc,
        contour=dict(x_mm=positions, radius_mm=radius * 1000, diameter_mm=2 * radius * 1000,
                     mouth_radius_mm=float(radius[-1]) * 1000,
                     mouth_area_cm2=float(math.pi * radius[-1] ** 2) * 1e4),
        cutoff_convention="0.2 of asymptotic throat resistance. The OS waveguide has NO sharp cutoff, so this figure "
                          "means roughly what exponential-horn cutoff means and nothing more.",
        low_frequency_note="a low cutoff needs a big throat or a narrow angle, which is exactly why OS waveguides are "
                           "poor at low frequencies: like conical horns they get very long and narrow before they load "
                           "anything in the bass.",
        throat_impedance="NOT COMPUTED, and deliberately so. Throat impedance for this contour has no closed form and "
                         "must be integrated numerically, and shape moves impedance by about a dB in the band where "
                         "the horn equation is valid anyway. See the module docstring.",
        higher_order_modes="above a frequency set by throat radius and horn angle, higher-order modes exist in an OS "
                           "waveguide and the one-parameter assumption fails. Neither source consulted gives that "
                           "frequency as a formula, only that it exists, so none is invented here.",
        optimality="waveguides based on the orthogonal coordinate geometries generate the fewest higher-order modes of "
                   "any contour joining the same throat and mouth apertures. That is the actual argument for the OS "
                   "shape - not loading.")


WEBSTER_LIMITS = [
    "Webster's equation assumes plane-wave propagation. Morse's condition, applied to a published example by Geddes, "
    "is satisfied only over roughly the first 15 to 20 cm of a horn whose total length is 40 cm.",
    "Impedance survives the violation and pattern does not: acoustic impedance is an average of the wavefront across "
    "the guide, so the equation predicts impedance well outside its strict validity, while directivity is a detail of "
    "the wavefront and the equation cannot see it at all.",
    "Geddes, at first hand: virtually any shape connecting a given throat and mouth area will yield approximately the "
    "same impedance, within a dB or so, in the long-wavelength region where the horn equation is valid. A "
    "throat-impedance solver that distinguishes exponential from hypex from conical is computing a distinction of "
    "about 1 dB with an equation that is invalid where the distinction would matter.",
    "Directivity comes from the mouth through Keele's constant-directivity relation, not from the flare.",
]
