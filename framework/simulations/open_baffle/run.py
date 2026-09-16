#!/usr/bin/env python3
"""Open-baffle dipole and first-order gradient loading: response, pattern, excursion demand,
cavity resonance and the cardioid arrangement's two band limits."""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, arrays  # noqa: E402

NAME = "open_baffle"
VERSION = "1.1"
NOTES = [
    "Two models of the same dipole. 'equivalence' is the sourced engineering form: unity above the equivalence frequency f = 0.17 c / D and 6 dB per octave below it. 'point_dipole' is the exact two-monopole result 2 sin(k D cos(theta) / 2), which adds the peak at c / (2 D) and the null at c / D that the equivalence form smooths away.",
    "The pattern is cos(theta) with nulls at plus and minus 90 degrees: about 1 dB down at 30, 3 dB at 45 and 6 dB at 60 degrees. A dipole radiates about 4.8 dB less power than a monopole for the same on-axis SPL.",
    "Excursion rises at 18 dB per octave below the equivalence frequency rather than the monopole's 12, so one octave lower at constant SPL costs eight times the volume displacement. That is the dominant fact in dipole woofer sizing and it is what the excursion table reports.",
    "D is the front-to-back acoustic path, not the baffle width: the route the rear wave takes around the panel. There is no room, no floor, no baffle diffraction and no driver nonlinearity here.",
    "The H-frame or U-frame cavity resonance F = 0.25 c / L caps the usable band; no source consulted states how far below it to cross.",
    "The cardioid block is the first-order gradient pattern D = 1 + cos(theta) and the two band limits that bound it: the lambda/2 spacing criterion above and the gradient's 6 dB/octave falloff below. The pattern equation and the gradient principle are physics and the delay-and-invert realisation is standard practice; the reported 2 to 2.5 octave practical passband comes from a PATENT SPECIFICATION, not a measurement series.",
    "What a passive cardioid cabinet actually is - a resistive rear vent rather than a second driver - has no published alignment mathematics, and that combination is deliberately not modelled. The gradient pair here is two sources of equal strength, delayed and inverted.",
]
VALIDITY = [
    "The dipole equivalence frequency and the 18 dB/octave excursion law come from one self-published modelling source. They are arithmetic that checks out, not measurements.",
    "Point-source geometry: the two faces are treated as a pair of monopoles separated by the acoustic path. A real panel's path length varies with angle and frequency, which is what makes D an estimate rather than a dimension.",
    "Above the first null the model is not useful: a real driver on a real baffle is beaming and diffracting there, and neither is in this model.",
    "A cardioid realisation with a resistive rear vent is outside this model. No source consulted gives how box tuning, vent resistance and delay interact in that arrangement, which is how most passive cardioid cabinets are built.",
]


