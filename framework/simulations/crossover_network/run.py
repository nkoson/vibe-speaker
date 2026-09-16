#!/usr/bin/env python3
"""Passive crossover as loaded series/shunt ladders: transfer, impedance, component stress and tolerance spread."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, networks, thermal  # noqa: E402

NAME = "crossover_network"
VERSION = "1.4"
NOTES = [
    "Exact complex series/shunt ladder recursion per section against the supplied load impedance; sections are parallel at the input terminals.",
    "Coil DCR defaults to 0.10 + 0.16 sqrt(L_mH) ohm and capacitor ESR to 0.01 ohm when not stated; replace them with the chosen parts' data.",
    "Acoustic transfer is terminal transfer times the section's free-field pressure per volt; geometry, directivity and baffle are applied by whole_speaker.",
    "Tolerance draws scale each leaf element independently with uniform spreads; the envelope is a sample, not a worst case.",
    "A coil-temperature scenario adds the resistance rise of the driver's own voice coil, Re (1 + 0.0039 (T - T0)) - Re, to its load impedance and recomputes. The network's own coil DCR and the motional part of the impedance are left cold, so the scenario is the first-order load effect and not a hot-system model.",
    "A hot driver takes a larger share of the terminal voltage, so the electrical transfer usually rises with temperature while the driver's own sensitivity falls with Bl/Re. The two effects are reported separately: this transfer change, and lf_box's thermal_scenario.compression_db. Read them together, not apart.",
    "Insertion loss is reported against the same ladder with coil DCR, capacitor ESR and the wire loop removed, which separates what the real parts cost from the attenuation the topology was asked for.",
    "Stress figures are per PHYSICAL PART. A composite element's voltage and current are distributed to its members - a series group shares current and divides voltage, a parallel group shares voltage and divides current - so each resistor, capacitor and coil of a bank, a Zobel or a notch carries its own dissipation and its own current, and the leaf powers sum to the group's power exactly. components[] is therefore per part and component_curves[] per element group.",
    "The efficiency block divides the real power the amplifier delivers between the drivers and the network, pink weighted so the share is not dominated by the top of the band. It is a reading of the network that was designed and not a target: what share is acceptable follows from the level budget, the pad depths and the compensation audit, which is why those figures are reported beside it.",
    "Component values are treated as linear at every level. Core saturation and its distortion are not modelled, and for cored coils no saturation figure exists to model: the supplier states it has not measured power handling or saturation points at all. The rating is therefore reported as 'not published', the core's failure mode is named where the core is known - ferrite saturates earlier and collapses abruptly, powder later and more softly - and the fallback is the vendor's frequency rule, ferromagnetic cores below about 1.2 kHz and air cores above.",
]
VALIDITY = [
    "Lumped elements hold while every part and every wire run is short compared with a wavelength; at 20 kHz that is 17 mm per degree of phase, so board layout, not the ladder, is the limit at the top of the band.",
    "The ladder is exact for the load it is given. A datasheet impedance prior is a prior, not a measurement, and a fit against one is only as good as it.",
    "No source consulted states the decibel error between a simulated and a measured crossover transfer; final values are set after measurement.",
]


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 10.0, 40000.0, 800)
    voltage = float(params.get("input_voltage_rms", 2.83))
    sections = cli.require(params, "sections")
    tol = params.get("tolerances") or {}
    draws = int(tol.get("draws", 0))
    rng = np.random.default_rng(int(tol.get("seed", 9919)))
    tol_defaults = {"C": float(tol.get("C", 0.05)), "L": float(tol.get("L", 0.03)), "R": float(tol.get("R", 0.02))}
    scenarios = params.get("thermal") or {}
    temperatures = [float(x) for x in (scenarios.get("coil_temperatures_c") or [])]
    reference_c = float(scenarios.get("reference_c", 20.0))
    coefficient = float(scenarios.get("copper_coefficient_per_c", thermal.COPPER_COEFFICIENT_PER_C))
    rows = []
    branch_z = []
    for section in sections:
        load, pressure = networks.section_load(section, f, base_dir)
        elements = networks.with_wire(section)
        polarity = float(section.get("polarity", 1))
        state = networks.ladder_state(f, load, elements, None, voltage)
        transfer = state["terminal"] / voltage * polarity
        row = dict(name=section.get("name"), polarity=polarity, load_z_ohm=load, transfer=transfer, branch_input_z_ohm=state["input_z"],
                   load_power_w=np.abs(state["load_current"]) ** 2 * load.real, terminal_voltage_rms=np.abs(state["terminal"]),
                   components=networks.leaf_summary(elements, state["states"], f),
                   inductor_ratings=networks.part_ratings(elements, state["states"], f, section.get("passband_hz")),
                   insertion_loss=networks.insertion_loss(f, load, elements, transfer, section.get("passband_hz")),
                   component_curves=[dict(id=st["id"], voltage_rms=np.abs(st["voltage"]), current_rms_a=np.abs(st["current"]), dissipation_w=st["dissipation_w"]) for st in state["states"]])
        compensated, declared = networks.compensated_load(f, load, elements)
        row["compensated_load_z_ohm"] = compensated
        audit = networks.compensation_audit(f, load, compensated, section.get("compensation_audit"), declared)
        if audit:
            row["compensation_audit"] = audit
        if temperatures and section.get("re_ohm"):
            cold = float(section["re_ohm"])
            cases = []
            for temperature in temperatures:
                hot = thermal.resistance_at(cold, temperature, reference_c, coefficient)
                hot_load = load + (hot - cold)
                hot_state = networks.ladder_transfer(f, hot_load, elements)
                cases.append(dict(coil_temperature_c=temperature, re_cold_ohm=cold, re_hot_ohm=hot,
                                  resistance_ratio=hot / cold, coil_rise_k=temperature - reference_c,
                                  transfer=hot_state[0] * polarity, branch_input_z_ohm=hot_state[1],
                                  transfer_change_db=acoustics.db(hot_state[0]) - acoustics.db(state["terminal"] / voltage)))
            row["coil_temperature_cases"] = cases
        if pressure is not None:
            row["acoustic_pressure_per_input_volt_pa"] = transfer * pressure
            row["acoustic_spl_db_at_input_voltage"] = acoustics.db(transfer * pressure * voltage / acoustics.P0)
        if draws:
            mags = []
            zmins = []
            for _ in range(draws):
                st = networks.ladder_state(f, load, elements, networks.draw_scale(elements, rng, tol_defaults), voltage)
                mags.append(acoustics.db(st["terminal"] / voltage))
                zmins.append(float(np.abs(st["input_z"]).min()))
            mags = np.array(mags)
            row["tolerance"] = dict(draws=draws, transfer_db_p5=np.percentile(mags, 5, axis=0), transfer_db_p50=np.percentile(mags, 50, axis=0),
                                    transfer_db_p95=np.percentile(mags, 95, axis=0), branch_z_min_ohm_p5=float(np.percentile(zmins, 5)),
                                    branch_z_min_ohm_p95=float(np.percentile(zmins, 95)))
        rows.append(row)
        branch_z.append(state["input_z"])
    total_z = 1 / np.sum([1 / z for z in branch_z], axis=0)
    zmag = np.abs(total_z)
    audible = (f >= 20) & (f <= 20000)
    dissipation = sum(sum(c["dissipation_w"] for c in row["component_curves"]) for row in rows)
    # Real power into each branch at the common terminal voltage, and the share of the total it takes.
    branch_power = [voltage ** 2 * np.real(1 / z) for z in branch_z]
    total_power = sum(branch_power)
    split_band = tuple(params.get("power_split_band_hz", [20.0, 20000.0]))
    split = (f >= split_band[0]) & (f <= split_band[1])
    power_split = dict(
        band_hz=list(split_band),
        total_input_power_w=total_power,
        sections=[dict(name=row["name"], input_power_w=p, fraction_of_input=p / total_power,
                       band_mean_fraction=float(np.mean((p / total_power)[split])),
                       band_energy_fraction=float(np.sum(p[split]) / np.sum(total_power[split])))
                  for row, p in zip(rows, branch_power)],
        note="computed at a flat drive voltage, which is not programme material. For sizing per-branch current ratings the "
             "equal-power frequency between the low band and everything above it lies between 250 and 350 Hz on typical "
             "programme; that figure belongs to the programme, not to this network.")
    to_drivers = sum(row["load_power_w"] for row in rows)
    efficiency = networks.power_efficiency(f, total_power, to_drivers, dissipation,
                                           sections=list(zip(sections, [row["load_power_w"] for row in rows])),
                                           band_hz=split_band)
    parts = networks.part_counts(rows)
    results = dict(f_hz=f, input_voltage_rms=voltage, sections=rows, input_z_ohm=total_z, input_current_rms_a=voltage / zmag,
                   total_component_dissipation_w=dissipation, total_driver_power_w=to_drivers, power_split=power_split,
                   efficiency=efficiency, parts=parts,
                   statistics=dict(input_z_min_ohm=float(zmag[audible].min()), input_z_min_hz=float(f[audible][np.argmin(zmag[audible])]),
                                   input_z_max_ohm=float(zmag[audible].max()), input_z_max_hz=float(f[audible][np.argmax(zmag[audible])]),
                                   max_total_component_dissipation_w=float(dissipation.max()),
                                   to_drivers_fraction=efficiency["to_drivers_fraction"], network_loss_db=efficiency["loss_db"],
                                   part_count=parts["total"],
                                   component_count=int(sum(len(row["components"]) for row in rows))))
    if all("acoustic_pressure_per_input_volt_pa" in row for row in rows):
        colocated = sum(row["acoustic_pressure_per_input_volt_pa"] for row in rows)
        results["colocated_sum_spl_db_at_input_voltage"] = acoustics.db(colocated * voltage / acoustics.P0)
        results["statistics"]["colocated_sum_note"] = "coherent sum with all sections at one point; use whole_speaker for positions, baffle and directivity"
    return results


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Loaded passive crossover ladders", NOTES, VALIDITY))
