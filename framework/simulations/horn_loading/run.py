#!/usr/bin/env python3
"""Horn throat impedance from the Webster one-parameter model, mouth termination and constant-directivity mouth sizing."""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, horn  # noqa: E402

NAME = "horn_loading"
VERSION = "1.1"
NOTES = [
    "Webster one-parameter (plane-wave) throat impedance of an INFINITE horn: exponential, hyperbolic-exponential and conical. A real finite horn softens the cutoff and adds mouth-reflection ripple that this model does not contain.",
    "Below cutoff the throat resistance of the infinite exponential and hypex horn is zero: the horn stops loading the diaphragm. That is an idealisation, but the design consequence - place the cutoff safely below the passband - stands.",
    "The mouth criterion k rm at cutoff has two published optima, 0.93 under a plane-wave assumption and 1.4 under a spherical-wave one, a factor of 1.5 in mouth radius and 2.3 in area. Both are reported; the sources disagree and this application does not choose.",
    "Keele's constant-directivity mouth relation is explicitly an empirical constant, not physics. A second source gives 25106 rather than 25400, a 1.2 percent difference that does not matter.",
    "Keele's Thiele/Small horn design equations - throat area, rear cavity volume, bandwidth, the HF corners and maximum acoustic output - are now in hand and are implemented in horn_design. Nothing HERE sizes a bass horn from a driver; run that application for the design arithmetic and this one for the impedance of a contour already chosen.",
    "THE FLARE CONTOUR BARELY MOVES THE IMPEDANCE. Geddes, at first hand: virtually any shape connecting a given throat and mouth area yields approximately the same impedance, within a dB or so, in the long-wavelength region where the horn equation is valid - and outside that region the equation cannot predict the wavefront at all. Read the difference between the exponential, hypex and conical curves as a distinction of about 1 dB computed with an equation that has stopped being valid where the distinction would matter, and do not choose a contour on it.",
    "No driver, no phase plug, no throat-cavity rolloff, no mouth roundover, no diffraction slot and no higher-order modes. The oblate-spheroidal contour and its cutoff convention are in directivity and horn_design; its throat impedance has no closed form and is computed nowhere here.",
]
VALIDITY = [
    "Plane-wave theory in one dimension: valid while the wavefront can be treated as plane across the cross-section, which fails as the flare angle grows and at high frequency where higher-order modes propagate. Morse's condition, worked by Geddes on a published example, is satisfied only over roughly the first 15 to 20 cm of a 40 cm horn.",
    "Impedance survives that violation and pattern does not: acoustic impedance is an average of the wavefront across the guide, so the equation predicts impedance well outside its strict validity, while directivity is a detail of the wavefront and the equation cannot see it at all.",
    "Infinite-horn throat impedance. A finite horn's mouth reflection produces ripple whose depth grows as the mouth shrinks below the k rm criterion, and that ripple is the practical reason the criterion exists.",
    "A pattern from the constant-directivity relation is a mouth-size statement, not a measured polar. Check it against a measured or computed pattern, and see directivity for the beamwidth models the framework does compute.",
]

KEELE_K = horn.KEELE_K  # metre-degree-hertz; empirical, and a second source gives 25106


