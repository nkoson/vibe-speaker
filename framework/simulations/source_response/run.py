#!/usr/bin/env python3
"""Acoustic source model of one section: complex pressure per volt at 1 m and load impedance on a common grid."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics  # noqa: E402

NAME = "source_response"
VERSION = "1.5"
NOTES = [
    "Pressure per volt is the on-axis free-field figure at 1 m for the source alone; directivity, baffle and position are applied later by whole_speaker.",
    "A published curve is turned into a minimum-phase response; the phase is a reconstruction, not a measurement. A bandwidth prior is a flat level with declared roll-offs.",
    "A cone section built from lf_box output takes its bass from the box model; an optional published curve shapes the response above the blend band, multiplying the model's own shape or replacing it.",
    "Impedance comes from the declared model; compression driver and dome impedance models are priors unless a measured curve is supplied.",
    "An imported gated measurement is valid only above about 1 / t_gate. State acoustic.gate_ms with it and the validity block reports that bound; below it the data is not merely noisy, it is absent and was replaced by whatever the near-field splice or the roll-off prior put there.",
]
VALIDITY = [
    "A bandwidth prior is a declared shape, not a response. A datasheet curve is a reading of a printed graph and carries the reading uncertainty of that.",
    "Minimum-phase reconstruction assumes the driver is minimum phase, which a horn-loaded or multi-way source is not; the phase is a reconstruction and never a measurement.",
    "Near-field piston scaling holds while ka << 1, which is safe below roughly 200 Hz for any practical membrane. Practice often needs an extra 1 to 2 dB of scaling to make a spliced pair meet, which is the real uncertainty of any absolute sensitivity derived that way.",
]


def _published_curve(record, f, base_dir):
    points = np.asarray(record["points"], float)
    if points.ndim != 2 or points.shape[1] != 2 or np.any(np.diff(points[:, 0]) <= 0):
        raise cli.InputError("published points must be [[hz, spl_db], ...] with increasing frequency")
    level = points[:, 1] + 20 * np.log10(2.83 / float(record.get("voltage_rms", 2.83))) + 20 * np.log10(float(record.get("distance_m", 1.0)))
    return acoustics.minimum_phase(f, points[:, 0], level, float(record.get("lower_rolloff_db_oct", 12.0)), float(record.get("upper_rolloff_db_oct", 24.0)))


def _own_shape_record(f, pressure):
    """The model's own magnitude across the whole grid, so it can be divided out of a published shape."""
    db = 20 * np.log10(np.maximum(np.abs(pressure), 1e-30))
    return {"points": [[float(x), float(y)] for x, y in zip(f, db)]}


def _shape_above(record, f, blend_hz):
    """Published shape relative to its own level in the blend band; unity below the blend."""
    points = np.asarray(record["points"], float)
    fp, dp = points[:, 0], points[:, 1]
    low, high = blend_hz
    inside = (fp >= high) & (fp <= high * 2.5)
    base = float(np.median(dp[inside])) if np.count_nonzero(inside) >= 2 else float(np.interp(np.log(high), np.log(fp), dp))
    weight = np.clip((np.log(fp) - np.log(low)) / (np.log(high) - np.log(low)), 0., 1.)
    shape = (dp - base) * weight
    if fp[0] > low:
        fp = np.r_[low / 2, fp]
        shape = np.r_[0., shape]
    return acoustics.minimum_phase(f, fp, shape, 0.0, float(record.get("upper_rolloff_db_oct", 24.0)))


