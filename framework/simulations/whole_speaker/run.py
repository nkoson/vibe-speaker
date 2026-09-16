#!/usr/bin/env python3
"""Coherent whole-speaker response: every section at its position with its filter, directivity and baffle, on and off axis."""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, arrays, radiation  # noqa: E402

NAME = "whole_speaker"
VERSION = "1.2"
NOTES = [
    "Point-source sum of the sections with analytical directivity, declared acoustic depths and the supplied electrical transfers; no BEM, no cabinet scattering beyond the supplied baffle factors, no room except the optional single floor image.",
    "SPL is normalized to the reference distance so that it reads like a 1 m figure; the common propagation delay is removed.",
    "Rear outlets radiate as monopoles into 4 pi (factor 0.5) unless a baffle reference is given; the cabinet depth sets their offset.",
    "Statistics are descriptive figures of the computed curves; acceptability is not decided here.",
    "The pair geometry is arithmetic over the positions already in the model: the spacing, the depth offset and the frequencies they imply. It is a prediction available before any filter is fitted, and it does not depend on the crossover the fit landed on.",
    "The array block covers the case the pair geometry does not: two or more sources reproducing the SAME band. Its criteria are Urban, Heil and Bauman's, stated as pass or fail, and the groups are declared rather than inferred - this model sums sections, and a driver pair inside one section is one point source to it.",
    "The near/far-field border is computed for a line source of the declared coherent radiating height. A conventional multiway is not an isophasic line source, so the border is an indication of where far-field assumptions become safe and not a computed property of this geometry.",
]
VALIDITY = [
    "Every angle map here is a far-field construction. Where the observation distance sits inside the near-field border reported in results.arrays, level falls 3 dB per doubling of distance rather than 6 and the polar data is not a far-field property at all.",
    "Point sources with analytical directivity: no cabinet scattering beyond the supplied baffle factors, no enclosure reflections, no BEM. The crossover region on a real cabinet is shaped by exactly those effects.",
    "The sum is valid where each section's own directivity model is valid. A piston pattern assumes pistonic behaviour, which stops at break-up; a horn coverage prior carries no throat or mouth physics.",
    "The forward hemisphere only: a section at or behind 90 degrees from its axis contributes nothing unless a rear-hemisphere prior is declared. Sound power and any directivity index computed from this model without one are front-hemisphere figures.",
    "No source consulted states the decibel or degree error between a simulated and a measured system response, so this curve carries no error bar from the literature.",
]


def _stats(f, total_db, per_section_db, analysis, sections):
    out = {}
    for band in analysis.get("ripple_bands_hz", [[100.0, 16000.0]]):
        inside = (f >= band[0]) & (f <= band[1])
        if np.any(inside):
            out[f"ripple_{int(band[0])}_{int(band[1])}_db"] = float(np.ptp(total_db[inside]))
            out[f"mean_{int(band[0])}_{int(band[1])}_db"] = float(np.mean(total_db[inside]))
    sens = analysis.get("sensitivity_band_hz", [500.0, 10000.0])
    inside = (f >= sens[0]) & (f <= sens[1])
    if np.any(inside):
        out["sensitivity_band_hz"] = list(sens)
        out["mean_spl_in_sensitivity_band_db"] = float(np.mean(total_db[inside]))
        out["median_spl_in_sensitivity_band_db"] = float(np.median(total_db[inside]))
    ref_band = analysis.get("reference_band_hz", [150.0, 300.0])
    if np.any((f >= ref_band[0]) & (f <= ref_band[1])):
        cut = {}
        for level in analysis.get("cutoff_thresholds_db", [-3.0, -6.0, -10.0]):
            value, bound, reference = acoustics.sustained_cutoff(f, total_db, level, tuple(ref_band))
            cut[f"f{abs(int(level))}"] = dict(value_hz=value, bound=bound)
            cut["reference_level_db"] = float(reference)
        out["low_cutoffs"] = cut
    tol = analysis.get("band_tolerance_db")
    if tol and np.any(inside):
        out["band_within_tolerance"] = acoustics.band_within(f, total_db - out["mean_spl_in_sensitivity_band_db"], float(tol), sens)
    out["acoustic_crossings"] = [dict(row, lower_section=sections[row["lower_section"]]["name"], upper_section=sections[row["upper_section"]]["name"])
                                 for row in radiation.acoustic_crossings(f, per_section_db, analysis.get("crossing_search_band_hz"))]
    presence = []
    for i, section in enumerate(sections):
        dominant = np.flatnonzero(per_section_db[i] >= np.max(per_section_db, axis=0) - 1e-9)
        if len(dominant):
            band = (float(f[dominant[0]]), float(f[dominant[-1]]))
            inside = (f >= band[0]) & (f <= band[1])
            presence.append(dict(section=section["name"], dominant_band_hz=list(band),
                                 min_level_below_sum_in_band_db=float(np.min(per_section_db[i][inside] - total_db[inside]))))
        else:
            presence.append(dict(section=section["name"], dominant_band_hz=None))
    out["section_presence"] = presence
    return out