def _throat_impedance(kind, f, fc, t_parameter, x0_conical):
    """Normalised throat impedance z = Za St / (rho c) of the infinite horn."""
    f = np.asarray(f, float)
    if kind == "conical":
        kx = 2 * np.pi * f / acoustics.C * x0_conical
        return (kx * kx + 1j * kx) / (1 + kx * kx)
    mu = fc / f
    above = mu <= 1.0
    denominator = 1 - (1 - t_parameter ** 2) * mu ** 2
    if np.any(np.abs(denominator) < 1e-9):
        raise cli.InputError(f"the hypex family has a pole at f = fc sqrt(1 - T^2) = {fc * math.sqrt(max(1 - t_parameter ** 2, 0)):.2f} Hz "
                             "for this T; move the grid off it or choose another T")
    z = np.zeros(len(f), complex)
    z[above] = (np.sqrt(1 - mu[above] ** 2) + 1j * t_parameter * mu[above]) / denominator[above]
    below = ~above
    z[below] = 1j * (t_parameter * mu[below] - np.sqrt(mu[below] ** 2 - 1)) / denominator[below]
    return z


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 20.0, 20000.0, 600)
    spec = cli.require(params, "horn")
    kind = spec.get("flare", "exponential")
    if kind not in ("exponential", "hypex", "conical"):
        raise cli.InputError(f"unknown horn.flare '{kind}'; known flares are exponential, hypex and conical")
    throat_area = cli.positive(spec.get("throat_area_cm2"), "horn.throat_area_cm2") * 1e-4
    mouth_area = cli.positive(spec.get("mouth_area_cm2"), "horn.mouth_area_cm2") * 1e-4
    length = cli.positive(spec.get("length_mm"), "horn.length_mm") / 1000
    t_parameter = float(spec.get("t", 1.0 if kind != "conical" else 0.0))
    if kind == "exponential":
        t_parameter = 1.0

    geometry = dict(flare=kind, throat_area_m2=throat_area, mouth_area_m2=mouth_area, length_m=length,
                    area_ratio=mouth_area / throat_area, t=t_parameter if kind != "conical" else None)
    x0_conical = None
    if kind == "conical":
        x0_conical = length / (math.sqrt(mouth_area / throat_area) - 1)
        geometry["apex_to_throat_m"] = x0_conical
        fc = None
        geometry["cutoff_note"] = ("a conical horn has no cutoff in the exponential sense; its loading falls away gradually. "
                                   "In the one worked comparison available, an exponential horn reached 80 percent of its "
                                   "asymptotic throat resistance at 270 Hz where the conical horn needed about 1200 Hz.")
    else:
        m_geometry = math.log(mouth_area / throat_area) / length
        fc_geometry = m_geometry * acoustics.C / (4 * math.pi)
        fc = float(spec.get("cutoff_hz") or fc_geometry)
        m_used = 4 * math.pi * fc / acoustics.C
        geometry.update(flare_rate_from_geometry_per_m=m_geometry, cutoff_from_geometry_hz=fc_geometry,
                        cutoff_used_hz=fc, flare_rate_used_per_m=m_used,
                        length_for_stated_cutoff_m=math.log(mouth_area / throat_area) / m_used,
                        reference_length_x0_m=acoustics.C / (2 * math.pi * fc))
        if spec.get("cutoff_hz"):
            geometry["cutoff_geometry_ratio"] = fc / fc_geometry

    z = _throat_impedance(kind, f, fc, t_parameter, x0_conical)
    absolute = z * acoustics.RHO * acoustics.C / throat_area
    resistance = np.real(z)
    reached = np.flatnonzero(resistance >= 0.8)
    loading = dict(normalised_throat_impedance=z, throat_impedance_ohm_acoustic=absolute,
                   throat_resistance_normalised=resistance,
                   asymptotic_throat_resistance_ohm_acoustic=acoustics.RHO * acoustics.C / throat_area,
                   eighty_percent_resistance_hz=float(f[reached[0]]) if len(reached) else None,
                   note="normalised by rho c / St, so a value of 1 is full plane-wave loading of the throat")

    mouth = dict(mouth_radius_m=math.sqrt(mouth_area / math.pi), criteria={})
    if fc:
        mouth = horn.mouth_criteria(fc, mouth_area)

    coverage = spec.get("coverage")
    directivity = None
    if coverage:
        planes = {}
        for plane, angle_key, size_key in (("horizontal", "horizontal_deg", "mouth_width_mm"),
                                           ("vertical", "vertical_deg", "mouth_height_mm")):
            angle = cli.positive(coverage.get(angle_key), f"horn.coverage.{angle_key}")
            size = cli.positive(coverage.get(size_key), f"horn.coverage.{size_key}") / 1000
            planes[plane] = dict(coverage_deg=angle, mouth_dimension_m=size,
                                 pattern_control_limit_hz=KEELE_K / (angle * size),
                                 mouth_for_control_to_cutoff_m=(KEELE_K / (angle * fc)) if fc else None,
                                 beamwidth_below_limit_deg_at=dict(
                                     note="theta(f) = K / (d f) below the control limit: the pattern widens as frequency falls",
                                     at_1000_hz=KEELE_K / (size * 1000.0)))
        h, v = planes["horizontal"], planes["vertical"]
        required_ratio = h["coverage_deg"] / v["coverage_deg"]
        actual_ratio = v["mouth_dimension_m"] / h["mouth_dimension_m"]
        flip_from = max(h["pattern_control_limit_hz"], v["pattern_control_limit_hz"])
        flip_to = min(h["pattern_control_limit_hz"], v["pattern_control_limit_hz"])
        directivity = dict(
            constant=KEELE_K, constant_note="1e6 inch-degree-hertz = 2.54e4 metre-degree-hertz, empirical; a second source gives 25106",
            planes=planes,
            planes_let_go_together=dict(
                required_height_over_width=required_ratio, actual_height_over_width=actual_ratio,
                note="to make both planes lose control at the same frequency the narrower-coverage plane's mouth dimension "
                     "must be larger by the ratio of the coverage angles: a 90 x 45 degree horn needs a mouth twice as tall "
                     "as it is wide. Commercial horns are usually the other way round."),
            pattern_flip=dict(
                narrow_plane_controls_above_hz=flip_from, wide_plane_controls_above_hz=flip_to,
                band_hz=[flip_to, flip_from],
                note="between these two frequencies one plane still controls and the other has already let go, so the "
                     "nominal coverage pair does not describe the horn there. In the 1 to 4 kHz region, exactly where a "
                     "two-way monitor or PA box crosses over, the real mismatch against a cone driver is usually larger "
                     "than the datasheet implies."),
            scaling="one octave lower control needs double the mouth dimension, and halving the coverage angle also needs double it")

    results = dict(f_hz=f, geometry=geometry, loading=loading, mouth=mouth)
    if directivity:
        results["constant_directivity"] = directivity
    intensity = spec.get("throat_intensity_w_m2")
    if intensity and fc:
        results["air_nonlinearity"] = dict(
            throat_intensity_w_m2=float(intensity), second_harmonic_percent=1.73e-2 * (f / fc) * float(intensity),
            note="Beranek's simplification for an infinite exponential horn, D2 [%] = 1.73e-2 (f / fc) It. It grows with "
                 "f / fc, so a low-cutoff horn driven hard at high frequency is the worst case; at domestic levels it is "
                 "negligible and at throat pressures of 150 to 170 dB it is real.")
    results["mid_band_narrowing"] = dict(
        factor_of_nominal=[0.4, 0.5],
        note="spherical-segment horns (multicellular and radial) narrow to 40 to 50 percent of their nominal beamwidth where "
             "the wavelength becomes comparable to the segment dimensions. Keele's constant-directivity horns removed it by "
             "doubling the included angle over the last third of the conical section. Both figures are reported at second "
             "hand without tolerances, and neither is modelled above.")
    results["validity"] = dict(statements=list(VALIDITY), cutoff_hz=fc,
                               contour_distinguishes_impedance_by_about_db=1.0,
                               design_arithmetic_lives_in="horn_design")
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Horn throat impedance, mouth termination and constant-directivity sizing", NOTES, VALIDITY))