def _box_pressure(model, f, base_dir, outlet=False):
    ref = dict(model["reference"])
    ref.setdefault("frequency_path", "results.f_hz")
    ref.setdefault("path", "results.curves.0.pressure_pa")
    document = cli.load_json(cli.resolve_path(ref["file"], base_dir))
    parts = ref["path"].split(".")
    if len(parts) != 4 or parts[:2] != ["results", "curves"] or not parts[2].isdigit():
        if model.get("voltage_basis", "source") != "source":
            raise cli.InputError("driver_terminal normalization requires results.curves.<index>.<pressure field>")
        if outlet:
            return None, ""
        voltage = cli.positive(model.get("voltage_rms", 2.83), "acoustic.voltage_rms")
        return cli.curve_from_reference(ref, base_dir, f) / voltage, "imported lf_box pressure per declared source volt; drive provenance not available"
    curve_path = ".".join(parts[:3])
    curve = cli.dotted(document, curve_path)
    if outlet:
        if "outlet_pressure_pa" not in curve:
            return None, ""
        ref["path"] = curve_path + ".outlet_pressure_pa"
    voltage = cli.positive(curve["voltage_rms"], "lf_box curve voltage_rms")
    p = cli.curve_from_reference(ref, base_dir, f) / voltage
    voltage_basis = model.get("voltage_basis", "source")
    if voltage_basis not in ("source", "driver_terminal"):
        raise cli.InputError("acoustic.voltage_basis must be source or driver_terminal")
    inputs = document.get("inputs") or {}
    series_r = cli.positive((inputs.get("drive") or {}).get("series_resistance_ohm", 0.0),
                            "lf_box drive.series_resistance_ohm", zero=True)
    basis = "lf_box pressure per source volt"
    if voltage_basis == "driver_terminal":
        if inputs.get("terminal_transfer"):
            raise cli.InputError("driver_terminal source needs an lf_box run without terminal_transfer; apply the network downstream")
        zref = dict(ref, path=curve_path + ".z_ohm")
        z = cli.curve_from_reference(zref, base_dir, f)
        if np.any(np.abs(z) < 1e-15):
            raise cli.InputError("cannot normalize lf_box pressure at zero driver impedance")
        p = p * (z + series_r) / z
        basis = "lf_box pressure per driver-terminal volt; external series resistance removed from acoustic transfer"
    elif series_r or inputs.get("terminal_transfer"):
        basis += "; includes external drive loss: do not apply that resistance or transfer again downstream"
    return p, basis


def _pressure(params, f, base_dir):
    model = cli.require(params, "acoustic")
    kind = cli.require(model, "kind", label="acoustic")
    if kind == "bandwidth_prior":
        level = float(cli.require(model, "sensitivity_db_2v83_1m", label="acoustic"))
        p = acoustics.P0 * 10 ** (level / 20) / 2.83 * acoustics.bandwidth_shape(f, model.get("lower_hz"), model.get("upper_hz"))
        return p, f"flat {level:g} dB at 2.83 V / 1 m with declared bandwidth roll-offs"
    if kind == "published_curve":
        p = acoustics.P0 * _published_curve(model, f, base_dir) / 2.83
        return p, "minimum-phase reconstruction of the published magnitude curve"
    if kind == "lf_box":
        mode = str((model.get("published_shape") or {}).get("mode", "multiply"))
        if mode not in ("multiply", "replace"):
            raise cli.InputError("published_shape mode must be 'multiply' or 'replace'")
        p, basis = _box_pressure(model, f, base_dir)
        if model.get("published_shape"):
            record = dict(model["published_shape"])
            if record.get("fixture_response"):
                points = np.asarray(record["points"], float)
                fixture = cli.curve_from_reference(
                    dict(extrapolation="error", **record["fixture_response"]),
                    base_dir, points[:, 0])
                if np.any(abs(fixture) < 1e-12):
                    raise cli.InputError("published-shape fixture response contains a null")
                record["points"] = np.c_[points[:, 0], points[:, 1]-acoustics.db(fixture)].tolist()
                basis += "; declared fixture magnitude removed before shape normalization and phase reconstruction"
            blend = tuple(model.get("blend_band_hz", [150.0, 300.0]))
            shape = _shape_above(record, f, blend)
            if mode == "replace":
                shape = shape / _shape_above(_own_shape_record(f, p), f, blend)
                basis += " with its own shape above the blend band replaced by the published curve"
            else:
                basis += " multiplied above the blend band by the published shape"
            p = p * shape
        return p, basis
    if kind == "simulation":
        ref = dict(model["reference"])
        ref.setdefault("path", "results.pressure_per_volt_pa")
        upstream=cli.load_json(cli.resolve_path(ref["file"],base_dir))
        origin=upstream.get("simulation","external")
        return cli.curve_from_reference(ref, base_dir, f), f"canonical source imported from {origin}; normalization follows its source contract"
    if kind == "measured":
        fr = np.asarray(model["frequency_hz"], float)
        if "spl_db" in model:
            mag = acoustics.P0 * 10 ** (np.asarray(model["spl_db"], float) / 20)
            if "phase_deg" in model:
                z = mag * np.exp(1j * np.deg2rad(np.asarray(model["phase_deg"], float)))
                basis = "imported complex response with supplied phase"
            elif model.get("phase_assumption", "minimum_phase") == "minimum_phase":
                z = acoustics.minimum_phase(fr, fr, np.asarray(model["spl_db"], float)) * acoustics.P0
                basis = "magnitude-only input with reconstructed minimum phase"
            elif model.get("phase_assumption") == "zero":
                z = mag.astype(complex)
                basis = "magnitude-only input with explicitly assumed zero phase"
            else:
                raise cli.InputError("phase_assumption needs minimum_phase or zero")
        else:
            z = np.asarray(model["real_pa"], float) + 1j * np.asarray(model["imag_pa"], float)
            basis = "imported complex response with supplied real/imaginary pressure"
        z = z * float(model.get("distance_m", 1.0)) / float(model.get("voltage_rms", 2.83))
        return cli.interp_complex(f, fr, z, delay_s=float(model.get("delay_s", 0.))), basis
    if kind == "frd_file":
        table = np.loadtxt(cli.resolve_path(model["file"], base_dir), comments=["#", "*", ";"])
        fr = table[:, 0]
        mag = acoustics.P0 * 10 ** (table[:, 1] / 20)
        phase = np.deg2rad(table[:, 2]) if table.shape[1] > 2 else np.zeros_like(fr)
        z = mag * np.exp(1j * phase) * float(model.get("distance_m", 1.0)) / float(model.get("voltage_rms", 2.83))
        if table.shape[1] <= 2 and model.get("minimum_phase", True):
            z = acoustics.minimum_phase(fr, fr, 20 * np.log10(np.abs(z) / acoustics.P0)) * acoustics.P0
        return cli.interp_complex(f, fr, z, delay_s=float(model.get("delay_s", 0.))), ("FRD supplied complex phase" if table.shape[1] > 2 else "FRD magnitude with reconstructed minimum phase" if model.get("minimum_phase", True) else "FRD magnitude with explicitly assumed zero phase")
    raise cli.InputError(f"unknown acoustic kind '{kind}'")


