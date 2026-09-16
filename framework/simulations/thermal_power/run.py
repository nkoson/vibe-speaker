#!/usr/bin/env python3
"""Two-body voice-coil thermal scenario: coil and magnet temperature, Re drift and the compression it costs."""
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, thermal  # noqa: E402

NAME = "thermal_power"
VERSION = "1.1"
NOTES = list(thermal.NOTES) + [
    "The two bodies are integrated as a coupled pair with the drive feeding back through Re(T), so a constant-voltage case delivers less power as it heats. The closed-form steady states and time constants are reported beside the integration.",
    "Compression is the level lost at constant drive voltage from the resistance change alone, 20 log10(Re_cold / Re_hot). It is not a measured compression figure and contains no nonlinear compression, which is instantaneous rather than thermal and cannot be separated from it by a single measurement duration.",
    "Feed the steady-state coil temperature back into lf_box as thermal.coil_temperature_c and into crossover_network as thermal.coil_temperatures_c to see what the hot load does to the alignment and to the filter corners.",
]
VALIDITY = [
    "A scenario over declared priors, not a prediction. Rtv, Rtm, Ctv and Ctm are almost never published, and the equivalent-mass check is the only sanity test available without a measurement.",
    "The priors come from the accelerated power-test protocol. Nothing here is calibrated against AES2-2012's two-hour-per-step endurance test, so no figure from this application is a rated power in the AES2 sense.",
    "Valid for the drive condition named. A continuous sine at the stress voltage is a probe; programme material distributes power across the spectrum and across time, which is why the power-handling standards specify shaped noise with a defined crest factor.",
    "The model neglects convection cooling, eddy-current heating of the pole pieces and heat distribution within each body. All three make it optimistic at long durations and at high level.",
]


def _integrate(params_t, re_cold, voltage, ambient_rise, seconds, constant_power_w=None):
    """Coupled two-body integration with the drive feeding back through Re(T)."""
    rtv, rtm = params_t["rtv_k_per_w"], params_t["rtm_k_per_w"]
    ctv, ctm = params_t["ctv_ws_per_k"], params_t["ctm_ws_per_k"]

    def power(tv):
        if constant_power_w is not None:
            return constant_power_w
        return voltage ** 2 / (re_cold * (1 + thermal.COPPER_COEFFICIENT_PER_C * (tv + ambient_rise)))

    def derivative(_, y):
        tv, tm = y
        flow = (tv - tm) / rtv
        return [(power(tv) - flow) / ctv, (flow - tm / rtm) / ctm]

    solution = solve_ivp(derivative, (0.0, float(seconds[-1])), [0.0, 0.0], t_eval=seconds, rtol=1e-6, atol=1e-8, max_step=max(seconds[-1] / 50, 1e-3))
    if not solution.success:
        raise cli.InputError(f"the thermal integration did not converge: {solution.message}")
    return solution.y[0], solution.y[1], np.array([power(tv) for tv in solution.y[0]])