def _pair_geometry(sections, crossings):
    """Spacing, depth offset and the three frequencies they decide, for every adjacent pair.

    d1 is the centre-to-centre spacing in the baffle plane and d2 the acoustic depth offset between
    the two centres. c / (2 d1) is the lowest frequency at which the pair can null at all, c / d1 is
    the spacing bound d1 / lambda = 1 above which the pattern breaks into multiple beams, and
    arctan(d2 / d1) is the angle the main lobe tilts toward the lagging driver.
    """
    rows = []
    for i in range(len(sections) - 1):
        a, b = sections[i], sections[i + 1]
        d1 = float(np.hypot(a["centre"][0] - b["centre"][0], a["centre"][2] - b["centre"][2]))
        d2 = float(abs(a["centre"][1] - b["centre"][1]))
        row = dict(sections=[a["name"], b["name"]], spacing_mm=d1 * 1000, depth_offset_mm=d2 * 1000)
        if d1 > 0:
            row.update(null_frequency_hz=acoustics.C / (2 * d1), spacing_bound_hz=acoustics.C / d1,
                       lobe_tilt_deg=float(np.rad2deg(np.arctan2(d2, d1))))
        else:
            row.update(null_frequency_hz=None, spacing_bound_hz=None, lobe_tilt_deg=None,
                       note="the two acoustic centres are coincident in the baffle plane, so the pair has no spacing null")
        row["offset_delay_us"] = d2 / acoustics.C * 1e6
        row["at_crossings"] = [
            dict(frequency_hz=c["frequency_hz"], d1_over_lambda=d1 * c["frequency_hz"] / acoustics.C,
                 phase_difference_per_degree_off_axis=360 * d1 * c["frequency_hz"] / acoustics.C * np.deg2rad(1.0))
            for c in crossings
            if c["lower_section"] == a["name"] and c["upper_section"] == b["name"]]
        rows.append(row)
    return dict(pairs=rows,
                bounds="d1 / lambda < 1 at the crossover is an upper bound, not a target: at exactly one wavelength the "
                       "pattern is already badly compromised. Below c / (2 d1) the pair still tilts and narrows its lobe "
                       "but cannot null.",
                note="a depth offset can be corrected electrically only by a pure delay of d2 / c, which a passive network "
                     "cannot generally supply. In a passive design the offset is handled mechanically - a stepped or sloped "
                     "baffle, a recessed driver, an asymmetric crossover order - or accepted as lobe tilt and stated.")


