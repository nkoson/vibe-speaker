#!/usr/bin/env python3
"""Low-frequency lumped box model: sealed, vented, aperiodic, passive-radiator or bandpass enclosure."""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, bass, thermal  # noqa: E402

NAME = "lf_box"
VERSION = "1.2"
NOTES = [
    "Linear lumped electro-mechanical-acoustic model at small signal; no suspension or Bl nonlinearity, thermal compression, port turbulence or cone breakup.",
    "Pressures are at 1 m in the stated radiation space (half = 2 pi infinite baffle, full = 4 pi free field); excursion and port air speed are sine peak values.",
    "Mms derived from Fs and Vas already contains radiation mass. Ql models enclosure leakage, Qp duct loss.",
    "Duct length is a straight round vent estimate with a 0.732 d end correction; a flared duct's tuning is reported separately from the throat dimensions and is not fed back into the response.",
    "Cutoff frequencies are descriptive statistics of the computed curve relative to the mean level in the reference band.",
    "The port Reynolds number is computed from the linear peak velocity. Port compression is not modelled at all: every port measured in the source study showed about 10 dB of compression at tuning at 40 V drive.",
    "The displacement-limited rating is Small's programme figure, not a measurement, and a linear model cannot see force-factor modulation or an Sd that varies with excursion.",
    "A coil-temperature scenario scales Re only. The motor, the suspension and the box are unchanged, so it is the first-order thermal effect and not a hot-driver model.",
    "An Xmax figure is meaningless without its definition. Four are in circulation - geometric, AES2-1984, the IEC 62458 two-tone procedure and AES2-2012 clause 5.5 - and only the last two measure the same quantity, so the definition travels with every displacement figure this application prints.",
    "Bandpass boxes are solved as the chamber circuit given, with no alignment table behind them: none was obtained for any bandpass family. The driver radiates into its chambers only and every reported decibel leaves through a port.",
    "The isobaric flag transforms the driver record into its coupled-pair equivalent before the box maths runs: Mms doubles, Cms halves, Vas halves, fs and Qts are unchanged and reference efficiency falls 3 dB. It is a derivation from the Thiele/Small definitions, not a citation.",
    "The aperiodic vent is one series resistance in the vent branch. RAV has no published relation to stuffing density or vent-covering material, so the application sweeps it and refuses to present one value as a designed alignment.",
]
VALIDITY = [
    "Lumped elements hold while every dimension is small compared with a wavelength; cone break-up and internal standing waves arrive before the model announces them.",
    "No source consulted states the decibel error between a simulated and a measured bass response, so the model carries no error bar from the literature, only its declared assumptions.",
]


def _stats(f, r, reference_band, thresholds, stress_band):
    inside = (f >= reference_band[0]) & (f <= reference_band[1])
    reference = float(np.mean(r["spl_db"][inside])) if np.any(inside) else None
    cutoffs = {}
    if reference is not None:
        for level in thresholds:
            value, bound, _ = acoustics.sustained_cutoff(f, r["spl_db"], level, reference_band, reference)
            cutoffs[f"f{abs(int(level))}"] = dict(value_hz=value, bound=bound, threshold_db=float(level))
    stress = (f >= stress_band[0]) & (f <= stress_band[1])
    zmag = np.abs(r["z_ohm"])
    out = dict(reference_band_hz=list(reference_band), reference_level_db=reference, cutoffs=cutoffs,
               impedance_min_ohm=float(zmag.min()), impedance_min_hz=float(f[np.argmin(zmag)]),
               impedance_max_ohm=float(zmag.max()), impedance_max_hz=float(f[np.argmax(zmag)]),
               stress_band_hz=list(stress_band),
               max_excursion_peak_mm=float(r["excursion_peak_mm"][stress].max()),
               max_excursion_hz=float(f[stress][np.argmax(r["excursion_peak_mm"][stress])]),
               max_copper_loss_w=float(r["copper_loss_w"].max()), max_spl_db=float(r["spl_db"].max()),
               max_spl_hz=float(f[np.argmax(r["spl_db"])]))
    if "port_air_speed_peak_ms" in r:
        out["max_port_air_speed_peak_ms"] = float(r["port_air_speed_peak_ms"][stress].max())
        out["max_port_air_speed_hz"] = float(f[stress][np.argmax(r["port_air_speed_peak_ms"][stress])])
    if "radiator_excursion_peak_mm" in r:
        out["max_radiator_excursion_peak_mm"] = float(r["radiator_excursion_peak_mm"][stress].max())
    return out