def _cardioid(spec):
    """The first-order gradient pattern and the two limits that bound its usable band.

        D(theta) = 1 + cos(theta)       normalised rho(theta) = 0.5 + 0.5 cos(theta)

    Unity forward, -6 dB at 90 degrees, a null at 180. Upper limit: rear cancellation needs the two
    arrivals in anti-phase, which fails as the spacing approaches lambda/2 - the same criterion that
    governs any two-source array. Lower limit: a first-order gradient's output falls 6 dB/octave
    relative to a monopole of the same volume velocity, paid in excursion and power.
    """
    spacing = cli.positive(spec.get("spacing_mm"), "cardioid.spacing_mm") / 1000
    angles = np.asarray(spec.get("angles_deg", [0, 30, 45, 60, 90, 120, 135, 150, 180]), float)
    pattern = 1 + np.cos(np.deg2rad(angles))
    upper = arrays.spacing_criterion(spacing, spec.get("upper_hz"))
    lower_hz = spec.get("lower_hz")
    out = dict(
        spacing_mm=spacing * 1000, delay_us=spacing / acoustics.C * 1e6,
        realisation="two sources separated by d along the axis, the rear one inverted in polarity and delayed by d/c, so "
                    "the two rear arrivals are equal and opposite.",
        pattern=dict(angles_deg=angles, directional_function=pattern, normalised=pattern / 2,
                     relative_db=acoustics.db(pattern / 2),
                     note="D = 1 + cos(theta): unity forward, -6 dB at 90 degrees, a null at 180 degrees."),
        upper_limit=dict(upper, mechanism="as d approaches lambda/2 the anti-phase condition ceases to hold and the "
                                          "pattern breaks up. This is the same spacing criterion that governs any "
                                          "two-source array."),
        lower_limit=dict(rolloff_db_per_octave=6.0,
                         mechanism="a first-order gradient source's output falls 6 dB/octave relative to a monopole of "
                                   "the same volume velocity as frequency drops, because the pattern is produced by a "
                                   "path-length difference that shrinks with wavelength. Holding the cardioid down in "
                                   "frequency costs 6 dB of drive per octave, paid in excursion and power."),
        reported_practical_passband_octaves=[2.0, 2.5],
        passband_source="a patent specification, not a measurement series. The two limits that produce it are sound, and "
                        "any cardioid design claiming a wider band should be asked which of them it escaped.",
        not_modelled="the resistive-rear-vent realisation, which is how most passive cardioid cabinets are built. No "
                     "source consulted gives its alignment mathematics, so this block is a gradient PAIR and nothing else.")
    if lower_hz:
        out["lower_limit"]["stated_lower_hz"] = float(lower_hz)
        out["stated_passband_octaves"] = float(np.log2(upper["half_wavelength_limit_hz"] / float(lower_hz)))
        out["stated_passband_inside_reported_range"] = bool(out["stated_passband_octaves"] <= 2.5)
        out["gradient_drive_penalty_db_at_lower_hz"] = float(6.0 * np.log2(
            upper["half_wavelength_limit_hz"] / float(lower_hz)))
    return out


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 10.0, 2000.0, 500)
    baffle = cli.require(params, "baffle")
    path = cli.positive(baffle.get("path_mm"), "baffle.path_mm") / 1000
    model = params.get("model", "equivalence")
    if model not in ("equivalence", "point_dipole"):
        raise cli.InputError(f"unknown model '{model}'; known models are equivalence and point_dipole")
    equivalence_hz = 0.17 * acoustics.C / path
    k = 2 * np.pi * f / acoustics.C
    exact = 2 * np.sin(k * path / 2)
    simple = (f / equivalence_hz) / np.sqrt(1 + (f / equivalence_hz) ** 2)
    response = simple if model == "equivalence" else np.abs(exact) / 2 * np.sqrt(2)
    geometry = dict(acoustic_path_m=path, equivalence_frequency_hz=equivalence_hz,
                    first_peak_hz=acoustics.C / (2 * path), first_null_hz=acoustics.C / path,
                    note="the equivalence frequency, the peak and the null are three descriptions of the same geometry. "
                         "Below the equivalence frequency output falls at 6 dB per octave whatever the model.")

    angles = np.asarray(params.get("angles_deg", [0, 15, 30, 45, 60, 75, 90]), float)
    pattern = dict(angles_deg=angles, relative_db=acoustics.db(np.cos(np.deg2rad(angles))),
                   power_relative_to_monopole_db=-4.8,
                   note="cos(theta) with nulls at plus and minus 90 degrees. The 4.8 dB is the power a dipole radiates "
                        "below a monopole at the same on-axis SPL, which is the efficiency the pattern buys.")

    results = dict(f_hz=f, model=model, geometry=geometry,
                   relative_response=response, relative_response_db=acoustics.db(response),
                   equivalence_response_db=acoustics.db(simple), point_dipole_response_db=acoustics.db(np.abs(exact) / 2 * np.sqrt(2)),
                   rolloff_db_per_octave_below_equivalence=-6.0, pattern=pattern)

    cavity = params.get("cavity")
    if cavity and cavity.get("depth_mm"):
        depth = float(cavity["depth_mm"]) / 1000
        results["cavity_resonance"] = dict(
            depth_m=depth, resonance_hz=0.25 * acoustics.C / depth,
            note="F = 0.25 c / L for an H-frame or U-frame of cavity depth L. It caps the usable band; no source consulted "
                 "states how far below it to cross, so that margin is a judgement to state.")

    driver = params.get("driver")
    target = params.get("target") or {}
    if driver and target.get("spl_db_at_1m"):
        sd = cli.positive(driver.get("sd_cm2"), "driver.sd_cm2") * 1e-4
        pressure = acoustics.P0 * 10 ** (float(target["spl_db_at_1m"]) / 20)
        space = target.get("space", "full")
        solid = 4 * math.pi if space == "full" else 2 * math.pi
        w = 2 * np.pi * f
        # Monopole at 1 m: |p| = rho w^2 Vd_rms / solid. The dipole needs the same pressure through
        # its own falling response, which is where the extra 6 dB per octave turns into excursion.
        monopole_vd = pressure * solid / (acoustics.RHO * w ** 2)
        dipole_vd = monopole_vd / response
        rows = []
        for frequency in target.get("frequencies_hz", [20, 25, 31.5, 40, 50, 63, 80, 100]):
            if not (f[0] <= frequency <= f[-1]):
                continue
            vd = float(np.interp(np.log(frequency), np.log(f), dipole_vd))
            mono = float(np.interp(np.log(frequency), np.log(f), monopole_vd))
            rows.append(dict(frequency_hz=float(frequency), dipole_volume_displacement_rms_m3=vd,
                             monopole_volume_displacement_rms_m3=mono, penalty_ratio=vd / mono,
                             required_excursion_peak_mm=vd * math.sqrt(2) / sd * 1000,
                             drivers_needed_at_stated_xmax=(vd * math.sqrt(2) / sd * 1000 / float(driver["xmax_mm"]))
                             if driver.get("xmax_mm") else None))
        results["excursion_demand"] = dict(
            target_spl_db_at_1m=float(target["spl_db_at_1m"]), space=space, sd_m2=sd,
            xmax_mm=driver.get("xmax_mm"), rows=rows,
            law="18 dB per octave: one octave lower at constant SPL costs eight times the volume displacement, against four "
                "times for a monopole",
            note="drivers_needed_at_stated_xmax is the volume displacement divided by one driver's, so it counts cones, not "
                 "cabinets, and it assumes the excursion figure is the binding one. See driver-selection.md section 4.")

    if params.get("cardioid"):
        results["cardioid"] = _cardioid(params["cardioid"])

    results["comparison"] = dict(
        note="a dipole trades output and efficiency for a pattern. Before choosing one, price the removed output: the 4.8 dB "
             "power deficit, the 6 dB per octave rolloff and the eightfold displacement per octave are all paid before any "
             "of the pattern's benefit arrives.")
    results["validity"] = dict(statements=list(VALIDITY), equivalence_frequency_hz=equivalence_hz,
                               useful_upper_bound_hz=acoustics.C / (2 * path))
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Dipole and gradient open-baffle response, pattern and excursion demand", NOTES, VALIDITY))
