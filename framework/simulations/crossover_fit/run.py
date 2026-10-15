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
VERSION = "1.2"
NOTES = [
    "Log-space bounded least squares on the marked element values; the target curve and weights are yours. The result is a local optimum inside the bounds within the evaluation budget, not a proof of the best crossover.",
    "The objective is the coherent on-axis sum (and optional extra angles) of the same geometry that whole_speaker evaluates, so the fitted values can be pasted into crossover_network and whole_speaker unchanged.",
    "The impedance term only penalizes input impedance below the stated figure; it does not enforce it.",
    "The compensation audit and the insertion loss are computed on the fitted values, so they describe the network the fit landed on and not the one it started from.",
    "The ablation pass removes one element at a time and refits the rest, so what each element is worth is measured against this design rather than assumed from its name. Removing a series element shorts it and removing a shunt element opens it, which is what leaving the part out of the build does. It reports the cost of the removal; whether that cost is worth the part is the designer's judgement and nothing here decides it.",
    "Quantization snaps each fitted value to the nearest value in the stock lists you supply and reports what the snap cost, with the network ready to paste. Values are not constrained to stock during the search, because a fit pinned to a grid hides which direction the value wanted to move.",
]
VALIDITY = [
    "The result is a local optimum inside the stated bounds within the evaluation budget. It is not a proof that no better set of values exists, and a value resting on a bound means the topology or the bound is wrong.",
    "Everything the fit optimises is a model: datasheet phase, prior impedance models, no measurement. Final stock selection also considers tolerance, protection, geometry and source-model sensitivity.",
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


def _value_key(kind):
    return "value_mh" if kind == "L" else "value_uf" if kind == "C" else "value_ohm"


def _stock_for(leaf, stock):
    """The purchasable values for one leaf: its own list if it has one, else the list for its type."""
    own = leaf.get("stock")
    if own:
        return [float(v) for v in own]
    shared = (stock or {}).get(leaf["type"])
    return [float(v) for v in shared] if shared else []


def _snap(value, choices):
    """Nearest stock value in log space, which treats a proportional error the same at every size."""
    return min(choices, key=lambda c: abs(np.log(max(c, 1e-12) / max(value, 1e-12))))


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

    def evaluate(x, polarity, rows_=None, elements_=None):
        rows_ = rows if rows_ is None else rows_
        elements_ = elements if elements_ is None else elements_
        _apply(rows_, x)
        transfers = []
        zin = []
        for wi in range(len(elements_)):
            h, z = networks.ladder_transfer(fit_f, loads[wi], elements_[wi])
            transfers.append(h * polarity[wi])
            zin.append(z)
        total, _ = radiation.pressure(geometry, fit_f, points, distance, transfers)
        return acoustics.db(total * scale), 1 / np.sum([1 / z for z in zin], axis=0), transfers

    def residual_values(x, polarity, target_db, rows_=None, elements_=None):
        db_, zin, _ = evaluate(x, polarity, rows_, elements_)
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

    def refit(variant, polarity, target_db, max_nfev, max_calls):
        """Fit one variant network under its own call budget; returns its in-band error and curves."""
        variant_elements = [networks.with_wire(w) for w in variant]
        try:
            variant_rows = _variables(variant)
        except cli.InputError:
            variant_rows = []
        spent = dict(calls=0)

        def variant_residual(x):
            spent["calls"] += 1
            if spent["calls"] > max_calls:
                raise RuntimeError("budget")
            return residual_values(x, polarity, target_db, variant_rows, variant_elements)

        status = "no free value left to fit; evaluated as given"
        x = np.log([r["start"] for r in variant_rows]) if variant_rows else np.zeros(0)
        if variant_rows:
            lo = np.log([r["min"] for r in variant_rows])
            hi = np.log([r["max"] for r in variant_rows])
            try:
                sol = least_squares(variant_residual, x, bounds=(lo, hi), max_nfev=max_nfev, x_scale="jac")
                x, status = sol.x, sol.message
            except RuntimeError:
                status = "objective-call budget exhausted"
        db_, zin, _ = evaluate(x, polarity, variant_rows, variant_elements)
        return dict(rms_error_in_band_db=float(np.sqrt(np.mean(((db_[0] - target_db) ** 2)[inside]))),
                    ripple_in_band_db=float(np.ptp(db_[0][inside])),
                    input_z_min_ohm=float(np.abs(zin[audible]).min()),
                    objective_calls=spent["calls"], status=status)

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
    # What the fitted network costs to run and to buy, from the same values the curves came from.
    states = [networks.ladder_state(full_f, loads_full[wi], elements[wi], None, voltage) for wi in range(len(sections_cfg))]
    driver_power = [np.abs(st["load_current"]) ** 2 * loads_full[wi].real for wi, st in enumerate(states)]
    component_power = sum(sum(leaf["dissipation_w"] for leaf in st["states"]) for st in states)
    branch_power = sum(voltage ** 2 * np.real(1 / st["input_z"]) for st in states)
    part_rows = [dict(name=w.get("name"), components=networks.leaf_summary(elements[wi], states[wi]["states"], full_f))
                 for wi, w in enumerate(sections_cfg)]
    fitted_efficiency = networks.power_efficiency(full_f, branch_power, sum(driver_power), component_power,
                                                  sections=list(zip(sections_cfg, driver_power)))
    fitted_parts = networks.part_counts(part_rows)

    ablation = None
    if params.get("ablation"):
        spec = params["ablation"] if isinstance(params["ablation"], dict) else {}
        only = set(spec.get("elements") or [])
        nfev_each = int(spec.get("max_nfev", 60))
        # A finite-difference jacobian costs one call per free value, so the call budget has to grow with them.
        calls_each = int(spec.get("max_objective_calls", 0)) or nfev_each * (len(rows) + 2)
        db_ref, z_ref, _ = evaluate(best["x"], best["polarity"])
        reference = dict(rms_error_in_band_db=float(np.sqrt(np.mean(((db_ref[0] - target_db) ** 2)[inside]))),
                         ripple_in_band_db=float(np.ptp(db_ref[0][inside])),
                         input_z_min_ohm=float(np.abs(z_ref[audible]).min()))
        trials = []
        for wi, section in enumerate(sections_cfg):
            for ei, element in enumerate(section.get("elements", [])):
                eid = element.get("id") or f"{section.get('name')}#{ei}"
                if only and eid not in only:
                    continue
                variant = copy.deepcopy(sections_cfg)
                removed = variant[wi]["elements"].pop(ei)
                out = refit(variant, best["polarity"], target_db, nfev_each, calls_each)
                trials.append(dict(id=eid, section=section.get("name"), position=element.get("position"),
                                   type=element.get("type"), role=element.get("role"),
                                   parts_removed=len(list(acoustics.iter_elements(removed))),
                                   rms_error_in_band_db=out["rms_error_in_band_db"],
                                   delta_rms_db=out["rms_error_in_band_db"] - reference["rms_error_in_band_db"],
                                   ripple_in_band_db=out["ripple_in_band_db"], input_z_min_ohm=out["input_z_min_ohm"],
                                   objective_calls=out["objective_calls"], status=out["status"]))
        trials.sort(key=lambda t: t["delta_rms_db"])
        _apply(rows, best["x"])
        ablation = dict(reference=reference, trials=trials,
                        note="each trial removes one element - a series element shorted, a shunt element opened - and "
                             "refits every remaining free value, so delta_rms_db is what the rest of the network cannot "
                             "recover without that part. A small delta says the element is doing little for the on-axis "
                             "sum in this design; it says nothing about what it does for impedance, stress, off-axis "
                             "behaviour or robustness, which are read from input_z_min_ohm here and from crossover_network "
                             "and whole_speaker on the variant you decide to try. Nothing is removed for you.")

    quantization = None
    if any(_stock_for(r["leaf"], params.get("stock") or {}) for r in rows):
        stock = params.get("stock") or {}
        variant = copy.deepcopy(sections_cfg)
        variant_rows = _variables(variant)
        snapped = []
        values = []
        for source, destination in zip(rows, variant_rows):
            choices = _stock_for(source["leaf"], stock)
            fitted = float(source["leaf"][source["key"]])
            value = _snap(fitted, choices) if choices else fitted
            destination["leaf"][destination["key"]] = value
            values.append(value)
            snapped.append(dict(id=source["id"], section=sections_cfg[source["section"]].get("name"),
                                type=source["leaf"]["type"], key=source["key"], fitted=fitted, stock_value=value,
                                error_percent=100.0 * (value - fitted) / fitted, from_stock=bool(choices)))
        variant_elements = [networks.with_wire(w) for w in variant]
        db_q, z_q, _ = evaluate(np.log(values), best["polarity"], variant_rows, variant_elements)
        quantized_sections = copy.deepcopy(variant)
        for section in quantized_sections:
            for e in section.get("elements", []):
                for leaf in acoustics.iter_elements(e):
                    leaf.pop("fit", None)
                    leaf.pop("stock", None)
        _apply(rows, best["x"])
        quantization = dict(values=snapped, sections=quantized_sections,
                            rms_error_in_band_db=float(np.sqrt(np.mean(((db_q[0] - target_db) ** 2)[inside]))),
                            ripple_in_band_db=float(np.ptp(db_q[0][inside])),
                            input_z_min_ohm=float(np.abs(z_q[audible]).min()),
                            note="the fitted values snapped to the nearest stock value in log space, evaluated as a whole. "
                                 "A value with from_stock false had no list to snap to. Rerun crossover_network on these "
                                 "sections with the real DCR and ESR before treating any of it as the design.")

    start_curve = start_db[0]
    aud = (full_f >= 20) & (full_f <= 20000)
    return dict(f_hz=full_f, fit_f_hz=fit_f, target_spl_db=target_db, band_hz=list(band), start_spl_db=start_curve,
                ablation=ablation, quantization=quantization, fitted_efficiency=fitted_efficiency, fitted_parts=fitted_parts,
                attempts=attempts, selected_polarity=best["polarity"], fitted_values=fitted_values, fitted_sections=fitted_sections,
                on_axis_spl_db=on_axis, sections=[dict(name=w.get("name"), transfer=transfers[i], spl_db=acoustics.db(parts[i, 0] * scale)) for i, w in enumerate(sections_cfg)],
                fitted_network_audit=audits, input_z_ohm=total_z,
                statistics=dict(rms_error_in_band_db=min(a["rms_error_in_band_db"] for a in attempts),
                                ripple_in_band_db=float(np.ptp(on_axis[(full_f >= band[0]) & (full_f <= band[1])])),
                                input_z_min_ohm=float(np.abs(total_z[aud]).min()), input_z_min_hz=float(full_f[aud][np.argmin(np.abs(total_z[aud]))]),
                                objective_calls=budget["calls"], variables=len(rows), values_at_bound=[v["id"] for v in fitted_values if v["at_bound"]]))


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Bounded fit of crossover values to a target response", NOTES, VALIDITY))
