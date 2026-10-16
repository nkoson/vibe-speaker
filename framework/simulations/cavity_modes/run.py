#!/usr/bin/env python3
"""Internal cavity acoustics of the bass chamber: modes, lining damping, cone loading change and outlet leakage."""
import itertools
import math
import sys
from pathlib import Path

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh, splu
from scipy.special import j1

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, geometry  # noqa: E402
from _common.acoustics import C, RHO, P0  # noqa: E402

NAME = "cavity_modes"
VERSION = "1.1"
NOTES = [
    "Rigid-wall modal model of the rectangular bass chamber: an analytical mode basis (fast) or a 3D finite-volume basis that masks brace windows and port tubes (slower). Lining enters as Miki surface admittance damping on the lined walls only.",
    "cone_deviation_db compares the cone velocity through the cavity model with the lumped box model of lf_box at the same drive; outlet_relative_db is the outlet pressure relative to the cone's mean level in 150 to 300 Hz.",
    "Walls are rigid and static; there is no structural coupling, no absorber propagation model and no nonlinear flow. Convergence figures compare consecutive meshes; you judge whether the change is small enough.",
]


def _geometry(params):
    cav = cli.require(params, "cavity")
    dims = np.array([cli.positive(cav.get("width_mm"), "cavity.width_mm"), cli.positive(cav.get("depth_mm"), "cavity.depth_mm"),
                     cli.positive(cav.get("height_mm"), "cavity.height_mm")]) / 1000
    braces = cav.get("braces") or []
    lining = cav.get("lining") or {}
    driver = cli.require(params, "driver")
    pos = cli.require(driver, "position", label="driver")
    cone = np.array([float(pos["x_mm"]) / 1000, 0.0, float(pos["z_mm"]) / 1000])
    radius = math.sqrt(float(driver["ts"]["sd_cm2"]) * 1e-4 / math.pi)
    outlet = params.get("outlet")
    patches = []
    o_radius = 0.0
    if outlet:
        kind = outlet.get("type", "port")
        face = outlet.get("face", "rear")
        if kind == "port":
            o_radius = cli.positive(outlet.get("inner_diameter_mm"), "outlet.inner_diameter_mm") / 2000
            length = cli.positive(outlet.get("length_mm"), "outlet.length_mm") / 1000
            inner_y = dims[1] - length if face == "rear" else length
            for p in cli.require(outlet, "positions", label="outlet"):
                patches.append(np.array([float(p["x_mm"]) / 1000, inner_y, float(p["z_mm"]) / 1000]))
        elif kind == "passive_radiator":
            pr = acoustics.pr_elements(cli.require(outlet, "radiator", label="outlet"))
            o_radius = math.sqrt(pr["sd"] / math.pi)
            p = cli.require(outlet, "position", label="outlet")
            patches.append(np.array([float(p["x_mm"]) / 1000, dims[1] if face == "rear" else 0.0, float(p["z_mm"]) / 1000]))
        else:
            raise cli.InputError(f"unknown outlet.type '{kind}'")
    return dict(dims=dims, braces=braces, lining=lining, cone=cone, cone_radius=radius, patches=patches, outlet_radius=o_radius,
                outlet=outlet, wall_thickness=float(cav.get("wall_thickness_mm", 18.0)) / 1000)


def rectangular_modes(g, max_hz):
    L = g["dims"]
    indices = np.array(list(itertools.product(*(range(int(2 * max_hz * l / C) + 1) for l in L))))
    k = np.pi * indices / L
    fn = C / (2 * np.pi) * np.linalg.norm(k, axis=1)
    keep = fn <= max_hz
    order = np.argsort(fn[keep])
    indices, k, fn = indices[keep][order], k[keep][order], fn[keep][order]
    norm = np.sqrt(np.prod(np.where(indices == 0, 1., 2.), axis=1))

    def disk(center, radius):
        q = np.hypot(k[:, 0], k[:, 2]) * radius
        average = np.ones_like(q)
        nz = q > 1e-10
        average[nz] = 2 * j1(q[nz]) / q[nz]
        return norm * np.prod(np.cos(k * center), axis=1) * average

    e0 = disk(g["cone"], g["cone_radius"])
    ep = sum(disk(p, g["outlet_radius"]) for p in g["patches"]) / len(g["patches"]) if g["patches"] else np.zeros_like(fn)
    # Lined: both side walls, rear, top and bottom; the front is unlined.
    boundary = 2 * np.where(indices[:, 0] == 0, 1, 2) / L[0] + np.where(indices[:, 1] == 0, 1, 2) / L[1] + 2 * np.where(indices[:, 2] == 0, 1, 2) / L[2]
    return dict(frequency_hz=fn, cone=e0, outlet=ep, boundary_ratio_m_inv=boundary, indices=indices, method="rectangular analytical modes",
                mode_norm=norm)