def _scaling(f, base, voltage, limits, stress_band):
    """Voltage and SPL at which each supplied limit is reached, by linear scaling of the base curve."""
    stress = (f >= stress_band[0]) & (f <= stress_band[1])
    rows = []
    if limits.get("xmax_mm"):
        peak = float(base["excursion_peak_mm"][stress].max())
        v = voltage * float(limits["xmax_mm"]) / peak
        rows.append(dict(limit="cone_excursion", limit_value=float(limits["xmax_mm"]), unit="mm peak", voltage_rms=v,
                         limiting_hz=float(f[stress][np.argmax(base["excursion_peak_mm"][stress])]),
                         limit_basis=limits.get("xmax_basis")))
    if limits.get("max_port_air_speed_ms") and "port_air_speed_peak_ms" in base:
        peak = float(base["port_air_speed_peak_ms"][stress].max())
        v = voltage * float(limits["max_port_air_speed_ms"]) / peak
        rows.append(dict(limit="port_air_speed", limit_value=float(limits["max_port_air_speed_ms"]), unit="m/s peak", voltage_rms=v,
                         limiting_hz=float(f[stress][np.argmax(base["port_air_speed_peak_ms"][stress])])))
    if limits.get("radiator_xmax_mm") and "radiator_excursion_peak_mm" in base:
        peak = float(base["radiator_excursion_peak_mm"][stress].max())
        v = voltage * float(limits["radiator_xmax_mm"]) / peak
        rows.append(dict(limit="radiator_excursion", limit_value=float(limits["radiator_xmax_mm"]), unit="mm peak", voltage_rms=v,
                         limiting_hz=float(f[stress][np.argmax(base["radiator_excursion_peak_mm"][stress])])))
    if limits.get("power_w"):
        nominal = float(limits.get("nominal_impedance_ohm") or base["elements"]["re"])
        rows.append(dict(limit="rated_power", limit_value=float(limits["power_w"]), unit="W into nominal impedance",
                         voltage_rms=float(np.sqrt(float(limits["power_w"]) * nominal)), limiting_hz=None))
    for row in rows:
        gain = 20 * np.log10(row["voltage_rms"] / voltage)
        row["spl_gain_db_relative_to_base"] = float(gain)
        row["spl_db_at_limit"] = cli.to_jsonable(base["spl_db"] + gain)
    return rows


def _alignments(ts, spec):
    """Solve every requested alignment against the driver, so QL and the required QT are explicit."""
    requests = spec if isinstance(spec, list) else [spec]
    rows = []
    for request in requests:
        request = dict(request or {})
        target = request.get("target", "B4")
        for ql in (request.get("ql_values") or [request.get("ql", 7.0)]):
            rows.append(bass.alignment_for_driver(ts, target, ql, request.get("a2")))
    return rows


def _validity(ts, enclosure, f):
    """The band in which the lumped model can be believed, from what the parameter set already says."""
    radius = math.sqrt(float(ts["sd_cm2"]) * 1e-4 / math.pi)
    out = dict(evaluated_band_hz=[float(f[0]), float(f[-1])],
               piston_ka_unity_hz=acoustics.C / (2 * math.pi * radius),
               piston_radius_m=radius,
               statements=list(VALIDITY))
    dimensions = enclosure.get("internal_dimensions_mm")
    if dimensions:
        longest = max(float(x) for x in dimensions)
        out["first_axial_mode_hz"] = acoustics.C / (2 * longest / 1000)
        out["lumped_upper_bound_hz"] = out["first_axial_mode_hz"]
        out["statements"] = out["statements"] + [
            f"The longest internal dimension is {longest:g} mm, so the first axial standing wave is at "
            f"{out['first_axial_mode_hz']:.0f} Hz and the lumped box model should not be read above it; run cavity_modes there."]
    else:
        out["statements"] = out["statements"] + [
            "enclosure.internal_dimensions_mm was not given, so the frequency of the first internal standing wave, and "
            "with it the upper bound of the lumped model, is unknown."]
    return out