def _arrays(spec, distance):
    """Same-band group criteria and the near/far-field border, for the case _pair_geometry misses.

    Every figure here is arithmetic over declared geometry, and the spacing limit in particular is
    available before any filter is fitted: an MTM with 180 mm between woofer acoustic centres is two
    sources above 953 Hz, and that is the number that should set its crossover.
    """
    spec = dict(spec or {})
    out = dict(criteria=list(arrays.WST_CRITERIA),
               groups=[arrays.same_band_group(group) for group in (spec.get("groups") or [])])
    height = spec.get("coherent_radiating_height_mm")
    if height:
        frequencies = spec.get("border_frequencies_hz") or [63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        table = arrays.near_field_table(frequencies, float(height) / 1000, distance)
        inside = [row["frequency_hz"] for row in table["rows"] if row.get("observer_inside_near_field")]
        out["near_field"] = dict(table, observer_inside_near_field_above_hz=min(inside, default=None))
    else:
        out["near_field"] = dict(
            available=False,
            note="give arrays.coherent_radiating_height_mm - the height of the coherent radiating section, not the "
                 "cabinet - to have the near/far-field border computed against this result's observation distance.")
    return out


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 20.0, 20000.0, 600)
    observer = params.get("observer") or {}
    distance = float(observer.get("distance_m", 3.0))
    ear = float(observer.get("ear_height_m", 1.0))
    voltage = float(params.get("input_voltage_rms", 2.83))
    sections = radiation.load_sections(params, f, base_dir)
    analysis = params.get("analysis") or {}
    axis = radiation.observation_points(distance, ear, [0.0], "V")
    total, parts = radiation.pressure(sections, f, axis, distance)
    scale = voltage / acoustics.P0
    total_db = acoustics.db(total[0] * scale)
    per_section_db = np.array([acoustics.db(parts[i, 0] * scale) for i in range(len(sections))])
    results = dict(f_hz=f, input_voltage_rms=voltage, observer=dict(distance_m=distance, ear_height_m=ear),
                   on_axis=dict(spl_db=total_db, pressure=total[0] * voltage, phase_deg=np.rad2deg(np.unwrap(np.angle(total[0]))),
                                sections=[dict(name=w["name"], spl_db=per_section_db[i], phase_deg=np.rad2deg(np.unwrap(np.angle(parts[i, 0])))) for i, w in enumerate(sections)],
                                power_sum_db=10 * np.log10(np.sum(np.abs(parts[:, 0, :] * scale) ** 2, axis=0))),
                   geometry=[dict(name=w["name"], centre_m=w["centre"], distance_to_observer_m=float(np.linalg.norm(axis[0] - w["centre"])),
                                  directivity=w["directivity"], outlets=[dict(centre_m=o["centre"], face=o["face"]) for o in w["outlets"]]) for w in sections])
    distances = np.array([g["distance_to_observer_m"] for g in results["geometry"]])
    results["path_differences"] = [dict(sections=[sections[i]["name"], sections[j]["name"]], difference_mm=float((distances[i] - distances[j]) * 1000),
                                        delay_us=float((distances[i] - distances[j]) / acoustics.C * 1e6))
                                   for i in range(len(sections)) for j in range(i + 1, len(sections))]
    h_angles = observer.get("horizontal_angles_deg", list(range(-90, 91, 5)))
    v_angles = observer.get("vertical_angles_deg", list(range(-30, 31, 5)))
    for label, angles, plane in (("horizontal", h_angles, "H"), ("vertical", v_angles, "V")):
        if angles:
            pts = radiation.observation_points(distance, ear, angles, plane)
            grid, _ = radiation.pressure(sections, f, pts, distance)
            grid_db = acoustics.db(grid * scale)
            results[label] = dict(angles_deg=angles, spl_db=grid_db, relative_to_axis_db=grid_db - total_db[None, :])
            window = observer.get(f"{label}_window_deg")
            if window:
                inside = np.abs(np.asarray(angles, float)) <= float(window)
                results[label]["window_deg"] = float(window)
                results[label]["window_max_deviation_db"] = float(np.max(np.abs(grid_db[inside] - total_db[None, :])))
                results[label]["window_mean_spl_db"] = np.mean(grid_db[inside], axis=0)
    floor = params.get("floor")
    if floor and floor.get("cases"):
        rows = []
        for case in floor["cases"]:
            d = float(case.get("distance_m", distance))
            e = float(case.get("ear_height_m", ear))
            r = float(case.get("reflection", floor.get("reflection", 0.7)))
            pts = radiation.observation_points(d, e, [0.0], "V")
            with_floor, _ = radiation.pressure(sections, f, pts, d, floor_reflection=r)
            free, _ = radiation.pressure(sections, f, pts, d)
            rows.append(dict(distance_m=d, ear_height_m=e, reflection=r, spl_db=acoustics.db(with_floor[0] * scale),
                             relative_to_free_field_db=acoustics.db(with_floor[0]) - acoustics.db(free[0])))
        results["floor_cases"] = rows
    if params.get("polarity_study") and len(sections) > 1:
        rows = []
        band = analysis.get("ripple_bands_hz", [[100.0, 16000.0]])[0]
        inside = (f >= band[0]) & (f <= band[1])
        for signs in itertools.product([1, -1], repeat=len(sections) - 1):
            transfers = [sections[0]["transfer"]] + [sections[i + 1]["transfer"] * s for i, s in enumerate(signs)]
            p, _ = radiation.pressure(sections, f, axis, distance, transfers)
            curve = acoustics.db(p[0] * scale)
            rows.append(dict(signs=[1, *signs], spl_db=curve, ripple_db=float(np.ptp(curve[inside])), mean_db=float(np.mean(curve[inside]))))
        results["polarity_study"] = dict(band_hz=list(band), cases=rows)
    depth_study = analysis.get("depth_perturbation_mm")
    if depth_study:
        # one figure for every section, or one per section by name: an acoustic centre 15 mm behind the
        # baffle and one 180 mm behind it do not have the same plausible mounting uncertainty
        if isinstance(depth_study, dict):
            unknown = sorted(set(depth_study) - {w["name"] for w in sections})
            if unknown:
                raise cli.InputError(f"analysis.depth_perturbation_mm names sections that do not exist: {unknown}")
            amounts = {w["name"]: depth_study.get(w["name"]) for w in sections}
        else:
            amounts = {w["name"]: float(depth_study) for w in sections}
        rows = []
        for i, section in enumerate(sections):
            amount = amounts.get(section["name"])
            if amount in (None, 0):
                continue
            for delta in (-abs(float(amount)), abs(float(amount))):
                moved = [dict(w) for w in sections]
                moved[i] = dict(section, centre=section["centre"] + np.array([0.0, -delta / 1000, 0.0]))
                p, _ = radiation.pressure(moved, f, axis, distance)
                rows.append(dict(section=section["name"], depth_change_mm=delta,
                                 acoustic_depth_mm=section.get("acoustic_depth_mm"),
                                 spl_db=acoustics.db(p[0] * scale)))
        results["depth_perturbations"] = rows
    results["statistics"] = _stats(f, total_db, per_section_db, analysis, sections)
    results["pair_geometry"] = _pair_geometry(sections, results["statistics"]["acoustic_crossings"])
    results["arrays"] = _arrays(params.get("arrays"), distance)
    results["validity"] = dict(statements=list(VALIDITY), observer_distance_m=distance,
                               far_field_guideline_m=3 * float((params.get("baffle") or {}).get("width_mm", 0)) / 1000 or None,
                               rear_hemisphere_modelled=False)
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Coherent whole-speaker response on and off axis", NOTES, VALIDITY))
