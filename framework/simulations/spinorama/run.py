#!/usr/bin/env python3
"""CTA-2034-A curve family and the Olive preference predictors from a full two-plane orbit."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, preference, radiation  # noqa: E402

NAME = "spinorama"
VERSION = "1.2"
NOTES = [
    "The orbit is computed from the same section model whole_speaker sums: point sources with analytical directivity, declared acoustic depths, supplied electrical transfers and baffle factors.",
    "Every computational detail of the curve family comes from one open-source reimplementation of ANSI/CTA-2034-A, not from the standard text, which is paywalled and was not read. Two of its details differ from the literal standard and are exposed as options; the legacy options are retained for compatibility and do not establish independent standard certification.",
    "Spatial averages are RMS in the pressure domain, not in decibels. Sound power is an area-weighted RMS over the 70-point spin with the published ring weights, and the predicted in-room curve is an energy sum on squared pressure.",
    "Front-only analytic patterns require a declared rear prior. Complete measured, analytical or geometry-derived patterns supply their own rear radiation.",
    "The preference score is Olive's generalized regression over seventy loudspeakers, read at first hand in Harman's patent and evaluated here on modelled curves rather than on anechoic measurements. It ranks; it does not certify.",
    "Every metric is named with the curve it was computed from - NBD_ON, SM_PIR - because NBD, SM and AAD are each defined over any of the seven curves and a bare NBD names nothing. LFX and LFQ are defined on sound power only.",
    "The score's term contributions are reported beside it as the patent states them: NBD_ON 31.5 percent, LFX 30.5 percent, NBD_PIR 20.5 percent, SM_PIR 17.5 percent. Read which term moved a score before reading the score.",
]
VALIDITY = [
    "A score computed from a modelled orbit is not a measured spinorama. The published research it comes from was fitted to measurements, and the distance between this model and a measurement is unquantified: no source consulted states the error between a simulated and a measured directivity.",
    "Sound-power accuracy depends on the supplied rear radiation, whether measured, geometry-derived or a declared shadow prior. Complete coverage is distinct from empirical accuracy.",
    "LFX carries no penalty for Q, group delay or distortion and SM is blind to tilt. A design optimised against this score alone will exploit both.",
]

CONFORMANCE_FULL = ("CTA-2034-A curve definitions as reimplemented in the open-source spinorama project, computed over a "
                    "complete modelled 70-point orbit. The curves are modelled, not measured.")
CONFORMANCE_PARTIAL = ("approximation: the orbit is incomplete, so these curves are front-hemisphere figures and are not "
                       "CTA-2034-A curves. No preference score is emitted from them.")


def _orbit(sections, f, distance, ear):
    """Pressure magnitude at each of the 70 spin points, keyed by (plane, signed degrees)."""
    out = {}
    for plane in ("H", "V"):
        angles = [preference.signed(a) for _, a in preference.spin_angles() if _ == plane]
        points = radiation.observation_points(distance, ear, angles, plane)
        total, _ = radiation.pressure(sections, f, points, distance)
        for index, angle in enumerate(angles):
            out[(plane, angle)] = np.abs(total[index])
    return out


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 20.0, 20000.0, 600)
    observer = params.get("observer") or {}
    distance = float(observer.get("distance_m", 3.0))
    ear = float(observer.get("ear_height_m", 1.0))
    voltage = float(params.get("input_voltage_rms", 2.83))
    options = params.get("options") or {}
    rear_wall = options.get("rear_wall", "standard")
    double_90 = bool(options.get("double_90_degree_weight", False))
    sections = radiation.load_sections(params, f, base_dir)

    def full(record):
        model = record.get("directivity") or {}
        if model.get("kind") in ("omni", "dipole", "cardioid", "distributed_edge_dipole"):
            return True
        if model.get("kind") == "measured_planes":
            from _common.response_data import full_sphere
            return full_sphere(model)
        if model.get("kind") == "complex_grid":
            return (min(model["horizontal_deg"]) <= -180 and max(model["horizontal_deg"]) >= 180
                    and min(model["vertical_deg"]) <= -90 and max(model["vertical_deg"]) >= 90)
        return bool(record.get("rear"))
    without_prior = [w["name"] for w in sections if not full(w)]
    without_prior += [f"{w['name']}/outlet-{i}" for w in sections for i,o in enumerate(w["outlets"]) if not full(o)]
    orbit = _orbit(sections, f, distance, ear)
    silent = sorted({f"{plane}{angle:+d}" for (plane, angle), p in orbit.items() if not np.any(p > 0)})
    complete = not without_prior

    family = preference.assemble(f, orbit, rear_wall, double_90)
    scale = voltage / acoustics.P0
    curves = {name: acoustics.db(family[name] * scale) for name in
              ("on_axis", "listening_window", "early_reflections", "sound_power", "predicted_in_room")}
    curves.update({f"early_reflections_{name}": acoustics.db(curve * scale)
                   for name, curve in family["early_reflection_groups"].items()})

    conformance = CONFORMANCE_FULL if complete else CONFORMANCE_PARTIAL
    results = dict(
        f_hz=f, input_voltage_rms=voltage, observer=dict(distance_m=distance, ear_height_m=ear),
        orbit=dict(points=family["point_count"], angles_deg=sorted({abs(a) for _, a in preference.spin_angles()}),
                   complete=complete, sections_without_rear_prior=without_prior, silent_points=silent,
                   rear_priors=[dict(section=w["name"], prior=w.get("rear")) for w in sections],
                   note="a complete orbit needs every section's radiation defined over 0 to 180 degrees in both planes. "
                        "Without a rear prior, a front-only analytic section uses the "
                        "infinite-baffle idealisation and makes the sound power a front-hemisphere figure."),
        options_used=dict(
            rear_wall=rear_wall, double_90_degree_weight=double_90,
            discrepancies=[
                "rear_wall: the literal standard specifies only +/-90 and 180 degrees; the reimplementation uses the whole "
                "+/-90 to +/-170 fan. Early reflections, the in-room curve and the early-reflections DI all differ between "
                "tools because of it. Default here: standard.",
                "double_90_degree_weight: the reimplementation doubles the 90-degree ring weight as a correction that is not "
                "obviously in the standard. Default here: off.",
                "early_reflections is the RMS of the five group curves rather than of all their constituent angles; the two "
                "conventions differ wherever the groups hold different numbers of points.",
            ]),
        standard_conformance=conformance,
        curves=curves,
        sound_power_di_db=family["sound_power_di_db"],
        early_reflections_di_db=family["early_reflections_di_db"],
        ring_weights=dict(published=preference.RING_WEIGHTS,
                          note="the 90-degree ring carries about 32 times the weight of the on-axis point, which is the "
                               "quantitative reason on-axis flatness barely moves sound power"),
        pir_weights=preference.PIR_WEIGHTS,
        horizontal=dict(angles_deg=[a for _, a in preference.spin_angles() if _ == "H"],
                        spl_db=[acoustics.db(orbit[("H", preference.signed(a))] * scale) for _, a in preference.spin_angles() if _ == "H"]),
        vertical=dict(angles_deg=[a for _, a in preference.spin_angles() if _ == "V"],
                      spl_db=[acoustics.db(orbit[("V", preference.signed(a))] * scale) for _, a in preference.spin_angles() if _ == "V"]),
    )

    analysis = params.get("analysis") or {}
    nbd_band = tuple(analysis.get("nbd_band_hz", preference.NBD_BAND_HZ))
    sm_band = tuple(analysis.get("sm_band_hz", preference.SM_BAND_HZ))
    metrics = {name: preference.curve_metrics(f, curves[name], conformance, nbd_band, sm_band, curve=name)
               for name in ("on_axis", "listening_window", "early_reflections", "sound_power", "predicted_in_room")}
    metrics["lfx"] = preference.lfx(f, curves["sound_power"], curves["listening_window"],
                                    float(analysis.get("lfx_upper_hz", preference.LFX_UPPER_HZ)),
                                    tuple(analysis.get("lfx_reference_band_hz", preference.LW_REFERENCE_BAND_HZ)))
    if metrics["lfx"]:
        metrics["lfx"]["name"] = "LFX"
        metrics["lfx"]["defined_on"] = "sound_power"
        metrics["lfq"] = preference.lfq(f, curves["listening_window"], metrics["lfx"]["frequency_hz"],
                                        float(analysis.get("lfx_upper_hz", preference.LFX_UPPER_HZ)))
    metrics["named"] = sorted({name for row in metrics.values()
                               if isinstance(row, dict) for name in row.get("names", [])} |
                              {row["name"] for row in metrics.values()
                               if isinstance(row, dict) and row.get("name")})
    metrics["naming_rule"] = ("NBD, SM and AAD are each defined over any of ON, LW, ER, PIR, SP, ERDI and SPDI, so they "
                              "are reported as NBD_ON, SM_PIR and so on and never bare. LFX and LFQ are defined on the "
                              "sound power curve only.")
    results["predictors"] = metrics

    di_band = tuple(analysis.get("directivity_index_band_hz", [500.0, 10000.0]))
    inside = (f >= di_band[0]) & (f <= di_band[1])
    if np.any(inside):
        spdi = np.asarray(family["sound_power_di_db"], float)
        results["directivity_index_window"] = dict(
            band_hz=list(di_band), min_db=float(spdi[inside].min()), max_db=float(spdi[inside].max()),
            mean_db=float(spdi[inside].mean()),
            slope_db_per_octave=float(np.polyfit(np.log2(f[inside]), spdi[inside], 1)[0]),
            broadcast_windows=dict(itu_r_bs_1116_3="6 to 12 dB over 500 Hz to 10 kHz, rising smoothly",
                                   ebu_tech_3276="4 to 12 dB over 250 Hz to 16 kHz, radiation maximum on the main axis"),
            note="the two documents disagree and neither defines the integration method, which materially changes the value. "
                 "The 12 dB ceiling excludes typical constant-directivity PA horns from qualifying as reference monitors.")

    if complete and metrics["lfx"] and metrics["on_axis"]["nbd"] and metrics["predicted_in_room"]["nbd"] \
            and metrics["predicted_in_room"]["smoothness"]:
        results["preference"] = dict(
            preference.preference_score(metrics["on_axis"]["nbd"]["value"], metrics["predicted_in_room"]["nbd"]["value"],
                                        metrics["lfx"]["value"], metrics["predicted_in_room"]["smoothness"]["value"]),
            basis=conformance,
            terms_used=dict(nbd_on=metrics["on_axis"]["nbd"]["name"], nbd_pir=metrics["predicted_in_room"]["nbd"]["name"],
                            sm_pir=metrics["predicted_in_room"]["smoothness"]["name"], lfx="LFX on sound power"),
            note="Olive's generalized model over seventy loudspeakers, read at first hand in the patent and evaluated on "
                 "modelled curves. LFX carries 30.5 percent of the model on its own and one octave of extension is worth "
                 "1.30 points. A 'with subwoofer' variant substitutes a fixed extension whose constant is contested "
                 "between 14.5 and 20 Hz, a difference of 0.60 points; it is not computed here.")
    else:
        reason = []
        if without_prior:
            reason.append(f"these sections declare no rear_radiation prior: {without_prior}")
        if silent:
            reason.append(f"these orbit points are silent at every frequency: {silent[:8]}")
        if not reason:
            reason.append("one or more predictors could not be computed on the supplied frequency grid")
        results["preference_withheld"] = dict(
            reason="; ".join(reason),
            note="two of the four preference terms are directivity measurements, so a score from a front-hemisphere orbit "
                 "would be a number about a different loudspeaker. Declare a rear_radiation prior on every section, or read "
                 "the curves above as front-hemisphere approximations.")

    results["validity"] = dict(statements=list(VALIDITY), orbit_complete=complete,
                               grid_covers_nbd_band=bool(f.min() <= nbd_band[0] and f.max() >= nbd_band[1]),
                               grid_covers_sm_band=bool(f.min() <= sm_band[0] and f.max() >= sm_band[1]))
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "CTA-2034-A curve family and Olive preference predictors", NOTES, VALIDITY))