def compute(params, base_dir):
    driver = cli.require(params, "driver")
    re_cold = cli.positive(driver.get("re_ohm"), "driver.re_ohm")
    ambient = float(params.get("ambient_c", 20.0))
    reference = float(params.get("reference_c", 20.0))
    ambient_rise = ambient - reference
    parameters = thermal.parameters(cli.require(params, "thermal"))
    time = params.get("time") or {}
    seconds = np.asarray(time.get("values_s") or np.linspace(0.0, float(time.get("duration_s", 1800.0)), int(time.get("points", 361))), float)
    if seconds[0] != 0:
        raise cli.InputError("time must start at 0 s")
    drive = params.get("drive") or {}
    cases = []
    voltages = [float(v) for v in drive.get("voltages_rms", [])]
    powers = [float(p) for p in drive.get("powers_w", [])]
    if not voltages and not powers:
        raise cli.InputError("drive needs voltages_rms or powers_w")
    for voltage in voltages:
        cases.append(("constant_voltage", voltage, None))
    for power_w in powers:
        cases.append(("constant_power", None, power_w))

    rows = []
    for kind, voltage, power_w in cases:
        coil, magnet, dissipated = _integrate(parameters, re_cold, voltage, ambient_rise, seconds, power_w)
        hot = thermal.resistance_at(re_cold, ambient + coil, reference)
        row = dict(drive=kind, voltage_rms=voltage, dissipated_power_w=dissipated,
                   seconds=seconds, coil_rise_k=coil, magnet_rise_k=magnet,
                   coil_temperature_c=ambient + coil, magnet_temperature_c=ambient + magnet,
                   re_ohm=hot, resistance_ratio=hot / re_cold,
                   compression_db=thermal.compression_db(re_cold, hot),
                   steady_state=dict(coil_rise_k=float(coil[-1]), magnet_rise_k=float(magnet[-1]),
                                     coil_temperature_c=float(ambient + coil[-1]),
                                     dissipated_power_w=float(dissipated[-1]), re_ohm=float(hot[-1]),
                                     resistance_ratio=float(hot[-1] / re_cold),
                                     compression_db=float(thermal.compression_db(re_cold, hot[-1])),
                                     settled=bool(seconds[-1] >= 4 * parameters["tau_m_s"]),
                                     settling_note=f"the long time constant is {parameters['tau_m_s']:.0f} s; a run shorter than "
                                                   f"about four of them has not reached steady state"))
        ratio = hot / re_cold
        crossed = np.flatnonzero(ratio >= thermal.ABORT_RESISTANCE_RATIO)
        row["abort_threshold"] = dict(resistance_ratio=thermal.ABORT_RESISTANCE_RATIO,
                                      rise_k=thermal.rise_at_resistance_ratio(thermal.ABORT_RESISTANCE_RATIO),
                                      reached=bool(len(crossed)),
                                      reached_at_s=float(seconds[crossed[0]]) if len(crossed) else None)
        row["working_window"] = dict(range_k=list(thermal.WORKING_RISE_RANGE_K),
                                     steady_state_inside=bool(thermal.WORKING_RISE_RANGE_K[0] <= coil[-1] <= thermal.WORKING_RISE_RANGE_K[1]))
        rows.append(row)

    results = dict(seconds=seconds, ambient_c=ambient, reference_c=reference, re_cold_ohm=re_cold,
                   thermal_parameters=parameters, cases=rows, test_protocol=thermal.PROTOCOL,
                   test_protocols=dict(thermal.PROTOCOLS, do_not_merge=thermal.PROTOCOLS_NOTE,
                                       priors_came_from=thermal.PRIOR_PROTOCOL),
                   feeds_into=dict(lf_box="thermal.coil_temperature_c", crossover_network="thermal.coil_temperatures_c",
                                   note="the steady-state coil temperature of the case you consider the design point"))
    if len(voltages) >= 2:
        span_db = 20 * np.log10(max(voltages) / min(voltages))
        loud = next(r for r in rows if r["voltage_rms"] == max(voltages))
        quiet = next(r for r in rows if r["voltage_rms"] == min(voltages))
        results["compression_over_drive_range"] = dict(
            drive_span_db=span_db,
            compression_db=loud["steady_state"]["compression_db"] - quiet["steady_state"]["compression_db"],
            calibration=thermal.PROTOCOL["calibration"],
            note="compare the two: a model that cannot reproduce the order of magnitude of a published compression figure "
                 "is a model whose priors are wrong, not a device that does not compress.")
    results["validity"] = dict(statements=list(VALIDITY), parameter_source=parameters["source"],
                               calibration_protocol=parameters["calibration_protocol"],
                               not_validated_against="AES2-2012 clause 6 endurance testing; that protocol answers what "
                                                     "the driver survives, not how fast its coil heats",
                               integrated_seconds=float(seconds[-1]),
                               long_time_constant_s=parameters["tau_m_s"], short_time_constant_s=parameters["tau_v_s"])
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Two-body voice-coil thermal scenario", NOTES, VALIDITY))
