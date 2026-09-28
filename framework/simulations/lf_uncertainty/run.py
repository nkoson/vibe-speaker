#!/usr/bin/env python3
"""Monte Carlo spread of the low-frequency box model over driver and build tolerances."""
import copy
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics  # noqa: E402

NAME = "lf_uncertainty"
VERSION = "1.2"
NOTES = [
    "Each draw perturbs the stated parameters independently with uniform distributions of the given half-width; the spreads are your assumptions, not measured production yield.",
    "Same linear lumped model as lf_box; percentiles describe the model's sensitivity to the inputs, nothing else.",
    "The defaults are sized to the reported method spread of the measurement, not to a catalogue tolerance: a perturbation tighter than the thing it perturbs gives false comfort, and one much wider is a sensitivity probe rather than a robustness figure.",
    "Mms is not drawn; it is derived from fs and Vas, so the Mms percentiles in the summary are what the fs and Vas spreads actually produce. Compare them with the 20 to 30 percent method spread before believing either.",
]

# Measured reality behind each default, so a reader can check the perturbation against the thing it
# perturbs rather than against a habit. See references/driver-selection.md section 6.
SPREAD_BASIS = {
    "fs_hz": "12 percent: the resonance shift a 25 percent compliance spread implies at constant mass. Compliance also moves "
             "with temperature and burn-in state, neither of which any datasheet reports.",
    "vas_l": "25 percent: the middle of the reported 20 to 30 percent spread between measurement methods, before "
             "sample-to-sample variation. Vas is directly proportional to compliance.",
    "qes": "10 percent. Qes follows Bl, Re and Mms; the widely reproduced impedance-sweep extraction chain for Qms and Qes "
           "was put to adversarial verification and refuted, so an extracted pair carries method uncertainty of its own.",
    "qms": "15 percent. Mechanical losses are the least repeatable of the small-signal parameters and drift with burn-in.",
    "re_ohm": "3 percent for the winding itself. A coil-temperature scenario is a separate, much larger effect: Re rises about "
              "0.39 percent per degree C, so a 40 K rise is 16 percent on its own.",
    "net_volume_l": "3 percent of the builder's net volume estimate: bracing, lining and driver displacement accounting.",
    "tuning_hz_abs": "1 Hz absolute on the realised tuning, which a duct cut to length and a leaky joint both move.",
    "ql_range": "5 to 20, Small's measured leakage range. His measured total QB in then-current commercial cabinets clustered "
                "at 5 to 10, which is where the QL = 7 design default comes from.",
    "added_mass_g_abs": "0 by default: a radiator mass is weighed, not estimated. Set it where the mass is a plan rather than a part.",
}

DEFAULT_SPREADS = {"fs_hz": .12, "qes": .10, "qms": .15, "vas_l": .25, "re_ohm": .03, "net_volume_l": .03,
                   "tuning_hz_abs": 1.0, "ql_range": [5.0, 20.0], "added_mass_g_abs": 0.0}


VALIDITY = [
    "A percentile band is a property of the assumed distributions. It is not a production yield and not a confidence interval on the physics.",
    "Uniform independent draws are an assumption of convenience: the real parameters are correlated, because fs, Vas and Mms are three views of two physical quantities.",
]


def summarize_samples(rows, percentiles):
    """Describe every outcome; cutoff percentiles exclude unresolved/censored draws explicitly."""
    summary = {}
    for key in rows[0]:
        if key.endswith("_bound"):
            continue
        bound_key = key[:-3] + "_bound" if key.endswith("_hz") else None
        is_cutoff = bound_key in rows[0] if bound_key else False
        values = [row[key] for row in rows
                  if isinstance(row[key], (int, float)) and np.isfinite(row[key])
                  and (not is_cutoff or row[bound_key] == "resolved")]
        if not values and not is_cutoff:
            continue
        item = {f"p{p}": float(np.percentile(values, p)) if values else None for p in percentiles}
        item.update(total_draws=len(rows), resolved_draws=len(values))
        if is_cutoff:
            counts = {bound: sum(row[bound_key] == bound for row in rows)
                      for bound in ("resolved", "left_censored", "no_sustained_pass")}
            item.update(bound_counts=counts, unresolved_draws=len(rows) - counts["resolved"],
                        percentile_basis="resolved cutoffs only; conditional, not an all-draw robustness claim")
        summary[key] = item
    return summary


