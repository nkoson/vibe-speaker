#!/usr/bin/env python3
"""Closed-form horn design from Thiele/Small parameters: suitability, throat, rear cavity, band, corners, output and mouth."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, horn  # noqa: E402

NAME = "horn_design"
VERSION = "1.0"
NOTES = [
    "Keele's recasting of the classical horn equations into Thiele/Small parameters. Every figure is closed form over fs, Qts, Vas, Sd, Re, Le, Bl and the chosen cutoff, and each one settles a decision rather than describing a curve.",
    "No throat impedance is computed, and that is the design decision behind this application. Geddes, at first hand: virtually any shape connecting a given throat and mouth area yields approximately the same impedance within about a dB in the band where Webster's equation is valid, and outside that band the equation cannot predict the wavefront at all. horn_loading still computes the Webster impedance for the record; read its 1 dB spread against this caveat.",
    "The throat area reported is the EFFICIENCY-OPTIMAL one. Keele's own conclusion, credited to Small, is that fixing the throat to maximise efficiency removes one valuable degree of design freedom, so it is a reference point and not the answer.",
    "PAR assumes a well-designed finite horn with an optimum mouth, and is the output available down to 1.26 fc. Thermal limits are a separate ceiling that is not in the equation.",
    "Directivity comes from the mouth through Keele's constant-directivity relation, not from the flare. The relation's constant is empirical, not physics.",
    "The oblate-spheroidal block gives the contour and the 0.2-of-asymptotic-resistance cutoff convention. An OS waveguide has no sharp cutoff, and no source consulted gives the higher-order-mode frequency as a formula, so none is computed.",
]
VALIDITY = [
    "Closed-form design arithmetic, not a wave solution. It says how big the parts have to be and what band the driver can work over; it does not predict a response curve, a polar or a throat impedance.",
    "Webster's plane-wave assumption, which the underlying equations rest on, is satisfied only over roughly the first 15 to 20 cm of a 40 cm horn in the one worked example available. Impedance survives that violation, pattern does not.",
    "A horn model cannot state its own accuracy above the first break-up of the driver, and for a compression driver that is a measured frequency, not a simulated one.",
    "No source consulted states the decibel error between a simulated and a measured horn response, so nothing here carries an error bar from the literature.",
]


def _directivity(coverage, fc):
    """Per plane: the pattern-control limit, the mouth that holds control to cutoff, and the pattern flip."""
    planes = {}
    for plane, angle_key, size_key in (("horizontal", "horizontal_deg", "mouth_width_mm"),
                                       ("vertical", "vertical_deg", "mouth_height_mm")):
        angle = cli.positive(coverage.get(angle_key), f"coverage.{angle_key}")
        size = cli.positive(coverage.get(size_key), f"coverage.{size_key}") / 1000
        planes[plane] = dict(coverage_deg=angle, mouth_dimension_m=size,
                             pattern_control_limit_hz=horn.pattern_control_hz(angle, size),
                             mouth_for_control_to_cutoff_m=horn.mouth_for_pattern(angle, fc) if fc else None)
    h, v = planes["horizontal"], planes["vertical"]
    flip_from = max(h["pattern_control_limit_hz"], v["pattern_control_limit_hz"])
    flip_to = min(h["pattern_control_limit_hz"], v["pattern_control_limit_hz"])
    return dict(
        constant=horn.KEELE_K,
        constant_note="1e6 inch-degree-hertz = 2.54e4 metre-degree-hertz, empirical; a second source gives 25106, a "
                      "1.2 percent difference that does not matter",
        planes=planes,
        planes_let_go_together=dict(
            required_height_over_width=h["coverage_deg"] / v["coverage_deg"],
            actual_height_over_width=v["mouth_dimension_m"] / h["mouth_dimension_m"],
            note="to make both planes lose control at the same frequency the narrower-coverage plane's mouth dimension "
                 "must be larger by the ratio of the coverage angles: a 90 x 45 degree horn needs a mouth twice as tall "
                 "as it is wide. Commercial horns are usually the other way round."),
        pattern_flip=dict(narrow_plane_controls_above_hz=flip_from, wide_plane_controls_above_hz=flip_to,
                          band_hz=[flip_to, flip_from],
                          note="between these two frequencies one plane still controls and the other has already let go, "
                               "so the nominal coverage pair does not describe the horn there."),
        scaling="one octave lower control needs double the mouth dimension, and halving the coverage angle also needs "
                "double it")


def compute(params, base_dir):
    ts = dict(cli.require(params, "driver", "ts"))
    fc = cli.positive(cli.require(params, "cutoff_hz"), "cutoff_hz")
    front_cavity = (params.get("front_cavity_l") or (params.get("cavities") or {}).get("front_l"))
    design = horn.keele_design(ts, fc, front_cavity)
    results = dict(design=design, webster_limits=list(horn.WEBSTER_LIMITS))

    mouth = params.get("mouth") or {}
    area = mouth.get("area_cm2")
    if not area and mouth.get("width_mm") and mouth.get("height_mm"):
        area = float(mouth["width_mm"]) * float(mouth["height_mm"]) / 100
    results["mouth"] = horn.mouth_criteria(fc, float(area) * 1e-4 if area else None)
    results["mouth"]["stated_area_cm2"] = float(area) if area else None
    results["mouth"]["both_optima_reported"] = True

    coverage = params.get("coverage")
    if coverage:
        results["constant_directivity"] = _directivity(coverage, fc)

    waveguide = params.get("os_waveguide")
    if waveguide:
        results["os_waveguide"] = horn.os_waveguide(
            cli.positive(waveguide.get("throat_radius_mm"), "os_waveguide.throat_radius_mm"),
            cli.positive(waveguide.get("half_angle_deg"), "os_waveguide.half_angle_deg"),
            waveguide.get("axial_positions_mm"))

    results["validity"] = dict(statements=list(VALIDITY), cutoff_hz=fc,
                               driver_suitable=design["suitability"]["suitable"],
                               usable_band_hz=[design["band"]["resistance_controlled_low_hz"],
                                               design["band"]["resistance_controlled_high_hz"]],
                               throat_impedance_computed=False,
                               par_valid_down_to_hz=1.26 * fc)
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Closed-form horn design from Thiele/Small parameters", NOTES, VALIDITY))
