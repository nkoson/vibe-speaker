#!/usr/bin/env python3
"""Bounded least-squares fit of passive crossover values toward a target coherent response."""
import copy
import itertools
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, networks, radiation  # noqa: E402

NAME = "crossover_fit"
VERSION = "1.1"
NOTES = [
    "Log-space bounded least squares on the marked element values; the target curve and weights are yours. The result is a local optimum inside the bounds within the evaluation budget, not a proof of the best crossover.",
    "The objective is the coherent on-axis sum (and optional extra angles) of the same geometry that whole_speaker evaluates, so the fitted values can be pasted into crossover_network and whole_speaker unchanged.",
    "The impedance term only penalizes input impedance below the stated figure; it does not enforce it.",
    "The compensation audit and the insertion loss are computed on the fitted values, so they describe the network the fit landed on and not the one it started from.",
]
VALIDITY = [
    "The result is a local optimum inside the stated bounds within the evaluation budget. It is not a proof that no better set of values exists, and a value resting on a bound means the topology or the bound is wrong.",
    "Everything the fit optimises is a model: datasheet phase, prior impedance models, no measurement. The values are a build starting point to be set after measurement.",
    "The objective is the coherent sum at the requested angles only. A low in-band residual with a step in the vertical map at the crossover is a worse loudspeaker than a slightly worse residual without one.",
]


def _variables(sections):
    rows = []
    for wi, section in enumerate(sections):
        for e in section.get("elements", []):
            for leaf in acoustics.iter_elements(e):
                fit = leaf.get("fit")
                if not fit:
                    continue
                key = "value_mh" if leaf["type"] == "L" else "value_uf" if leaf["type"] == "C" else "value_ohm"
                start = float(leaf[key])
                if fit is True:
                    lo, hi = start * .25, start * 4
                else:
                    lo, hi = float(fit.get("min", start * .25)), float(fit.get("max", start * 4))
                lo = max(lo, 1e-6)
                rows.append(dict(section=wi, leaf=leaf, key=key, start=start, min=lo, max=hi, id=leaf.get("id")))
    if not rows:
        raise cli.InputError("no element carries a fit record; mark values with \"fit\": true or {min, max}")
    return rows


def _apply(rows, x):
    for row, value in zip(rows, x):
        row["leaf"][row["key"]] = float(np.exp(value))


def _target(spec, f, base_dir, current_db, band):
    if isinstance(spec, dict) and "file" in spec:
        return cli.curve_from_reference(spec, base_dir, f, kind="real")
    if isinstance(spec, (int, float)):
        return np.full(len(f), float(spec))
    inside = (f >= band[0]) & (f <= band[1])
    return np.full(len(f), float(np.mean(current_db[inside])))


