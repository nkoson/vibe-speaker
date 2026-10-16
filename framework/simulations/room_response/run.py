#!/usr/bin/env python3
"""Finite-order 3D rectangular-room image response at physical listening positions."""
import itertools
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import acoustics, cli, radiation  # noqa: E402

NAME = "room_response"
VERSION = "1.0"
WALLS = ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max")
NOTES = [
    "Finite-order coherent image-receiver sum in a rectangular 3D room. Each source retains its position, orientation, complex pressure, crossover and baffle factor.",
    "Pressure is at the actual receiver distance, not a 1 m equivalent. Absolute propagation delay is retained. Floor reflection is included only by the room walls.",
    "Wall inputs are signed pressure reflection coefficients, not energy absorption coefficients; they are frequency-dependent declared scenarios, independent of incidence angle.",
    "Multiple speakers are driven coherently by the same signal. This is a mono/correlated-channel scenario, not the response of arbitrary stereo programme.",
]
VALIDITY = [
    "Specular planar reflections only: no furniture, scattering, transmission, air absorption, wall vibration or source-room feedback on driver impedance.",
    "Finite reflection order predicts direct sound and early-reflection interference. It is not a converged low-frequency room-mode solution or a late-reverberation/RT60 prediction.",
    "Directional sources require a declared rear-radiation prior. Imported on-axis baffle factors are reused for reflected rays; this is not angle-dependent cabinet diffraction or a 3D cabinet wave solve.",
    "Last-order contribution and frequency-step diagnostics report numerical sensitivity, not empirical error bounds. No pass/fail judgement is made.",
]


def vector3(value, label):
    try:
        vector = np.asarray(value, float)
    except (TypeError, ValueError) as exc:
        raise cli.InputError(f"{label} needs three finite coordinates") from exc
    if vector.shape != (3,) or not np.all(np.isfinite(vector)):
        raise cli.InputError(f"{label} needs three finite coordinates")
    return vector


def inside(position, dimensions, label):
    if np.any(position <= 0) or np.any(position >= dimensions):
        raise cli.InputError(f"{label} must lie strictly inside the room")


def reflection_curve(spec, f, label):
    if isinstance(spec, (int, float)) and not isinstance(spec, bool):
        values = np.full(len(f), float(spec))
    elif isinstance(spec, dict) and "points" in spec:
        try:
            table = np.asarray(spec["points"], float)
        except (TypeError, ValueError) as exc:
            raise cli.InputError(f"{label}.points needs [frequency_hz, pressure_reflection] rows") from exc
        if table.ndim != 2 or table.shape[1] != 2 or len(table) < 2 or not np.all(np.isfinite(table)):
            raise cli.InputError(f"{label}.points needs at least two finite [frequency_hz, pressure_reflection] rows")
        if np.any(table[:, 0] <= 0) or np.any(np.diff(table[:, 0]) <= 0):
            raise cli.InputError(f"{label} frequencies must be positive and increasing")
        if f[0] < table[0, 0] or f[-1] > table[-1, 0]:
            raise cli.InputError(f"{label} table must cover the requested frequency band")
        if np.any(np.abs(table[:, 1]) > 1):
            raise cli.InputError(f"{label} pressure reflection must be between -1 and 1")
        values = np.interp(np.log(f), np.log(table[:, 0]), table[:, 1])
    else:
        raise cli.InputError(f"{label} needs a pressure coefficient or a points table")
    if not np.all(np.isfinite(values)) or np.any(np.abs(values) > 1):
        raise cli.InputError(f"{label} pressure reflection must be finite and between -1 and 1")
    return values


def image_paths(dimensions, order):
    """Unfold receiver r to 2*n*L + sign*r; keep exact counts per physical wall."""
    axes = []
    for length in dimensions:
        options = []
        for n in range(-order, order + 1):
            for parity in (0, 1):
                low, high = abs(n - parity), abs(n)
                if low + high <= order:
                    options.append((2 * n * length, 1 - 2 * parity, low, high))
        axes.append(options)
    paths = []
    for combination in itertools.product(*axes):
        counts = np.array([v for item in combination for v in item[2:]], int)
        if counts.sum() <= order:
            paths.append(dict(offset=np.array([item[0] for item in combination]),
                              sign=np.array([item[1] for item in combination]),
                              counts=counts, order=int(counts.sum())))
    return sorted(paths, key=lambda row: (row["order"], tuple(row["counts"]), tuple(row["offset"])))


