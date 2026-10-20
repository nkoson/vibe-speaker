#!/usr/bin/env python3
"""Normalize measured polar files to a canonical complex source without inventing coverage."""
import hashlib
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, response_data
NAME = "polar_import"
VERSION = "1.0"


def compute(params, base_dir):
    voltage = cli.positive(params.get("voltage_rms"), "voltage_rms")
    distance = cli.positive(params.get("distance_m"), "distance_m")
    timing = params.get("phase_reference")
    if timing not in ("intrinsic", "absolute", "reference_delay_removed"):
        raise cli.InputError("phase_reference needs intrinsic, absolute or reference_delay_removed")
    if params.get("baffle","included") not in ("included","external"):
        raise cli.InputError("baffle must be included or external")
    if params.get("gate_ms") is not None:
        cli.positive(params["gate_ms"],"gate_ms")
    source = np.asarray(params.get("source_position_m", [0, 0, 0]), float)
    centre = np.asarray(params.get("rotation_center_m", [0, 0, 0]), float)
    if source.shape != (3,) or centre.shape != (3,) or not np.all(np.isfinite([source, centre])):
        raise cli.InputError("source and rotation centre need finite xyz positions")
    rows = []
    for record in cli.require(params, "responses"):
        path = cli.resolve_path(record["file"], base_dir)
        fp, p, phase = response_data.read_table(path, phase_assumption=params.get("phase_assumption"))
        if phase != "supplied" and timing != "intrinsic":
            raise cli.InputError("geometric timing removal requires supplied complex phase")
        angle = float(record["angle_deg"])
        plane = record["plane"].upper()
        if plane not in ("H", "V") or not -180 <= angle <= 180:
            raise cli.InputError("plane is H or V and angle lies within -180..180")
        a = np.deg2rad(angle)
        direction = [np.sin(a), np.cos(a), 0] if plane == "H" else [0, np.cos(a), np.sin(a)]
        path_length = np.linalg.norm(centre+distance*np.array(direction)-source)
        if path_length <= 0:
            raise cli.InputError("measurement observer coincides with source")
        removed = (path_length if timing == "absolute" else path_length-distance) / cli.C
        if timing == "intrinsic":
            removed = 0
        # Remove known acquisition and geometric delay BEFORE frequency resampling.
        removed += float(params.get("acquisition_delay_s", 0))
        normalized = p*np.exp(2j*np.pi*fp*removed)*path_length/voltage
        rows.append(dict(plane=plane, angle=angle, f=fp, p=normalized, phase=phase,
                         file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    if not rows:
        raise cli.InputError("responses cannot be empty")
    low, high = max(r["f"][0] for r in rows), min(r["f"][-1] for r in rows)
    if low >= high:
        raise cli.InputError("polar files have no common frequency interval")
    f = cli.frequency_grid(params.get("frequencies"), low, high, 400)
    planes = {}
    onaxis = None
    for key, name in (("H", "horizontal"), ("V", "vertical")):
        records = [r for r in rows if r["plane"] == key]
        if not records:
            if key == "V" and params.get("axial_symmetry"):
                continue
            raise cli.InputError(f"missing {key} plane; axial_symmetry must be explicit")
        values = {}
        for r in records:
            if r["angle"] in values:
                raise cli.InputError("duplicate polar direction")
            values[r["angle"]] = response_data.resample(f, r["f"], r["p"])
        if params.get("mirror_missing"):
            for a, p in list(values.items()):
                values.setdefault(-a, p.copy())
        # +/-180 denote exactly the same physical direction.
        if 180 in values:
            if -180 in values and not np.allclose(values[180],values[-180],rtol=1e-4,atol=1e-12):
                raise cli.InputError("plus/minus 180-degree measurements disagree at the same direction")
            values.setdefault(-180, values[180])
        if -180 in values:
            values.setdefault(180, values[-180])
        if 0 not in values or len(values) < 2:
            raise cli.InputError("each measured plane needs zero degrees and another direction")
        if onaxis is None:
            onaxis = values[0]
        elif not np.allclose(values[0], onaxis, rtol=1e-4, atol=1e-12):
            raise cli.InputError("horizontal and vertical on-axis complex responses disagree")
        floor = max(abs(onaxis).max()*1e-12, 1e-30)
        if np.any(abs(onaxis) <= floor):
            raise cli.InputError("on-axis null prevents pressure/directivity factorization")
        angles = sorted(values)
        data = np.stack([values[a]/onaxis for a in angles])
        planes[name] = dict(angles_deg=angles, real=data.real, imag=data.imag)
    model = dict(kind="measured_planes", frequency_hz=f, axial_symmetry=bool(params.get("axial_symmetry")), **planes)
    return dict(f_hz=f, pressure_per_volt_pa=onaxis, directivity=model,
                source_contract=dict(phase_reference="intrinsic", pressure_reference_m=1.,
                                     normalization="driver_terminal_volt", baffle=params.get("baffle", "included"),
                                     phase_basis=sorted({r["phase"] for r in rows})),
                coverage=dict(full_sphere=response_data.full_sphere(model),
                              mirror_missing=bool(params.get("mirror_missing")),
                              diagonal_interpolation="complex transverse-angle blend; diagonal data is not measured"),
                provenance=[{k:r[k] for k in ("file", "sha256", "plane", "angle", "phase")} for r in rows],
                validity=dict(gate_ms=params.get("gate_ms"), gated_valid_above_hz=1000/params["gate_ms"] if params.get("gate_ms") else None))


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, __doc__, [
        "Imported pressure is normalized to 1 m per terminal volt. Coverage and phase assumptions remain explicit.",
        "Two great-circle measurements do not identify a full spherical field. Diagonals use a declared complex interpolation.",
        "See framework/references/measured-response-processing.md for source conventions and independent references."]))