def compute(params, base_dir):
    system = copy.deepcopy(cli.require(params, "system"))
    sections_cfg = cli.require(params, "sections")
    system["sections"] = [dict(w, transfer=None) for w in system["sections"]]
    target = params.get("target") or {}
    band = tuple(target.get("band_hz", [100.0, 16000.0]))
    fit_f = cli.frequency_grid(params.get("fit_frequencies"), band[0] / 1.5, band[1] * 1.5, 240)
    full_f = cli.frequency_grid(params.get("frequencies"), 10.0, 40000.0, 800)
    observer = system.get("observer") or {}
    distance = float(observer.get("distance_m", 3.0))
    ear = float(observer.get("ear_height_m", 1.0))
    voltage = float(params.get("input_voltage_rms", 2.83))
    angles = target.get("vertical_angles_deg", [0.0])
    points = radiation.observation_points(distance, ear, angles, "V")
    geometry = radiation.load_sections(system, fit_f, base_dir)
    loads = [networks.section_load(w, fit_f, base_dir)[0] for w in sections_cfg]
    elements = [networks.with_wire(w) for w in sections_cfg]
    rows = _variables(sections_cfg)
    x0 = np.log([r["start"] for r in rows])
    bounds = (np.log([r["min"] for r in rows]), np.log([r["max"] for r in rows]))
    inside = (fit_f >= band[0]) & (fit_f <= band[1])
    weights = np.ones(len(fit_f))
    for w in target.get("weights", []):
        sel = (fit_f >= w["band_hz"][0]) & (fit_f <= w["band_hz"][1])
        weights[sel] = float(w["weight"])
    weights = weights * inside
    min_z = float(target.get("min_input_impedance_ohm", 0.0))
    z_weight = float(target.get("impedance_weight", 1.0))
    audible = (fit_f >= 20) & (fit_f <= 20000)
    scale = voltage / acoustics.P0
    budget = dict(calls=0, max=int(params.get("max_objective_calls", 4000)))

    def evaluate(x, polarity):
        _apply(rows, x)
        transfers = []
        zin = []
        for wi, section in enumerate(sections_cfg):
            h, z = networks.ladder_transfer(fit_f, loads[wi], elements[wi])
            transfers.append(h * polarity[wi])
            zin.append(z)
        total, _ = radiation.pressure(geometry, fit_f, points, distance, transfers)
        return acoustics.db(total * scale), 1 / np.sum([1 / z for z in zin], axis=0), transfers

    def residual_values(x, polarity, target_db):
        db_, zin, _ = evaluate(x, polarity)
        r = ((db_ - target_db[None, :]) * weights[None, :]).ravel()
        if min_z > 0:
            shortfall = np.maximum(min_z - np.abs(zin[audible]), 0.0) / min_z
            r = np.r_[r, z_weight * 10 * shortfall]
        return r

    def residual(x, polarity, target_db):
        budget["calls"] += 1
        if budget["calls"] > budget["max"]:
            raise RuntimeError("budget")
        return residual_values(x, polarity, target_db)

    start_db, _, _ = evaluate(x0, [float(w.get("polarity", 1)) for w in sections_cfg])
    target_db = _target(target.get("spl_db", "auto"), fit_f, base_dir, start_db[0], band)
    trials = int(params.get("polarity_trials", 1))
    base_polarity = [float(w.get("polarity", 1)) for w in sections_cfg]
    combos = [tuple(base_polarity)]
    if trials > 1 and len(sections_cfg) > 1:
        combos = [(base_polarity[0], *signs) for signs in itertools.product([1, -1], repeat=len(sections_cfg) - 1)][:trials]
    best = None
    attempts = []
    for polarity in combos:
        try:
            sol = least_squares(residual, x0, bounds=bounds, args=(list(polarity), target_db), max_nfev=int(params.get("max_nfev", 150)), x_scale="jac")
            x = sol.x
            cost = float(sol.cost)
            status = sol.message
        except RuntimeError:
            # the budget is gone, so score the start point without spending another call
            x = x0
            cost = float(np.sum(residual_values(x0, list(polarity), target_db) ** 2) / 2)
            status = "objective-call budget exhausted"
        db_, zin, _ = evaluate(x, list(polarity))
        rms = float(np.sqrt(np.mean(((db_[0] - target_db) ** 2)[inside])))
        attempts.append(dict(polarity=list(polarity), cost=cost, rms_error_in_band_db=rms, status=status, objective_calls=budget["calls"]))
        if best is None or cost < best["cost"]:
            best = dict(x=x, polarity=list(polarity), cost=cost)
    _apply(rows, best["x"])
    fitted_values = [dict(id=r["id"], section=sections_cfg[r["section"]].get("name"), type=r["leaf"]["type"], key=r["key"], start=r["start"],
                          fitted=float(r["leaf"][r["key"]]), min=r["min"], max=r["max"],
                          at_bound=bool(abs(np.log(r["leaf"][r["key"]] / r["min"])) < 1e-3 or abs(np.log(r["leaf"][r["key"]] / r["max"])) < 1e-3)) for r in rows]
    fitted_sections = copy.deepcopy(sections_cfg)
    for section, sign in zip(fitted_sections, best["polarity"]):
        section["polarity"] = sign
        for e in section.get("elements", []):
            for leaf in acoustics.iter_elements(e):
                leaf.pop("fit", None)
    for section, src in zip(fitted_sections, sections_cfg):
        for e_new, e_old in zip(section.get("elements", []), src.get("elements", [])):
            for l_new, l_old in zip(acoustics.iter_elements(e_new), acoustics.iter_elements(e_old)):
                for key in ("value_mh", "value_uf", "value_ohm"):
                    if key in l_old:
                        l_new[key] = l_old[key]
    geometry_full = radiation.load_sections(system, full_f, base_dir)
    loads_full = [networks.section_load(w, full_f, base_dir)[0] for w in sections_cfg]
    transfers = []
    zin = []
    for wi, section in enumerate(sections_cfg):
        h, z = networks.ladder_transfer(full_f, loads_full[wi], elements[wi])
        transfers.append(h * best["polarity"][wi])
        zin.append(z)
    total_z = 1 / np.sum([1 / z for z in zin], axis=0)
    total, parts = radiation.pressure(geometry_full, full_f, radiation.observation_points(distance, ear, [0.0], "V"), distance, transfers)
    on_axis = acoustics.db(total[0] * scale)
    audits = []
    for wi, section in enumerate(sections_cfg):
        compensated, declared = networks.compensated_load(full_f, loads_full[wi], elements[wi])
        audit = networks.compensation_audit(full_f, loads_full[wi], compensated, section.get("compensation_audit"), declared)
        row = dict(name=section.get("name"),
                   insertion_loss=networks.insertion_loss(full_f, loads_full[wi], elements[wi], transfers[wi], section.get("passband_hz")))
        if audit:
            row["compensation_audit"] = audit
        audits.append(row)
    start_curve = start_db[0]
    aud = (full_f >= 20) & (full_f <= 20000)
    return dict(f_hz=full_f, fit_f_hz=fit_f, target_spl_db=target_db, band_hz=list(band), start_spl_db=start_curve,
                attempts=attempts, selected_polarity=best["polarity"], fitted_values=fitted_values, fitted_sections=fitted_sections,
                on_axis_spl_db=on_axis, sections=[dict(name=w.get("name"), transfer=transfers[i], spl_db=acoustics.db(parts[i, 0] * scale)) for i, w in enumerate(sections_cfg)],
                fitted_network_audit=audits, input_z_ohm=total_z,
                statistics=dict(rms_error_in_band_db=min(a["rms_error_in_band_db"] for a in attempts),
                                ripple_in_band_db=float(np.ptp(on_axis[(full_f >= band[0]) & (full_f <= band[1])])),
                                input_z_min_ohm=float(np.abs(total_z[aud]).min()), input_z_min_hz=float(full_f[aud][np.argmin(np.abs(total_z[aud]))]),
                                objective_calls=budget["calls"], variables=len(rows), values_at_bound=[v["id"] for v in fitted_values if v["at_bound"]]))


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Bounded fit of crossover values to a target response", NOTES, VALIDITY))