def finite_volume_modes(g, mesh_mm, max_hz, include_braces=True, include_tubes=True):
    dims = g["dims"]
    edges = []
    for axis, L in enumerate(dims):
        v = list(np.linspace(0, L, int(np.ceil(L / (mesh_mm / 1000))) + 1))
        if include_braces:
            for brace in g["braces"]:
                rim = float(brace.get("rim_mm", 60.0)) / 1000
                if axis < 2:
                    v += [rim, L - rim]
                else:
                    z0 = float(brace["z_mm"]) / 1000
                    v += [z0, z0 + float(brace.get("thickness_mm", 18.0)) / 1000]
        edges.append(np.array(sorted(set(round(x, 9) for x in v if 0 <= x <= L))))
    widths = [np.diff(x) for x in edges]
    centers = [(x[1:] + x[:-1]) / 2 for x in edges]
    X, Y, Z = np.meshgrid(*centers, indexing="ij")
    shape = X.shape
    fluid = np.ones(shape, bool)
    if g.get("assembly"):
        fluid &= geometry.air_mask(g["assembly"], np.stack([X,Y,Z],axis=-1))
    if include_braces:
        for brace in g["braces"]:
            rim = float(brace.get("rim_mm", 60.0)) / 1000
            z0 = float(brace["z_mm"]) / 1000
            z1 = z0 + float(brace.get("thickness_mm", 18.0)) / 1000
            rim_mask = (X < rim) | (X > dims[0] - rim) | (Y < rim) | (Y > dims[1] - rim)
            fluid &= ~((Z >= z0) & (Z < z1) & rim_mask)
    outlet = g["outlet"] or {}
    if include_tubes and outlet.get("type") == "port":
        od = float(outlet.get("outer_diameter_mm", outlet["inner_diameter_mm"] * 1.06)) / 2000
        for p in g["patches"]:
            inside_tube = (X - p[0]) ** 2 + (Z - p[2]) ** 2 < od ** 2
            along = (Y > p[1]) if outlet.get("face", "rear") == "rear" else (Y < p[1])
            fluid &= ~(inside_tube & along)
    ids = np.full(shape, -1, int)
    ids[fluid] = np.arange(np.count_nonzero(fluid))
    n = int(fluid.sum())
    if n < 50:
        raise cli.InputError("finite-volume mesh has fewer than 50 fluid cells; refine mesh_mm")
    volume = (widths[0][:, None, None] * widths[1][None, :, None] * widths[2][None, None, :])[fluid]
    rows, cols, values = [], [], []
    diag = np.zeros(n)
    for axis in range(3):
        a = [slice(None)] * 3
        b = a.copy()
        a[axis] = slice(None, -1)
        b[axis] = slice(1, None)
        a, b = tuple(a), tuple(b)
        ok = fluid[a] & fluid[b]
        ia, ib = ids[a][ok], ids[b][ok]
        distances = np.diff(centers[axis])
        ash = [1, 1, 1]
        ash[axis] = len(distances)
        area = np.ones(shape)
        for other in range(3):
            if other != axis:
                sh = [1, 1, 1]
                sh[other] = len(widths[other])
                area *= widths[other].reshape(sh)
        conductance = (area[a] / distances.reshape(ash))[ok]
        rows.extend([ia, ib])
        cols.extend([ib, ia])
        values.extend([-conductance, -conductance])
        np.add.at(diag, ia, conductance)
        np.add.at(diag, ib, conductance)
    rows.append(np.arange(n))
    cols.append(np.arange(n))
    values.append(diag)
    stiffness = sparse.coo_matrix((np.concatenate(values), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsr()
    mass_inv = sparse.diags(1 / np.sqrt(volume))
    operator = mass_inv @ stiffness @ mass_inv
    estimated = int(4 * np.pi / 3 * np.prod(dims) * (max_hz / C) ** 3 + sum(dims) * max_hz / C * 8 + 25)
    nm = min(n - 2, max(45, estimated))
    eigen, vec = eigsh(operator, k=nm, sigma=-1., which="LM", tol=1e-8, v0=np.random.default_rng(9900).normal(size=n))
    order = np.argsort(eigen)
    eigen = np.maximum(eigen[order], 0)
    vec = vec[:, order]
    fn = C / (2 * np.pi) * np.sqrt(eigen)
    fn[0] = 0
    keep = fn <= max_hz
    fn = fn[keep]
    psi = vec[:, keep] / np.sqrt(volume[:, None]) * math.sqrt(volume.sum())
    coords = np.column_stack([X[fluid], Y[fluid], Z[fluid]])
    face_area = (widths[0][:, None, None] * np.ones(shape) * widths[2][None, None, :])[fluid]
    patch_vectors = []

    def average_patch(x, z, r, y, front=False):
        plane = 0 if front else min(len(centers[1]) - 1, max(0, np.searchsorted(centers[1], y) - (0 if y >= dims[1] else 0)))
        if not front and y < dims[1]:
            plane = max(0, np.searchsorted(centers[1], y) - 1)
        if not front and y >= dims[1]:
            plane = len(centers[1]) - 1
        choose = (np.abs(coords[:, 1] - centers[1][plane]) < 1e-8) & ((coords[:, 0] - x) ** 2 + (coords[:, 2] - z) ** 2 <= r * r)
        if not np.any(choose):
            raise cli.InputError("a source patch found no fluid cells; check positions against braces and tubes")
        weight = face_area[choose]
        vector = np.zeros(n)
        vector[choose] = weight / weight.sum()
        patch_vectors.append(vector)
        return vector @ psi

    e0 = average_patch(g["cone"][0], g["cone"][2], g["cone_radius"], 0.0, True)
    if g["patches"]:
        ep = sum(average_patch(p[0], p[2], g["outlet_radius"], p[1], p[1] <= 1e-9) for p in g["patches"]) / len(g["patches"])
        patches = np.column_stack([patch_vectors[0], np.mean(patch_vectors[1:], axis=0)])
    else:
        ep = np.zeros_like(fn)
        patches = patch_vectors[0][:, None]
    rhs = patches - volume[:, None] / volume.sum()
    potential = np.zeros_like(rhs)
    potential[1:] = splu(stiffness[1:, 1:].tocsc()).solve(rhs[1:])
    potential -= volume @ potential / volume.sum()
    static_fields = volume.sum() / C ** 2 * potential
    static_matrix = patches.T @ static_fields
    boundary = np.zeros(n)
    for axis, side in [(0, 0), (0, -1), (1, -1), (2, 0), (2, -1)]:
        selection = [slice(None)] * 3
        selection[axis] = side
        selection = tuple(selection)
        area = np.ones(shape)
        for other in range(3):
            if other != axis:
                sh = [1, 1, 1]
                sh[other] = len(widths[other])
                area *= widths[other].reshape(sh)
        valid = fluid[selection].copy()
        np.add.at(boundary, ids[selection][valid], area[selection][valid])
    ratio = boundary @ (psi * psi) / volume.sum()
    return dict(frequency_hz=fn, cone=e0, outlet=ep, boundary_ratio_m_inv=ratio, method="3D finite-volume modes", cells=n, mesh_mm=mesh_mm,
                modeled_air_volume_l=float(volume.sum() * 1000), static_matrix=static_matrix, static_fields=static_fields, coords=coords, psi=psi,
                volume=volume, outlet_count=len(g["patches"]))


def acoustic_response(g, params, basis, f, lined=True):
    ts = params["driver"]["ts"]
    enclosure = cli.require(params, "enclosure")
    net_l = cli.positive(enclosure.get("net_volume_l"), "enclosure.net_volume_l")
    ql = float(enclosure.get("ql", 10.0))
    drive = params.get("drive") or {}
    voltage = float(drive.get("voltage_rms", 2.83))
    series_r = float(drive.get("series_resistance_ohm", 0.0))
    s = 1j * 2 * np.pi * f
    w = 2 * np.pi * f
    fn = basis["frequency_hz"]
    wn = 2 * np.pi * fn
    lining = g["lining"]
    sigma = float(lining.get("flow_resistivity_pas_m2", 10000.0))
    thickness = float(lining.get("thickness_mm", 0.0)) if lined else 0.0
    background_q = float(g.get("unlined_background_q", 30.0))
    fm = np.maximum(fn, sigma * .010001)
    y = acoustics.lining_admittance(fm, thickness, sigma)
    damping = wn / background_q + C * np.maximum(y.real, 0) * basis["boundary_ratio_m_inv"]
    outlet = g["outlet"] or {}
    kind = outlet.get("type") if outlet else None
    fb = float(enclosure.get("tuning_hz", ts["fs_hz"]))
    damping[0] = 2 * np.pi * fb / ql if kind != "port" else 0.0
    denom = wn[None, :] ** 2 - w[:, None] ** 2 + 1j * w[:, None] * damping
    kernel = s[:, None] * RHO * C * C / (net_l / 1000) / denom
    ec, ep = basis["cone"], basis["outlet"]
    zcc = kernel @ (ec * ec)
    zcp = kernel @ (ec * ep)
    zpp = kernel @ (ep * ep)
    residual_fields = None
    if "static_matrix" in basis:
        couplings = np.column_stack([ec, ep]) if kind else ec[:, None]
        nz = wn > 0
        retained = couplings[nz].T @ (couplings[nz] / wn[nz, None] ** 2)
        residual = basis["static_matrix"] - retained
        factor = s * RHO * C * C / (net_l / 1000)
        zcc = zcc + factor * residual[0, 0]
        if kind:
            zcp = zcp + factor * residual[0, 1]
            zpp = zpp + factor * residual[1, 1]
        residual_fields = basis["static_fields"] - basis["psi"][:, nz] @ (couplings[nz] / wn[nz, None] ** 2)
    outlet_transfer = np.ones_like(s)
    if kind == "port":
        radius = g["outlet_radius"]
        area = len(g["patches"]) * math.pi * radius ** 2
        length = float(outlet["length_mm"]) / 1000 + .61 * radius
        qp = float(outlet.get("qp", enclosure.get("qp", 20.0)))
        gamma = 2 * np.pi * fb / (C * qp) + 1j * w / C
        z0 = RHO * C / area
        ka = np.maximum(w / C * radius, 1e-9)
        radiation = z0 * acoustics.piston_radiation_impedance(f, radius)
        ta = np.cosh(gamma * length)
        tb = z0 * np.sinh(gamma * length)
        tc = np.sinh(gamma * length) / z0
        termination = (ta * radiation + tb) / (tc * radiation + ta)
        outlet_transfer = 1 / (tc * radiation + ta)
        box = zcc - zcp * zcp / (zpp + termination)
    elif kind == "passive_radiator":
        pr = acoustics.pr_elements(outlet["radiator"])
        added = outlet.get("added_mass_g")
        if added is None:
            added = acoustics.pr_added_mass(net_l, fb, outlet["radiator"])["required_added_mass_g"]
        termination = (pr["rmp"] + s * (pr["mmp"] + float(added) / 1000) + 1 / (s * pr["cmp"])) / pr["sd"] ** 2
        box = zcc - zcp * zcp / (zpp + termination)
    else:
        termination = None
        box = zcc
    e = acoustics.driver_elements(ts)
    zm = e["rms"] + s * e["mms"] + 1 / (s * e["cms"]) + e["sd"] ** 2 * box
    ze = e["re"] + series_r + s * e["le"]
    transfer = np.ones_like(s)
    if drive.get("terminal_transfer"):
        transfer = cli.curve_from_reference(drive["terminal_transfer"], params["_base_dir"], f)
    velocity = e["bl"] * voltage * transfer / (ze * zm + e["bl"] ** 2)
    uc = e["sd"] * velocity
    if termination is not None:
        up = -zcp * uc / (zpp + termination)
    else:
        up = np.zeros_like(uc)
    uout = up * outlet_transfer
    pcone = s * RHO * uc / (2 * np.pi)
    pout = s * RHO * uout / (2 * np.pi)
    lumped_type = "vented" if kind == "port" else "passive_radiator" if kind == "passive_radiator" else "sealed"
    lumped_enclosure = dict(type=lumped_type, net_volume_l=net_l, tuning_hz=fb, ql=ql, qp=float(enclosure.get("qp", 20.0)))
    if kind == "port":
        lumped_enclosure["port"] = dict(diameter_mm=float(outlet["inner_diameter_mm"]), count=len(g["patches"]))
    if kind == "passive_radiator":
        lumped_enclosure["radiator"] = outlet["radiator"]
        lumped_enclosure["added_mass_g"] = added
    lumped = acoustics.box_response(ts, lumped_enclosure, f, voltage, series_r, "half", transfer)
    ref_velocity = lumped["excursion_peak_mm"] / 1000 / np.sqrt(2) * w
    deviation = 20 * np.log10(np.maximum(np.abs(velocity), 1e-30) / np.maximum(ref_velocity, 1e-30))
    refmask = (f >= 150) & (f <= 300)
    reference = float(np.mean(20 * np.log10(np.maximum(np.abs(pcone[refmask]), 1e-30) / P0))) if np.any(refmask) else float(np.mean(20 * np.log10(np.maximum(np.abs(pcone), 1e-30) / P0)))
    outlet_db = 20 * np.log10(np.maximum(np.abs(pout), 1e-30) / P0) - reference
    coeff = kernel * (-uc[:, None] * ec + (-up)[:, None] * ep)
    residual_strengths = (s * RHO * C * C / (net_l / 1000))[:, None] * (np.column_stack([-uc, -up]) if kind else (-uc)[:, None])
    result = dict(f_hz=f, cone_deviation_db=deviation, outlet_relative_db=outlet_db, cone_pressure_pa=pcone, outlet_pressure_pa=pout,
                  box_pressure_at_cone_pa=box * uc, driver_z_ohm=ze + e["bl"] ** 2 / zm, mode_coefficients=coeff, damping=damping,
                  q_modes=np.divide(wn, damping, out=np.zeros_like(wn), where=damping > 0), residual_fields=residual_fields,
                  residual_strengths=residual_strengths, lumped_spl_db=lumped["spl_db"],
                  cavity_spl_db=20 * np.log10(np.maximum(np.abs(pcone + pout), 1e-30) / P0), has_outlet=bool(kind))
    if kind == "passive_radiator":
        result["radiator_excursion_peak_mm"] = np.sqrt(2) * np.abs(up / (s * pr["sd"])) * 1000
    return result


def pressure_field(basis, r, selection):
    field = basis["psi"] @ r["mode_coefficients"][selection].T
    if r.get("residual_fields") is not None:
        field += r["residual_fields"] @ r["residual_strengths"][selection].T
    return field


def _summary(basis, r, f):
    band = (f >= 150) & (f <= 1000)
    leakage = f >= 300
    out = dict(method=basis["method"], mode_count=int(len(basis["frequency_hz"])), first_modes_hz=basis["frequency_hz"][1:11],
               modes=[dict(frequency_hz=float(fn), q_lined=float(q), cone_coupling=float(c), outlet_coupling=float(o))
                      for fn, q, c, o in zip(basis["frequency_hz"], r["q_modes"], basis["cone"], basis["outlet"])][:60],
               max_abs_cone_deviation_150_1000_db=float(np.max(np.abs(r["cone_deviation_db"][band]))) if np.any(band) else None,
               cone_deviation_at_max_hz=float(f[band][np.argmax(np.abs(r["cone_deviation_db"][band]))]) if np.any(band) else None)
    if r["has_outlet"] and np.any(leakage):
        out["max_outlet_leakage_above_300_db"] = float(np.max(r["outlet_relative_db"][leakage]))
        out["outlet_leakage_max_hz"] = float(f[leakage][np.argmax(r["outlet_relative_db"][leakage])])
    if "cells" in basis:
        out.update(cells=basis["cells"], mesh_mm=basis["mesh_mm"], modeled_air_volume_l=basis["modeled_air_volume_l"])
        envelope = np.concatenate([np.max(np.abs(pressure_field(basis, r, slice(i, i + 80))), axis=0) for i in range(0, len(f), 80)])
        out["pressure_envelope_rms_pa"] = envelope
        out["max_cell_pressure_rms_pa"] = float(envelope.max())
        out["max_cell_pressure_hz"] = float(f[np.argmax(envelope)])
    else:
        bound = np.abs(r["mode_coefficients"]) @ basis["mode_norm"]
        out["pressure_envelope_rms_pa"] = bound
        out["max_cell_pressure_rms_pa"] = float(bound.max())
        out["pressure_envelope_note"] = "analytical triangle-inequality bound over the whole cavity"
    return out


VALIDITY = [
    "Interior acoustics of the air in the chamber. It does not radiate: what leaves through the panels is plate_structure's question and what leaves through the port is lf_box's.",
    "The lining model is a damping admittance on a rigidly backed porous layer, so it is valid where the layer is thin compared with a wavelength and is not a model of bulk stuffing filling the box.",
    "Above the first modes the modal density rises and a mesh that resolved the lowest modes no longer resolves these; read the convergence figures before quoting a high-order mode.",
    "The finite-volume basis is a wave-based solve, so the elements-per-wavelength rule applies to it: h = c P / (10 f_max) at shape-function order P, which is 1 for this scheme. The rule addresses interpolation error only - the pollution term of the error bound carries an extra factor of k, so a mesh that is adequate at the lowest modes is progressively less adequate as frequency rises. That is what the mesh convergence figures are for.",
]


def compute(params, base_dir):
    params = dict(params, _base_dir=base_dir)
    g = _geometry(params)
    if params.get("assembly"):
        g["assembly"] = geometry.load_assembly(params["assembly"], base_dir)
    g["unlined_background_q"] = float((params.get("cavity") or {}).get("unlined_background_q", 30.0))
    method = params.get("method") or {}
    kind = method.get("kind", "rectangular")
    max_hz = float(method.get("max_mode_hz", 1800.0))
    default_f = np.concatenate([np.geomspace(20, 100, 81)[:-1], np.linspace(100, max_hz, 551)])
    f = cli.frequency_grid(params.get("frequencies"), 20, max_hz, 631) if params.get("frequencies") else default_f
    bases = []
    if kind == "rectangular":
        bases.append(rectangular_modes(g, max_hz))
    elif kind == "fvm":
        meshes = method.get("mesh_mm", [35.0])
        if not isinstance(meshes, list):
            meshes = [meshes]
        for mesh in meshes:
            bases.append(finite_volume_modes(g, float(mesh), max_hz, bool(method.get("include_braces", True)), bool(method.get("include_port_tubes", True))))
    else:
        raise cli.InputError("method.kind must be rectangular or fvm")
    responses = [acoustic_response(g, params, b, f) for b in bases]
    fine_basis, fine = bases[-1], responses[-1]
    results = dict(f_hz=f, geometry=dict(inside_dims_mm=g["dims"] * 1000, cone_center_mm=g["cone"] * 1000, cone_radius_mm=g["cone_radius"] * 1000,
                                         outlet_centers_mm=[p * 1000 for p in g["patches"]], outlet_radius_mm=g["outlet_radius"] * 1000),
                   bases=[_summary(b, r, f) for b, r in zip(bases, responses)],
                   cone_deviation_db=fine["cone_deviation_db"], outlet_relative_db=fine["outlet_relative_db"],
                   cavity_spl_db=fine["cavity_spl_db"], lumped_spl_db=fine["lumped_spl_db"], driver_z_ohm=fine["driver_z_ohm"],
                   box_pressure_at_cone_pa=fine["box_pressure_at_cone_pa"], pressure_envelope_rms_pa=results_envelope(bases, responses, f))
    terminal_params = dict(params, drive=dict(voltage_rms=1., series_resistance_ohm=0.))
    terminal = acoustic_response(g, terminal_params, fine_basis, f)
    results.update(pressure_per_volt_pa=terminal["cone_pressure_pa"],
                   outlet_pressure_per_volt_pa=terminal["outlet_pressure_pa"], z_ohm=terminal["driver_z_ohm"],
                   source_contract=dict(phase_reference="intrinsic", pressure_reference_m=1.,
                                        baffle="external", normalization="driver_terminal_volt", radiation_space="half"))
    if params.get("export_complex_field") and "psi" in fine_basis:
        results["complex_field"] = dict(coordinates_m=fine_basis["coords"], pressure_pa=pressure_field(fine_basis, fine, np.arange(len(f))).T)
    if "radiator_excursion_peak_mm" in fine:
        results["radiator_excursion_peak_mm"] = fine["radiator_excursion_peak_mm"]
    unlined = acoustic_response(g, params, fine_basis, f, lined=False)
    results["unlined_comparison"] = dict(cone_deviation_db=unlined["cone_deviation_db"], outlet_relative_db=unlined["outlet_relative_db"],
                                         max_abs_cone_deviation_150_1000_db=_summary(fine_basis, unlined, f)["max_abs_cone_deviation_150_1000_db"])
    if len(bases) > 1:
        coarse, fine_r = responses[-2], responses[-1]
        first_c, first_f = bases[-2]["frequency_hz"][1:11], bases[-1]["frequency_hz"][1:11]
        n = min(len(first_c), len(first_f))
        leak = f >= 300
        results["mesh_convergence"] = dict(meshes_mm=[b["mesh_mm"] for b in bases],
                                           first_modes_max_relative_change_percent=float(np.max(np.abs(first_f[:n] - first_c[:n]) / first_f[:n]) * 100) if n else None,
                                           cone_deviation_max_change_db=float(np.max(np.abs(fine_r["cone_deviation_db"] - coarse["cone_deviation_db"]))),
                                           outlet_leakage_max_change_db=float(np.max(np.abs(fine_r["outlet_relative_db"][leak] - coarse["outlet_relative_db"][leak]))) if fine_r["has_outlet"] else None)
    results["validity"] = dict(statements=list(VALIDITY), method=kind, max_mode_hz=max_hz,
                               evaluated_band_hz=[float(f[0]), float(f[-1])])
    if kind == "fvm":
        rule = acoustics.mesh_rule(max_hz, order=1)
        results["validity"]["mesh_rule"] = dict(
            rule, meshes_used_mm=[b["mesh_mm"] for b in bases],
            finest_mesh_inside_rule=bool(min(b["mesh_mm"] for b in bases) <= rule["max_element_size_mm"]),
            note="a finite-volume cell is a first-order element, so P = 1 and the allowance is c / (10 f_max). "
                 "Quadratic elements would allow twice the cell size for the same degrees of freedom per wavelength.")
    sections = params.get("field_sections")
    if sections and "psi" in fine_basis:
        coords = fine_basis["coords"]
        x_target = float(sections.get("x_mm", (g["patches"][0][0] * 1000 if g["patches"] else g["cone"][0] * 1000))) / 1000
        unique = np.unique(coords[:, 0])
        x = unique[np.argmin(np.abs(unique - x_target))]
        mask = np.abs(coords[:, 0] - x) < 1e-8
        rows = []
        for target in sections.get("frequencies_hz", [50, 100, 500, 1000]):
            index = int(np.argmin(np.abs(f - target)))
            field = pressure_field(fine_basis, fine, index)
            rows.append(dict(frequency_hz=float(f[index]), section_x_mm=float(x * 1000), y_mm=coords[mask, 1] * 1000, z_mm=coords[mask, 2] * 1000,
                             pressure_rms_pa=np.abs(field[mask]), relative_to_max_db=20 * np.log10(np.maximum(np.abs(field[mask]), 1e-12) / max(np.abs(field).max(), 1e-12))))
        results["field_sections"] = rows
    return results


def results_envelope(bases, responses, f):
    summary = _summary(bases[-1], responses[-1], f)
    return summary["pressure_envelope_rms_pa"]


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Internal cavity acoustics of the bass chamber", NOTES, VALIDITY))