def yaw_matrix(degrees):
    if isinstance(degrees, bool) or not isinstance(degrees, (int, float)) or not np.isfinite(degrees):
        raise cli.InputError("speaker yaw_deg must be finite")
    angle = np.deg2rad(degrees)
    c, s = np.cos(angle), np.sin(angle)
    return np.array([[c, s, 0.], [-s, c, 0.], [0., 0., 1.]])


def check_curve_domains(document, f, base_dir):
    """Room interference must not be built from silently extended source endpoints."""
    refs = []
    for section in document.get("sections", []):
        refs.extend(section[key] for key in ("source", "pressure_per_volt", "transfer", "baffle")
                    if isinstance(section.get(key), dict) and "file" in section[key])
        for outlet in section.get("rear_outlets", []):
            refs.extend(outlet[key] for key in ("pressure", "baffle") if outlet.get(key))
    for ref in refs:
        path = cli.resolve_path(ref["file"], base_dir)
        data = cli.load_json(path)
        if data.get("status", "computed") != "computed":
            raise cli.InputError(f"room source reference is not computed: {path}")
        grid = np.asarray(cli.dotted(data, ref.get("frequency_path", "results.f_hz")), float)
        if grid.ndim != 1 or len(grid) < 2 or not np.all(np.isfinite(grid)) or np.any(grid <= 0):
            raise cli.InputError(f"room source reference needs a finite positive frequency grid: {path}")
        if len(np.unique(grid)) != len(grid) or f[0] < grid.min() or f[-1] > grid.max():
            raise cli.InputError(f"room source reference must have unique frequencies and cover the requested band: {path}")


def load_emitters(params, f, base_dir, dimensions):
    speakers = cli.require(params, "speakers")
    if not isinstance(speakers, list) or not speakers:
        raise cli.InputError("speakers must be a nonempty list")
    emitters = []
    for index, speaker in enumerate(speakers):
        label = speaker.get("name", f"speaker-{index + 1}")
        origin = vector3(cli.require(speaker, "origin_m", label=label), f"{label}.origin_m")
        rotation = yaw_matrix(speaker.get("yaw_deg", 0.))
        if ("speaker_file" in speaker) == ("speaker" in speaker):
            raise cli.InputError(f"{label} needs exactly one of speaker_file or speaker")
        if "speaker_file" in speaker:
            path = cli.resolve_path(speaker["speaker_file"], base_dir)
            document, source_base = cli.load_json(path), path.parent
        else:
            document, source_base = speaker["speaker"], base_dir
        voltage = cli.positive(speaker.get("input_voltage_rms", document.get("input_voltage_rms", 2.83)),
                               f"{label}.input_voltage_rms", zero=True)
        check_curve_domains(document, f, source_base)
        sections = radiation.load_sections(document, f, source_base)
        if not sections:
            raise cli.InputError(f"{label} needs at least one section")
        fallback = radiation.rear_prior(speaker.get("rear_radiation"))
        for section in sections:
            records = [(section, section["pressure"] * section["baffle"] * section["transfer"],
                        section["tilt_rad"], section["name"])]
            for outlet_index, outlet in enumerate(section["outlets"]):
                records.append((outlet, outlet["pressure"] * outlet["baffle"] * section["transfer"],
                                np.pi if outlet["face"] == "rear" else 0., f"{section['name']}:outlet-{outlet_index + 1}"))
            for record, pressure, pitch, name in records:
                centre = origin + rotation @ record["centre"]
                inside(centre, dimensions, f"{label}/{name} acoustic centre")
                rear = record.get("rear") or fallback
                if record["directivity"].get("kind") not in ("omni", "dipole", "cardioid", "complex_grid") and rear is None:
                    raise cli.InputError(f"{label}/{name} needs rear_radiation for reflected rays")
                emitters.append(dict(name=f"{label}/{name}", centre=centre, rotation=rotation,
                                     pitch=pitch, axis=record.get("axis"), pressure=pressure * voltage,
                                     directivity=record["directivity"], rear=rear))
    return emitters