def _bandpass_exchange(f, curve, ts, efficiency, voltage):
    """The bandwidth-for-gain exchange, stated as numbers so the midband gain is never read as free output."""
    spl = np.asarray(curve["spl_db"], float)
    peak = float(spl.max())
    top = int(np.argmax(spl))
    rows = {}
    for level in (-3.0, -6.0):
        low = np.flatnonzero((np.arange(len(f)) < top) & (spl < peak + level))
        high = np.flatnonzero((np.arange(len(f)) > top) & (spl < peak + level))
        lo = float(f[low[-1]]) if len(low) else None
        hi = float(f[high[0]]) if len(high) else None
        rows[f"passband_{abs(int(level))}_db"] = dict(
            low_hz=lo, high_hz=hi,
            width_octaves=float(np.log2(hi / lo)) if lo and hi else None,
            bound="resolved" if lo and hi else "not_resolved_on_this_grid")
    reference = efficiency["sensitivity_1w_1m_half_space_db"] + 20 * math.log10(voltage / math.sqrt(ts["re_ohm"]))
    return dict(rows, peak_spl_db=peak, peak_hz=float(f[top]),
                driver_reference_sensitivity_db=reference,
                midband_gain_over_reference_db=peak - reference,
                exchange="bandwidth and gain are exchangeable: narrowing the passband raises the midband level because the "
                         "same displacement-limited volume velocity is concentrated into fewer octaves. The gain is not "
                         "created output, it is the output of the bands that were given up, and it is the only reason to "
                         "build a bandpass box.")


def _bandpass_ports(bandpass, stress_band):
    """Every port's first pipe resonance, and the failure it marks."""
    rows = []
    for port in bandpass["ports"]:
        resonance = port["pipe_resonance_hz"]
        limit = port["lumped_limit_hz"]
        rows.append(dict(chamber=port["chamber"], tuning_hz=port["tuning_hz"], radiates_to_room=port["radiates_to_room"],
                         physical_length_mm=port["vent"]["physical_length_mm"],
                         effective_length_mm=port["vent"]["effective_length_mm"], diameter_mm=port["vent"]["diameter_mm"],
                         count=port["vent"]["count"], pipe_resonance_hz=resonance, lumped_limit_hz=limit,
                         resonance_above_stress_band=bool(resonance and resonance > stress_band[1]),
                         lumped_limit_above_stress_band=bool(limit and limit > stress_band[1])))
    return dict(ports=rows,
                derivation="A port is a tube open at both ends. Its first pipe resonance is the half-wave one, "
                           "f = c / (2 L_eff), on the end-corrected length L_eff = L_physical + 0.732 d; the chamber's "
                           "compliance lifts it only slightly. At f = c / (4 L_eff) the lumped-mass model already "
                           "under-states the port's volume velocity by 3.9 dB (kL / sin kL = pi / 2), so the box's "
                           "acoustic low-pass is no longer what the model shows from there up.",
                consequence="above its first pipe resonance the acoustic low-pass stops working and out-of-band energy is "
                            "radiated straight out of the port. The published comparison of a lumped-mass port against the "
                            "same port modelled as a transmission line makes the conclusion flat: AN ELECTRICAL LOW-PASS "
                            "FILTER IS IN PRACTICE MANDATORY on a bandpass box. A design that relies on the enclosure alone "
                            "for its low-pass is relying on a model that has stopped being true.",
                geometry_warning="a long, narrow port pushes this frequency down into the region the box was supposed to "
                                 "filter, and a low tuning in a small chamber is exactly what asks for one.")


