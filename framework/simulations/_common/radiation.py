"""Coherent exterior sum of the sections of one loudspeaker, shared by whole_speaker and crossover_fit.

Coordinates: x lateral (0 at the cabinet centre line, positive to the listener's right),
y forward (front face at 0, positive toward the listener), z height above the floor.
Pressures are normalized to the reference distance: a source's 1 m pressure per volt
multiplied by reference_distance / actual_distance, with the common delay of the
reference distance removed, so the sum reads like an SPL at 1 m equivalent.
"""
import numpy as np

from . import acoustics, cli, geometry
from .acoustics import C


def load_sections(params, f, base_dir):
    """Resolve every section of a whole_speaker parameter document into arrays on f."""
    cabinet = params.get("cabinet") or {}
    floor_offset = float(cabinet.get("floor_offset_mm", 0.0)) / 1000
    depth_m = float(cabinet.get("depth_mm", 0.0)) / 1000
    sections = []
    assembly = geometry.load_assembly(params["assembly"],base_dir) if params.get("assembly") else None
    for original in cli.require(params, "sections"):
        section = dict(original)
        if section.get("assembly_source"):
            if not assembly: raise cli.InputError("assembly_source needs a shared assembly")
            src = next(s for s in assembly["sources"] if s["id"] == section["assembly_source"])
            obj = next(o for o in assembly["objects"] if o["id"] == src["object_id"])
            rotation, origin = geometry.transform(obj)
            point = rotation @ np.asarray(src["local_position_m"]) + origin
            section["position"] = dict(x_mm=point[0]*1000,depth_mm=-point[1]*1000,z_mm=point[2]*1000)
            section["normal"] = (rotation @ np.asarray(src.get("local_normal",[0,1,0]))).tolist()
        source_doc = None
        pressure = None
        if section.get("source"):
            ref = dict(section["source"])
            ref.setdefault("frequency_path", "results.f_hz")
            source_doc = cli.load_json(cli.resolve_path(ref["file"], base_dir))
            pressure = cli.curve_from_reference(dict(ref, path=ref.get("pressure_path", "results.pressure_per_volt_pa")), base_dir, f)
        if section.get("pressure_per_volt"):
            ref = dict(section["pressure_per_volt"])
            ref.setdefault("frequency_path", "results.f_hz")
            pressure = cli.curve_from_reference(ref, base_dir, f)
        if pressure is None:
            raise cli.InputError(f"section '{section.get('name')}' needs a source file or a pressure_per_volt reference")
        directivity = section.get("directivity") or (cli.dotted(source_doc, "results.directivity") if source_doc else None) or {"kind": "omni"}
        depth = section.get("position", {}).get("depth_mm")
        if depth is None and source_doc:
            depth = cli.dotted(source_doc, "results.acoustic_depth_mm")
        depth = float(depth or 0.0)
        contract = (source_doc or {}).get("results", {}).get("source_contract", {})
        if contract.get("baffle") == "included" and section.get("baffle"):
            raise cli.InputError("source already includes the baffle correction")
        position = cli.require(section, "position", label=f"section {section.get('name')}")
        centre = np.array([float(position.get("x_mm", 0.0)) / 1000, -depth / 1000, float(position["z_mm"]) / 1000 + floor_offset])
        if contract.get("phase_reference") == "common_observer":
            reference = np.asarray(contract.get("observer_position_m"),float)
            if reference.shape != (3,):raise cli.InputError("common-observer source needs observer_position_m")
            r0=float(contract["reference_distance_m"])
            measured_path=float(np.linalg.norm(reference-centre))
            if measured_path<=0:raise cli.InputError("common observer coincides with source centre")
            pressure=pressure*(measured_path/r0)*np.exp(2j*np.pi*f*(measured_path-r0)/C)
        transfer = transfer_curve(section.get("transfer"), f, base_dir)
        baffle = np.ones(len(f), complex)
        if section.get("baffle"):
            ref = dict(section["baffle"])
            ref.setdefault("frequency_path", "results.f_hz")
            baffle = cli.curve_from_reference(ref, base_dir, f)
        entry = dict(name=section.get("name"), pressure=pressure, directivity=directivity, centre=centre, transfer=transfer, baffle=baffle,
                     acoustic_depth_mm=depth,
                     rear=rear_prior(section.get("rear_radiation"), cabinet.get("baffle_width_mm")),
                     axis=section.get("normal"), tilt_rad=np.deg2rad(float(section.get("tilt_deg", 0.0))), outlets=[])
        for outlet in section.get("rear_outlets", []) or []:
            ref = dict(outlet["pressure"])
            ref.setdefault("frequency_path", "results.f_hz")
            p_out = cli.curve_from_reference(ref, base_dir, f) / float(outlet.get("voltage_rms", 2.83))
            positions = outlet.get("positions") or [{"x_mm": 0.0, "z_mm": position["z_mm"]}]
            face = outlet.get("face", "rear")
            o_baffle = np.ones(len(f), complex)
            if outlet.get("baffle"):
                oref = dict(outlet["baffle"])
                oref.setdefault("frequency_path", "results.f_hz")
                o_baffle = cli.curve_from_reference(oref, base_dir, f)
            elif face == "rear":
                o_baffle = np.full(len(f), 0.5, complex)
            for pos in positions:
                y = float(pos["y_mm"])/1000 if "y_mm" in pos else -float(pos["depth_mm"])/1000 if "depth_mm" in pos else -depth_m if face == "rear" else 0.0
                entry["outlets"].append(dict(pressure=p_out / len(positions), baffle=o_baffle, face=face,
                                             centre=np.array([float(pos.get("x_mm", 0.0)) / 1000, y, float(pos["z_mm"]) / 1000 + floor_offset]),
                                             rear=rear_prior(outlet.get("rear_radiation"), cabinet.get("baffle_width_mm")),
                                             axis=outlet.get("normal", [0,-1,0] if face=="rear" else [0,1,0]),
                                             directivity=outlet.get("directivity") or {"kind": "omni"}))
        sections.append(entry)
    return sections