def propagated(emitter, points, f):
    # Unfolded receiver rays originate at the real source, so source orientation is
    # applied once here; reflecting source positions without their axes is incorrect.
    vector = (points - emitter["centre"]) @ emitter["rotation"]
    distance = np.linalg.norm(vector, axis=1)
    if np.any(distance <= 1e-9):
        raise cli.InputError("a receiver coincides with an acoustic centre")
    pitch = emitter["pitch"]
    axial = vector[:, 1] * np.cos(pitch) + vector[:, 2] * np.sin(pitch)
    up = -vector[:, 1] * np.sin(pitch) + vector[:, 2] * np.cos(pitch)
    lateral = vector[:,0]
    if emitter.get("axis") is not None:
        forward=np.asarray(emitter["axis"],float);forward/=np.linalg.norm(forward)
        right=np.cross(forward,[0,0,1] if abs(forward[2])<.99 else [0,1,0]);right/=np.linalg.norm(right)
        vertical=np.cross(right,forward);axial=vector@forward;up=vector@vertical;lateral=vector@right
    h = np.arctan2(lateral, axial)
    v = np.arctan2(up, np.hypot(lateral, axial))
    pattern = acoustics.directivity(emitter["directivity"], f[None, :], h[:, None], v[:, None])
    if emitter["rear"] is not None and emitter["directivity"].get("kind") not in ("omni", "dipole", "cardioid", "complex_grid"):
        behind = np.maximum(-axial / distance, 0.)[:, None]
        pattern = pattern * (1 + (radiation.rear_gain(emitter["rear"], f)[None, :] - 1) * behind)
    phase = np.exp(-2j * np.pi * distance[:, None] * f[None, :] / acoustics.C)
    return emitter["pressure"][None, :] * pattern * phase / distance[:, None], distance


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 20., 2000., 1981, "linear")
    if len(f) < 2:
        raise cli.InputError("room_response needs at least two frequencies")
    room = cli.require(params, "room")
    dimensions = vector3(cli.require(room, "dimensions_m"), "room.dimensions_m")
    if np.any(dimensions <= 0):
        raise cli.InputError("room dimensions must be positive")
    walls = cli.require(room, "pressure_reflection")
    if not isinstance(walls, dict) or set(walls) != set(WALLS):
        raise cli.InputError(f"room.pressure_reflection needs exactly {WALLS}")
    coefficients = np.array([reflection_curve(walls[name], f, name) for name in WALLS])
    order = params.get("max_order", 2)
    if isinstance(order, bool) or not isinstance(order, int) or not 0 <= order <= 8:
        raise cli.InputError("max_order must be an integer from 0 to 8")
    receivers = cli.require(params, "receivers")
    if not isinstance(receivers, list) or not receivers:
        raise cli.InputError("receivers must be a nonempty list")
    positions = np.array([vector3(cli.require(r, "position_m"), "receiver.position_m") for r in receivers])
    for point in positions:
        inside(point, dimensions, "receiver.position_m")
    emitters = load_emitters(params, f, base_dir, dimensions)
    paths = image_paths(dimensions, order)
    direct = np.zeros((len(receivers), len(f)), complex)
    reflected = np.zeros_like(direct)
    last_order = np.zeros_like(direct)
    arrivals = [[] for _ in receivers]
    max_path = 0.
    for path in paths:
        gain = np.prod(coefficients ** path["counts"][:, None], axis=0)
        if not np.any(gain):
            continue
        images = path["offset"] + positions * path["sign"]
        for emitter in emitters:
            contribution, distances = propagated(emitter, images, f)
            contribution *= gain[None, :]
            if params.get("max_arrival_ms") is not None and path["order"] > 0:
                contribution *= (distances[:, None] / acoustics.C <= float(params["max_arrival_ms"]) / 1000)
            max_path = max(max_path, float(distances.max()))
            if path["order"] == 0:
                direct += contribution
            else:
                reflected += contribution
                if path["order"] == order:
                    last_order += contribution
            if path["order"] <= 1:
                for i, distance in enumerate(distances):
                    arrivals[i].append(dict(source=emitter["name"], order=path["order"],
                                            wall_hits=dict(zip(WALLS, path["counts"].tolist())),
                                            distance_m=float(distance), arrival_ms=float(1000 * distance / acoustics.C)))
    total = direct + reflected
    scale = 1 / acoustics.P0
    rows = []
    for i, receiver in enumerate(receivers):
        curve = acoustics.db(total[i] * scale)
        direct_db = acoustics.db(direct[i] * scale)
        rows.append(dict(name=receiver.get("name", f"receiver-{i + 1}"), position_m=positions[i],
                         pressure_pa=total[i], direct_pressure_pa=direct[i], reflected_pressure_pa=reflected[i],
                         spl_db=curve, direct_spl_db=direct_db, room_minus_direct_db=curve - direct_db,
                         last_order_pressure_pa=last_order[i],
                         order_increment_db=curve - acoustics.db((total[i] - last_order[i]) * scale),
                         direct_and_first_arrivals=sorted(arrivals[i], key=lambda r: r["arrival_ms"])))
    blend = params.get("model_blend")
    if blend:
        transition = blend["transition_hz"]
        if not 0 < transition[0] < transition[1]:
            raise cli.InputError("model_blend.transition_hz needs positive increasing endpoints")
        modal = cli.load_json(cli.resolve_path(blend["modal_file"],base_dir))
        modal_f = np.asarray(modal["results"]["f_hz"])
        if modal_f[0] > f[0] or modal_f[-1] < transition[1]:
            raise cli.InputError("modal source does not cover the low band and transition")
        weight = np.clip((np.log(f)-np.log(transition[0]))/np.log(transition[1]/transition[0]),0,1)
        weight = .5-.5*np.cos(np.pi*weight)
        ray = cli.load_json(cli.resolve_path(blend["ray_file"],base_dir)) if blend.get("ray_file") else None
        for i,row in enumerate(rows):
            lowrow = modal["results"]["receivers"][i]
            if not np.allclose(lowrow["position_m"],positions[i]):
                raise cli.InputError("modal/image receiver coordinates differ")
            low = cli.interp_complex(f,modal_f,cli.complex_from_record(lowrow["pressure_pa"]))
            late = np.zeros(len(f))
            if ray:
                rayrow=ray["results"]["receivers"][i]
                if not np.allclose(rayrow["position_m"],positions[i]):
                    raise cli.InputError("ray/image receiver coordinates differ")
                rayf=np.asarray(ray["results"]["f_hz"])
                if rayf[0]>transition[0] or rayf[-1]<f[-1]:
                    raise cli.InputError("ray source does not cover the high band")
                late=cli.interp_real(f,rayf,rayrow["reflected_mean_square_pa2"])
            high=abs(total[i])**2+late
            hybrid=(1-weight)*abs(low)**2+weight*high
            row.update(hybrid_mean_square_pa2=hybrid,hybrid_spl_db=10*np.log10(np.maximum(hybrid,1e-60)/acoustics.P0**2),
                       model_overlap_difference_db=acoustics.db(low)-acoustics.db(total[i]),
                       high_model_weight=weight)
            row["hybrid_basis"]="Declared power blend of modal and early-plus-late fields; not a coherent phase blend."
            if ray:
                row["early_late_overlap_ms"]=None if params.get("max_arrival_ms") is None else float(params["max_arrival_ms"])-float(ray.get("validity",{}).get("min_arrival_ms",0))
    seat_db = acoustics.db(total * scale)
    energy = np.mean(np.abs(total) ** 2, axis=0)
    suggested_step = acoustics.C / (8 * max_path)
    return dict(f_hz=f, max_order=order, image_count=len(paths),
                room_dimensions_m=dimensions, walls=list(WALLS), pressure_reflection=coefficients,
                source_geometry=[dict(name=e["name"], centre_m=e["centre"],
                                      forward_vector=e["rotation"] @ np.asarray(e["axis"] if e.get("axis") is not None else [0., np.cos(e["pitch"]), np.sin(e["pitch"])]),
                                      directivity=e["directivity"], rear_radiation=e["rear"]) for e in emitters],
                receivers=rows,
                spatial_summary=dict(energy_mean_spl_db=10 * np.log10(np.maximum(energy / acoustics.P0 ** 2, 1e-60)),
                                     min_spl_db=seat_db.min(axis=0), max_spl_db=seat_db.max(axis=0),
                                     spread_db=seat_db.max(axis=0) - seat_db.min(axis=0),
                                     note="Energy average over declared seats; not a coherent sum across microphones or a preference score."),
                validity=dict(reflection_order=order, longest_included_path_m=max_path,
                              max_frequency_step_hz=float(np.max(np.diff(f))),
                              eight_samples_per_longest_path_cycle_step_hz=suggested_step,
                              pressure_basis="Pa RMS at actual receiver, full propagation delay; source input is Pa per volt at 1 m",
                              order_note="order_increment_db compares N with N-1 within the same model; increase order independently before interpreting stable room interference."))


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "3D room direct sound and early reflections", NOTES, VALIDITY))