def compute(params, base_dir):
    ts = dict(cli.require(params, "driver", "ts"))
    enclosure = dict(cli.require(params, "enclosure"))
    isobaric = (params.get("driver") or {}).get("isobaric")
    isobaric_report = None
    if isobaric:
        spec = isobaric if isinstance(isobaric, dict) else {}
        ts, isobaric_report = bass.isobaric_pair(ts, spec.get("wiring", "series"))
    scenario = params.get("thermal")
    thermal_report = None
    if scenario:
        cold = float(ts["re_ohm"])
        hot = thermal.resistance_at(cold, cli.require(scenario, "coil_temperature_c", label="thermal"),
                                    float(scenario.get("reference_c", 20.0)),
                                    float(scenario.get("copper_coefficient_per_c", thermal.COPPER_COEFFICIENT_PER_C)))
        ts["re_ohm"] = hot
        ts["qes"] *= hot / cold
        thermal_report = dict(coil_temperature_c=float(scenario["coil_temperature_c"]),
                              reference_c=float(scenario.get("reference_c", 20.0)),
                              re_cold_ohm=cold, re_hot_ohm=hot, resistance_ratio=hot / cold,
                              compression_db=thermal.compression_db(cold, hot),
                              note="Re is scaled by 1 + 0.0039 (T - T0) and the whole model recomputed; Qes, Qts and the "
                                   "alignment move with it. The abort point of the standard power test is 130 percent of "
                                   "cold Re, about +80 K.")
    if enclosure.get("type") == "sealed" and enclosure.get("net_volume_l") is None and enclosure.get("qtc"):
        enclosure["net_volume_l"] = acoustics.sealed_volume_for_qtc(ts, float(enclosure["qtc"]))
    drive = params.get("drive") or {}
    voltages = [float(v) for v in drive.get("voltages_rms", [2.83])]
    series_r = float(drive.get("series_resistance_ohm", 0.0))
    space = drive.get("space", "half")
    f = cli.frequency_grid(params.get("frequencies"), 10.0, 1500.0, 480)
    transfer = None
    if params.get("terminal_transfer"):
        transfer = cli.curve_from_reference(params["terminal_transfer"], base_dir, f)
    analysis = params.get("analysis") or {}
    reference_band = tuple(analysis.get("reference_band_hz", [150.0, 300.0]))
    thresholds = analysis.get("cutoff_thresholds_db", [-3.0, -6.0, -10.0])
    stress_band = tuple(analysis.get("stress_band_hz", [float(f[0]), 300.0]))

    # One enclosure per curve. Only the aperiodic vent has more than one: its resistance has no
    # source, so it is swept and the bracketing sealed and vented boxes are computed beside it.
    cases = [dict(enclosure=enclosure)]
    if enclosure.get("type") == "aperiodic":
        sweep = [float(x) for x in (enclosure.get("rav_sweep_pa_s_per_m3") or [])]
        if len(sweep) < 2:
            raise cli.InputError(
                "an aperiodic vent needs enclosure.rav_sweep_pa_s_per_m3 with at least two values. RAV has no published "
                "relation to stuffing density or vent-covering material, so a single value would be presented as a "
                "designed alignment when it is one point of an exploration. Sweep it, or ask for a sealed or vented box.")
        cases = [dict(enclosure=dict(enclosure, rav_pa_s_per_m3=rav), rav_pa_s_per_m3=rav) for rav in sorted(sweep)]
    curves = []
    for case in cases:
        for v in voltages:
            r = acoustics.box_response(ts, case["enclosure"], f, v, series_r, space, transfer)
            curve = dict(voltage_rms=v, spl_db=r["spl_db"], pressure_pa=r["pressure_pa"], cone_pressure_pa=r["cone_pressure_pa"],
                         z_ohm=r["z_ohm"], excursion_peak_mm=r["excursion_peak_mm"], copper_loss_w=r["copper_loss_w"],
                         current_rms_a=r["current_rms_a"], statistics=_stats(f, r, reference_band, thresholds, stress_band))
            if "rav_pa_s_per_m3" in case:
                curve["rav_pa_s_per_m3"] = case["rav_pa_s_per_m3"]
            for key in ("outlet_pressure_pa", "port_air_speed_peak_ms", "radiator_excursion_peak_mm"):
                if key in r:
                    curve[key] = r[key]
            curves.append(curve)
    enclosure = cases[0]["enclosure"]
    base = acoustics.box_response(ts, enclosure, f, voltages[0], series_r, space, transfer)
    elements = base["elements"]
    results = dict(f_hz=f, enclosure_used=enclosure,
                   derived_driver=dict(sd_m2=elements["sd"], cms_m_per_n=elements["cms"], mms_g=elements["mms"] * 1000,
                                       rms_ns_per_m=elements["rms"], bl_tm=elements["bl"], qts=elements["qts"],
                                       ebp_hz=float(ts["fs_hz"] / ts["qes"])),
                   curves=curves)
    if thermal_report:
        results["thermal_scenario"] = thermal_report
    if isobaric_report:
        results["isobaric"] = isobaric_report
    for key in ("vent", "radiator", "system_resonance_hz", "qtc", "aperiodic", "bandpass"):
        if key in base:
            results[key] = base[key]
    if "qtc" in results:
        results["sealed_alignment"] = bass.sealed_alignment(results["qtc"])
    if ts.get("mms_g") or ts.get("bl_tm"):
        results["published_consistency"] = {k: float(abs(v / ts[k] - 1)) for k, v in
                                            (("mms_g", elements["mms"] * 1000), ("bl_tm", elements["bl"])) if ts.get(k)}

    # Two numbers that end arguments early, reported whatever else was asked for: the efficiency the
    # driver's own parameters fix, and the ceiling this volume and extension cannot be taken above.
    efficiency = bass.reference_efficiency(ts)
    f3 = (curves[0]["statistics"]["cutoffs"].get("f3") or {}).get("value_hz")
    efficiency["ceiling"] = bass.efficiency_ceiling(f3, enclosure.get("net_volume_l"), efficiency["eta_0"])
    measured = curves[0]["statistics"]["reference_level_db"]
    if measured is not None:
        efficiency["modelled_reference_band_level_db"] = measured
        efficiency["modelled_minus_formula_db"] = measured - (efficiency["sensitivity_1w_1m_half_space_db"] +
                                                              20 * math.log10(voltages[0] / math.sqrt(ts["re_ohm"])))
    results["efficiency"] = efficiency

    displacement = bass.binding_displacement_limit(ts)
    if displacement:
        results["displacement_limit"] = displacement
        output = bass.displacement_limited_output(ts["sd_cm2"], displacement["xmax_mm"], f3, efficiency["eta_0"],
                                                  float(analysis.get("kp", bass.KP_DEFAULT)))
        if output:
            results["displacement_limited_output"] = output

    if "bandpass" in results:
        results["bandpass"]["port_resonances"] = _bandpass_ports(results["bandpass"], stress_band)
        results["bandpass"]["exchange"] = _bandpass_exchange(f, curves[0], ts, efficiency, voltages[0])
        vd = (displacement or {}).get("xmax_mm")
        for port, row in zip(results["bandpass"]["ports"], results["bandpass"]["port_resonances"]["ports"]):
            row["vent_physics"] = bass.vent_physics(
                port["vent"], port["tuning_hz"], port["chamber_volume_l"],
                float(np.max(port["air_speed_peak_ms"])),
                elements["sd"] * vd * 1e-3 if vd else None, None)

    if "aperiodic" in results:
        limits = {}
        for label, spec in (("sealed_limit", dict(type="sealed", net_volume_l=enclosure["net_volume_l"], ql=enclosure.get("ql", 10.0))),
                            ("vented_limit", dict(enclosure, type="vented"))):
            limits[label] = acoustics.box_response(ts, spec, f, voltages[0], series_r, space, transfer)["spl_db"]
        results["aperiodic"]["sweep"] = dict(
            rav_values_pa_s_per_m3=[c["rav_pa_s_per_m3"] for c in cases],
            sealed_limit_spl_db=limits["sealed_limit"], vented_limit_spl_db=limits["vented_limit"],
            cutoffs=[dict(rav_pa_s_per_m3=c["rav_pa_s_per_m3"], voltage_rms=c["voltage_rms"],
                          cutoffs=c["statistics"]["cutoffs"], max_excursion_peak_mm=c["statistics"]["max_excursion_peak_mm"],
                          impedance_min_ohm=c["statistics"]["impedance_min_ohm"])
                     for c in curves if "rav_pa_s_per_m3" in c],
            status="EXPLORATORY. The two limits are rigorous - infinite RAV is the sealed box, zero RAV the vented one - and "
                   "everything between them is a free parameter with no published value. Do not report one row of this "
                   "sweep as a designed alignment, and do not quote a rolloff slope from it: the 18 dB/octave claim was "
                   "found in no source that derives it.")

    if "vent" in results:
        vd = (displacement or {}).get("xmax_mm")
        results["vent_physics"] = bass.vent_physics(
            results["vent"], enclosure["tuning_hz"], enclosure["net_volume_l"],
            curves[0]["statistics"].get("max_port_air_speed_peak_ms"),
            elements["sd"] * vd * 1e-3 if vd else None, enclosure.get("port"))

    if params.get("alignment"):
        results["solved_alignments"] = _alignments(ts, params["alignment"])
    if enclosure.get("type") == "bandpass":
        results["loss_split"] = bass.loss_split(float((enclosure.get("front") or {}).get("ql", 10.0)))
    elif enclosure.get("type") != "sealed":
        results["loss_split"] = bass.loss_split(enclosure.get("ql", 10.0))

    limits = dict(params.get("limits") or {})
    if displacement and "xmax_mm" not in limits:
        limits["xmax_mm"] = displacement["xmax_mm"]
        limits["xmax_basis"] = f"{displacement['binding_limit']} ({displacement['standard']})"
        limits["xmax_definition"] = displacement["definition"]["definition"]
    if limits:
        results["linear_scaling_to_limits"] = _scaling(f, base, voltages[0], limits, stress_band)
    results["validity"] = _validity(ts, enclosure, f)
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Sealed, vented, aperiodic, passive-radiator or bandpass lumped bass model", NOTES, VALIDITY))