def transfer_curve(spec, f, base_dir):
    """Electrical transfer of a section: unity, a file reference or an ideal filter description."""
    if not spec:
        return np.ones(len(f), complex)
    if "file" in spec:
        ref = dict(spec)
        ref.setdefault("frequency_path", "results.f_hz")
        return cli.curve_from_reference(ref, base_dir, f)
    ideal = spec.get("ideal") or spec
    h = np.ones(len(f), complex)
    order = int(ideal.get("order", 4))
    kind = ideal.get("type", "linkwitz_riley")
    builder = acoustics.linkwitz_riley if kind == "linkwitz_riley" else (lambda ff, fc, o, hp: acoustics.butterworth(ff, fc, o, hp))
    if ideal.get("low_hz"):
        h = h * builder(f, float(ideal["low_hz"]), order, True)
    if ideal.get("high_hz"):
        h = h * builder(f, float(ideal["high_hz"]), order, False)
    h = h * 10 ** (float(ideal.get("gain_db", 0.0)) / 20) * float(ideal.get("polarity", 1))
    if ideal.get("delay_ms"):
        h = h * np.exp(-2j * np.pi * f * float(ideal["delay_ms"]) / 1000)
    return h


def observation_points(distance_m, ear_height_m, angles_deg, plane):
    a = np.deg2rad(np.asarray(angles_deg, float))
    if plane == "H":
        return np.column_stack([distance_m * np.sin(a), distance_m * np.cos(a), np.full_like(a, ear_height_m)])
    return np.column_stack([np.zeros_like(a), distance_m * np.cos(a), ear_height_m + distance_m * np.sin(a)])


def rear_prior(spec, default_width_mm=None):
    """Normalise a declared rear-hemisphere prior, or return None when none was declared.

    {"kind": "shadowed_monopole", "corner_hz" | "baffle_width_mm", "floor_db", "order"}

    Without one, a source contributes nothing at or behind 90 degrees from its axis, which is the
    infinite-baffle idealisation and is wrong for a real cabinet at low frequency, where the box is
    small compared with a wavelength and radiates in every direction. It is a declared prior with no
    measurement behind it: a BEM solve is what would replace it, and none is available here.
    """
    if not spec:
        return None
    kind = spec.get("kind", "shadowed_monopole")
    if kind != "shadowed_monopole":
        raise cli.InputError(f"unknown rear_radiation kind '{kind}'; the only model here is shadowed_monopole")
    corner = spec.get("corner_hz")
    width = spec.get("baffle_width_mm", default_width_mm)
    if corner is None:
        if not width:
            raise cli.InputError("rear_radiation needs corner_hz or baffle_width_mm")
        corner = C / (2 * float(width) / 1000)
    return dict(kind=kind, corner_hz=float(corner), floor_db=float(spec.get("floor_db", -20.0)),
                order=float(spec.get("order", 1.0)), baffle_width_mm=width)


def rear_gain(prior, f):
    """Amplitude behind the cabinet relative to the front: unity well below the corner, the floor well above it."""
    floor = 10 ** (prior["floor_db"] / 20)
    return floor + (1 - floor) / (1 + (np.asarray(f, float) / prior["corner_hz"]) ** prior["order"])