def compute(params, base_dir):
    ts = dict(cli.require(params, "driver", "ts"))
    enclosure = dict(cli.require(params, "enclosure"))
    drive = params.get("drive") or {}
    voltage = float(drive.get("voltage_rms", 2.83))
    series_r = float(drive.get("series_resistance_ohm", 0.0))
    f = cli.frequency_grid(params.get("frequencies"), 10.0, 1500.0, 300)
    draws = int(params.get("draws", 128))
    if draws < 1:
        raise cli.InputError("draws must be at least 1")
    rng = np.random.default_rng(int(params.get("seed", 1)))
    spreads = dict(DEFAULT_SPREADS, **(params.get("spreads") or {}))
    analysis = params.get("analysis") or {}
    reference_band = tuple(analysis.get("reference_band_hz", [150.0, 300.0]))
    stress_band = tuple(analysis.get("stress_band_hz", [20.0, 300.0]))
    thresholds = analysis.get("cutoff_thresholds_db", [-6.0, -10.0])
    percentiles = analysis.get("percentiles", [5, 50, 95])
    stress = (f >= stress_band[0]) & (f <= stress_band[1])
    rows = []
    spl_stack = []
    nominal = acoustics.box_response(ts, enclosure, f, voltage, series_r)
    for _ in range(draws):
        d_ts = dict(ts)
        for key in ("fs_hz", "qes", "qms", "vas_l", "re_ohm"):
            d_ts[key] = ts[key] * (1 + rng.uniform(-spreads[key], spreads[key]))
        d_enc = copy.deepcopy(enclosure)
        d_enc["net_volume_l"] = enclosure["net_volume_l"] * (1 + rng.uniform(-spreads["net_volume_l"], spreads["net_volume_l"]))
        if enclosure.get("type", "vented") != "sealed":
            d_enc["tuning_hz"] = enclosure["tuning_hz"] + rng.uniform(-spreads["tuning_hz_abs"], spreads["tuning_hz_abs"])
        lo, hi = spreads["ql_range"]
        d_enc["ql"] = rng.uniform(lo, hi)
        if enclosure.get("type") == "passive_radiator" and spreads.get("added_mass_g_abs"):
            base_mass = enclosure.get("added_mass_g", acoustics.pr_added_mass(enclosure["net_volume_l"], enclosure["tuning_hz"], enclosure["radiator"])["required_added_mass_g"])
            d_enc["added_mass_g"] = max(0.0, base_mass + rng.uniform(-spreads["added_mass_g_abs"], spreads["added_mass_g_abs"]))
        r = acoustics.box_response(d_ts, d_enc, f, voltage, series_r)
        row = dict(fs_hz=d_ts["fs_hz"], qes=d_ts["qes"], qms=d_ts["qms"], vas_l=d_ts["vas_l"], re_ohm=d_ts["re_ohm"],
                   mms_g=r["elements"]["mms"] * 1000, qts=r["elements"]["qts"],
                   net_volume_l=d_enc["net_volume_l"], tuning_hz=d_enc.get("tuning_hz"), ql=d_enc["ql"],
                   max_excursion_peak_mm=float(r["excursion_peak_mm"][stress].max()),
                   impedance_min_ohm=float(np.abs(r["z_ohm"]).min()))
        for level in thresholds:
            value, bound, _ = acoustics.sustained_cutoff(f, r["spl_db"], level, reference_band)
            row[f"f{abs(int(level))}_hz"] = value
            row[f"f{abs(int(level))}_bound"] = bound
        if "port_air_speed_peak_ms" in r:
            row["max_port_air_speed_peak_ms"] = float(r["port_air_speed_peak_ms"][stress].max())
        if "radiator_excursion_peak_mm" in r:
            row["max_radiator_excursion_peak_mm"] = float(r["radiator_excursion_peak_mm"][stress].max())
        rows.append(row)
        spl_stack.append(r["spl_db"])
    spl_stack = np.array(spl_stack)
    summary = summarize_samples(rows, percentiles)
    derived = {}
    for key, published in (("mms_g", nominal["elements"]["mms"] * 1000), ("qts", nominal["elements"]["qts"])):
        values = np.array([row[key] for row in rows], float)
        derived[key] = dict(nominal=float(published), min=float(values.min()), max=float(values.max()),
                            half_width_fraction=float((values.max() - values.min()) / (2 * published)))
    return dict(f_hz=f, draws=draws, spreads_used=spreads, spread_basis=SPREAD_BASIS,
                derived_parameter_spread=dict(derived,
                                              note="Mms and Qts are not drawn; these are the spreads the drawn fs, Vas, Qes "
                                                   "and Qms produce. The reported method spread on Mms is 20 to 30 percent."),
                nominal_spl_db=nominal["spl_db"],
                spl_percentiles={f"p{p}": np.percentile(spl_stack, p, axis=0) for p in percentiles},
                summary=summary, samples=rows)


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Monte Carlo spread of the lumped bass model", NOTES, VALIDITY))