def _impedance(params, f, base_dir):
    model = cli.require(params, "impedance")
    kind = cli.require(model, "kind", label="impedance")
    if kind == "reference":
        ref = dict(model["reference"])
        ref.setdefault("frequency_path", "results.f_hz")
        return cli.curve_from_reference(ref, base_dir, f), "impedance curve read from another result file"
    if kind == "zma_file":
        table = np.loadtxt(cli.resolve_path(model["file"], base_dir), comments=["#", "*", ";"])
        z = table[:, 1] * np.exp(1j * np.deg2rad(table[:, 2] if table.shape[1] > 2 else 0.0))
        return cli.interp_complex(f, table[:, 0], z), "ZMA file interpolated onto the grid"
    return acoustics.impedance_model(model, f), f"{kind} impedance model"


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 10.0, 40000.0, 800)
    p, p_basis = _pressure(params, f, base_dir)
    z, z_basis = _impedance(params, f, base_dir)
    model = params.get("acoustic") or {}
    inherited_contract = {}
    inherited_directivity = None
    if model.get("kind") == "simulation":
        upstream = cli.load_json(cli.resolve_path(model["reference"]["file"],base_dir)).get("results",{})
        inherited_contract = upstream.get("source_contract",{})
        inherited_directivity = upstream.get("directivity")
    contract = dict(inherited_contract, **(model.get("contract") or {}))
    phase_reference = contract.get("phase_reference", "intrinsic")
    if contract.get("baffle","external") not in ("external","included"):
        raise cli.InputError("contract.baffle needs external or included")
    if phase_reference not in ("intrinsic", "common_observer"):
        raise cli.InputError("contract.phase_reference needs intrinsic or common_observer")
    if phase_reference == "common_observer":
        phase_evidence=str(contract.get("phase_basis",""))+" "+p_basis
        if "reconstructed" in phase_evidence or "assumed zero" in phase_evidence or "assumed_zero" in phase_evidence:
            raise cli.InputError("common_observer phase needs supplied complex timing information")
        reference_m = cli.positive(contract.get("reference_distance_m"), "contract.reference_distance_m")
        observer = np.asarray(contract.get("observer_position_m"),float)
        if observer.shape != (3,) or not np.all(np.isfinite(observer)):
            raise cli.InputError("common_observer contract needs observer_position_m in cabinet coordinates")
        if not contract.get("common_delay_removed", False):
            p *= np.exp(2j * np.pi * f * reference_m / acoustics.C)
        contract["common_delay_removed"] = True
    contract.update(phase_reference=phase_reference, pressure_reference_m=1.,
                    baffle=contract.get("baffle", "external"), phase_basis=contract.get("phase_basis",p_basis),
                    normalization=contract.get("normalization", "driver_terminal_volt" if model.get("voltage_basis") == "driver_terminal" else "declared_volt"))
    calibration = model.get("level_calibration")
    gain = 1.0
    if calibration is not None:
        if not isinstance(calibration, dict):
            raise cli.InputError("acoustic.level_calibration must be an object with gain_db and basis")
        gain_db = calibration.get("gain_db")
        if isinstance(gain_db, bool) or not isinstance(gain_db, (int, float)) or not np.isfinite(gain_db):
            raise cli.InputError("acoustic.level_calibration.gain_db must be finite")
        if not isinstance(calibration.get("basis"), str) or not calibration["basis"].strip():
            raise cli.InputError("acoustic.level_calibration.basis must explain the source and derivation")
        try:
            gain = 10.0 ** (gain_db / 20.0)
        except OverflowError as exc:
            raise cli.InputError("acoustic.level_calibration.gain_db produces an unrepresentable gain") from exc
        if not np.isfinite(gain) or gain == 0:
            raise cli.InputError("acoustic.level_calibration.gain_db produces an unrepresentable gain")
        p = p * gain
        p_basis += f"; acoustic-only calibration {gain_db:g} dB: {calibration['basis']}"
    extra = {}
    if model.get("kind") == "lf_box":
        outlet, _ = _box_pressure(model, f, base_dir, outlet=True)
        if outlet is not None:
            extra["outlet_pressure_per_volt_pa"] = outlet * gain
    if calibration is not None:
        extra["level_calibration"] = dict(calibration)
    spl = 20 * np.log10(np.maximum(np.abs(p) * 2.83, 1e-30) / acoustics.P0)
    band = params.get("analysis", {}).get("sensitivity_band_hz")
    stats = dict(spl_2v83_1m_db=spl)
    if band:
        inside = (f >= band[0]) & (f <= band[1])
        stats["sensitivity_band_hz"] = list(band)
        stats["mean_spl_in_band_db"] = float(np.mean(spl[inside]))
    zmag = np.abs(z)
    stats["impedance_min_ohm"] = float(zmag.min())
    stats["impedance_min_hz"] = float(f[np.argmin(zmag)])
    validity = dict(statements=list(VALIDITY), evaluated_band_hz=[float(f[0]), float(f[-1])], acoustic_kind=model.get("kind"))
    gate_ms = model.get("gate_ms")
    if gate_ms:
        validity["gate_ms"] = float(gate_ms)
        validity["gated_valid_above_hz"] = 1000.0 / float(gate_ms)
        validity["statements"] = validity["statements"] + [
            f"The imported measurement was gated at {float(gate_ms):g} ms, so it is trustworthy only above about "
            f"{1000.0 / float(gate_ms):.0f} Hz. Below that the curve here is the splice or the prior, not the measurement."]
    elif model.get("kind") in ("measured", "frd_file"):
        validity["statements"] = validity["statements"] + [
            "acoustic.gate_ms was not stated for an imported measurement, so its low-frequency validity limit is unknown. A "
            "response quoted without its gate has an unstated low-frequency validity limit."]
    radius = params.get("piston_radius_mm")
    if radius:
        validity["piston_ka_unity_hz"] = acoustics.C / (2 * np.pi * float(radius) / 1000)
    return dict(f_hz=f, name=params.get("name"), pressure_per_volt_pa=p, z_ohm=z, pressure_basis=p_basis, impedance_basis=z_basis,
                directivity=params.get("directivity", inherited_directivity), acoustic_depth_mm=params.get("acoustic_depth_mm"), statistics=stats,
                validity=validity, source_contract=contract, **extra)


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Complex acoustic source and load model of one section", NOTES, VALIDITY))