def _propagate(f, source, centre, directivity, tilt_rad, points, reference_m, mirror=False, reflection=1.0, rear=None, axis=None):
    """Pressure of one source at each point (points x f), optionally its floor image."""
    c = centre.copy()
    if mirror:
        c[2] = -c[2]
    vector = points - c[None, :]
    distance = np.linalg.norm(vector, axis=1)
    if np.any(distance <= 0):
        raise cli.InputError("an observer coincides with an acoustic centre")
    pitch = -tilt_rad if mirror else tilt_rad
    axial = vector[:, 1] * np.cos(pitch) + vector[:, 2] * np.sin(pitch)
    up = -vector[:, 1] * np.sin(pitch) + vector[:, 2] * np.cos(pitch)
    lateral = vector[:,0]
    if axis is not None:
        forward = np.asarray(axis,float); forward = forward/np.linalg.norm(forward)
        if mirror: forward[2] *= -1
        right = np.cross(forward,[0,0,1] if abs(forward[2])<.99 else [0,1,0]); right/=np.linalg.norm(right)
        vertical = np.cross(right,forward)
        axial=vector@forward;up=vector@vertical;lateral=vector@right
    h = np.arctan2(lateral, axial)
    v = np.arctan2(up, np.hypot(lateral, axial))
    d = acoustics.directivity(directivity, f[None, :], h[:, None], v[:, None])
    complete_pattern = directivity.get("kind") in ("omni", "dipole", "cardioid", "complex_grid", "measured_planes")
    if rear is None and not complete_pattern:
        d = d * (axial > 0)[:, None]
    elif rear is not None and not complete_pattern:
        # Blend linearly in cos(polar angle) from the front hemisphere to the shadowed rear one, so the
        # pattern is continuous at 90 degrees instead of stepping to silence there.
        mu = np.clip(axial / distance, -1.0, 1.0)
        behind = np.minimum(mu, 0.0)[:, None]
        gain = rear_gain(rear, f)[None, :]
        d = d * (1 + (gain - 1) * (-behind))
    path = reference_m / distance[:, None] * np.exp(-2j * np.pi * f[None, :] / C * (distance[:, None] - reference_m))
    return reflection * path * d * source[None, :]


def pressure(sections, f, points, reference_m, transfers=None, floor_reflection=None):
    """Coherent sum at points: returns total (points x f) and per-section contributions (sections x points x f)."""
    points = np.atleast_2d(np.asarray(points, float))
    contributions = []
    for index, section in enumerate(sections):
        h = section["transfer"] if transfers is None else transfers[index]
        section_rear = section.get("rear")
        direct = _propagate(f, section["pressure"] * section["baffle"] * h, section["centre"], section["directivity"], section["tilt_rad"], points, reference_m, rear=section_rear, axis=section.get("axis"))
        if floor_reflection:
            direct = direct + _propagate(f, section["pressure"] * section["baffle"] * h, section["centre"], section["directivity"], section["tilt_rad"], points, reference_m, True, floor_reflection, section_rear, section.get("axis"))
        for outlet in section["outlets"]:
            rear = outlet["face"] == "rear"
            src = outlet["pressure"] * outlet["baffle"] * h
            pts = points.copy()
            centre = outlet["centre"].copy()
            outlet_pitch = np.pi if rear else 0.0
            outlet_rear = outlet.get("rear")
            direct = direct + _propagate(f, src, centre, outlet["directivity"], outlet_pitch, pts, reference_m, rear=outlet_rear, axis=outlet.get("axis"))
            if floor_reflection:
                direct = direct + _propagate(f, src, centre, outlet["directivity"], outlet_pitch, pts, reference_m, True, floor_reflection, outlet_rear, outlet.get("axis"))
        contributions.append(direct)
    contributions = np.stack(contributions, axis=0)
    return contributions.sum(axis=0), contributions


def acoustic_crossings(f, per_section_db, band=None):
    """Frequencies where adjacent sections have equal magnitude, with the level of each relative to the louder of the two."""
    rows = []
    for i in range(len(per_section_db) - 1):
        diff = per_section_db[i] - per_section_db[i + 1]
        sign = np.sign(diff)
        change = np.flatnonzero(np.diff(sign) != 0)
        for j in change:
            if band and not (band[0] <= f[j] <= band[1]):
                continue
            t = diff[j] / (diff[j] - diff[j + 1])
            fx = float(np.exp(np.log(f[j]) + t * (np.log(f[j + 1]) - np.log(f[j]))))
            rows.append(dict(lower_section=i, upper_section=i + 1, frequency_hz=fx, level_db=float(np.interp(np.log(fx), np.log(f), per_section_db[i]))))
    return rows
