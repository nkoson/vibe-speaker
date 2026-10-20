"""Linear acoustic and electrical building blocks shared by the simulations (SI units).

Phasors are complex RMS. Excursion and air speed outputs are sine peak values
where named so. Nothing here is nonlinear, thermal or measured.
"""
import math

import numpy as np
from scipy.special import j1, struve

from .cli import InputError, positive, RHO, C, P0, MU  # noqa: F401  (re-exported: one definition, in cli)
from .driver_models import blocked_impedance, mechanical_impedance


def driver_elements(ts):
    """Lumped elements from Thiele/Small data: Sd, Cms, Mms (includes radiation mass), Rms, Bl, Re, Le."""
    for key in ("fs_hz", "vas_l", "qms", "qes", "re_ohm", "sd_cm2"):
        positive(ts.get(key), f"driver.{key}")
    sd = ts["sd_cm2"] * 1e-4
    cms = ts["vas_l"] * 1e-3 / (RHO * C * C * sd * sd)
    ws = 2 * np.pi * ts["fs_hz"]
    mms = 1 / (ws * ws * cms)
    rms = ws * mms / ts["qms"]
    bl = math.sqrt(ws * mms * ts["re_ohm"] / ts["qes"])
    qts = 1 / (1 / ts["qes"] + 1 / ts["qms"])
    return dict(sd=sd, cms=cms, mms=mms, rms=rms, bl=bl, re=float(ts["re_ohm"]),
                le=float(ts.get("le_mh", 0.0)) * 1e-3, qts=qts)


def vent_geometry(net_l, fb_hz, diameter_mm, count=1):
    """Straight round duct: total area, effective length and physical length with a 0.732 d end correction."""
    area = count * np.pi * (diameter_mm / 2000) ** 2
    effective = C * C * area / ((2 * np.pi * fb_hz) ** 2 * (net_l / 1000))
    physical = effective - 0.732 * diameter_mm / 1000
    return dict(area_m2=float(area), effective_length_mm=float(effective * 1000), physical_length_mm=float(physical * 1000),
                diameter_mm=float(diameter_mm), count=int(count))


def pr_elements(radiator):
    """Passive radiator mechanical elements without added mass: Sd, Mmp, Cmp, Rmp."""
    ts = radiator
    for key in ("fp_hz", "vap_l", "mmp_g", "qmp", "sd_cm2"):
        positive(ts.get(key), f"radiator.{key}")
    sd = ts["sd_cm2"] * 1e-4
    mmp = ts["mmp_g"] * 1e-3
    cmp_ = ts["vap_l"] * 1e-3 / (RHO * C * C * sd * sd)
    return dict(sd=sd, mmp=mmp, cmp=cmp_, rmp=2 * np.pi * ts["fp_hz"] * mmp / ts["qmp"], fp_hz=float(ts["fp_hz"]))


def pr_added_mass(net_l, fb_hz, radiator):
    """Added mass that tunes one passive radiator to fb_hz in net_l; the suspension null frequency follows.

    Mass can only be added, so the bare radiator's own in-box resonance is the highest tuning the part
    can reach in this volume. A required mass below zero means the requested tuning is above it, and
    the caller has to decide what to do; nothing is clamped here.
    """
    d = pr_elements(radiator)
    cb = net_l / 1000 / (RHO * C * C)
    stiffness = 1 / d["cmp"] + d["sd"] ** 2 / cb
    required = (stiffness / (2 * np.pi * fb_hz) ** 2 - d["mmp"]) * 1000
    total = d["mmp"] + required / 1000
    maximum = math.sqrt(stiffness / d["mmp"]) / (2 * np.pi)
    out = dict(required_added_mass_g=float(required), realizable=bool(required >= 0.0),
               maximum_tuning_hz=float(maximum))
    if required >= 0.0:
        out.update(total_moving_mass_g=float(total * 1000),
                   null_hz=float(1 / (2 * np.pi * math.sqrt(total * d["cmp"]))),
                   tuning_sensitivity_hz_per_g=float(-fb_hz / (2 * total) * 0.001))
    else:
        out.update(total_moving_mass_g=None, null_hz=None, tuning_sensitivity_hz_per_g=None)
    return out


def chamber_network(spec, f, reference_hz, label="chamber"):
    """One bandpass chamber as an acoustic impedance, with its vent branch and any chamber behind it.

    The component-value method is the one the vented box already uses, applied per chamber:

        CAB  = VB / (rho0 c^2)          LMAP = 1 / ((2 pi fB)^2 CAB)        RAL = QL / (2 pi fB CAB)

    A vent either opens into the room or feeds a further chamber, in which case that chamber's
    impedance is in series with the port mass. Nesting is how a sixth- and an eighth-order box are
    built, so the recursion is the topology: order = 2 (1 + vents).
    """
    f = np.asarray(f, float)
    s = 2j * np.pi * f
    volume = positive((spec or {}).get("volume_l"), f"{label}.volume_l") / 1000
    ql = positive(spec.get("ql", 10.0), f"{label}.ql")
    cab = volume / (RHO * C * C)
    record = dict(label=label, volume_l=volume * 1000, cab_m3_per_pa=cab, ql=ql,
                  leak_reference_hz=float(reference_hz))
    admittance = s * cab + 1 / (ql / (2 * np.pi * float(reference_hz) * cab))
    record["ral_pa_s_per_m3"] = float(ql / (2 * np.pi * float(reference_hz) * cab))
    vent = spec.get("vent")
    branch = None
    if vent:
        fb = positive(vent.get("tuning_hz"), f"{label}.vent.tuning_hz")
        qp = positive(vent.get("qp", 20.0), f"{label}.vent.qp")
        lmap = 1 / ((2 * np.pi * fb) ** 2 * cab)
        z_port = 2 * np.pi * fb * lmap / qp + s * lmap
        geometry = vent_geometry(volume * 1000, fb, positive(vent.get("diameter_mm"), f"{label}.vent.diameter_mm"),
                                 int(vent.get("count", 1)))
        child = None
        z_branch = z_port
        if vent.get("into"):
            # a nested chamber's leakage is referred to its own tuning where it has one, and to the
            # port feeding it where it is sealed: there is no third frequency in the circuit
            child_spec = vent["into"]
            child = chamber_network(child_spec, f, (child_spec.get("vent") or {}).get("tuning_hz") or fb,
                                    f"{label}.into")
            z_branch = z_port + child["z"]
        # a port is open at both ends: its first pipe resonance is the half-wave one on the end-corrected
        # length, and the lumped-mass model under-states the port flow by 3.9 dB at the quarter-wave point
        realizable = geometry["physical_length_mm"] > 0
        effective_m = geometry["effective_length_mm"] / 1000
        branch = dict(tuning_hz=fb, qp=qp, lmap_kg_per_m4=float(lmap), z_port=z_port, z_branch=z_branch,
                      geometry=geometry, child=child, radiates_to_room=child is None,
                      pipe_resonance_hz=C / (2 * effective_m) if realizable else None,
                      lumped_limit_hz=C / (4 * effective_m) if realizable else None)
        admittance = admittance + 1 / z_branch
    record["has_vent"] = branch is not None
    return dict(z=1 / admittance, cab=cab, record=record, branch=branch)


def chamber_flows(node, pressure, out=None):
    """Volume velocity through every vent of a chamber tree, and which of them reach the room."""
    out = [] if out is None else out
    branch = node["branch"]
    if branch is not None:
        flow = pressure / branch["z_branch"]
        out.append(dict(label=node["record"]["label"], tuning_hz=branch["tuning_hz"], flow=flow,
                        geometry=branch["geometry"], radiates_to_room=branch["radiates_to_room"],
                        pipe_resonance_hz=branch["pipe_resonance_hz"], lumped_limit_hz=branch["lumped_limit_hz"],
                        chamber_volume_l=node["record"]["volume_l"]))
        if branch["child"] is not None:
            chamber_flows(branch["child"], flow * branch["child"]["z"], out)
    return out


def count_vents(node):
    branch = node["branch"]
    if branch is None:
        return 0
    return 1 + (count_vents(branch["child"]) if branch["child"] is not None else 0)


def bandpass_response(ts, enclosure, f, voltage_rms=2.83, series_r=0.0, space="half", terminal_transfer=None):
    """Bandpass box of any order: the driver radiates into its chambers only, the ports radiate.

    enclosure: {"type": "bandpass", "rear": {...}, "front": {...}} where each chamber is
    {"volume_l", "ql", "vent": {"tuning_hz", "diameter_mm", "count", "qp", "into": {chamber}}}.
    A sealed rear chamber and one front vent is the fourth-order box; venting the rear as well, or
    nesting a second chamber behind a front vent, gives the sixth; both give the eighth.

    No alignment table is used anywhere here - none was obtained for any bandpass family. This
    solves the circuit for the geometry it is given and reports what came out.
    """
    f = np.asarray(f, float)
    d = driver_elements(ts)
    s = 2j * np.pi * f
    solid = 2 * np.pi if space == "half" else 4 * np.pi
    chambers = {}
    for name in ("rear", "front"):
        spec = enclosure.get(name)
        if not spec:
            raise InputError(f"a bandpass box needs enclosure.{name} with at least volume_l")
        tuning = (spec.get("vent") or {}).get("tuning_hz")
        # a sealed chamber has no tuning of its own, so its leakage is referred to the driver's
        # resonance in that chamber, which is the frequency the sealed-box model uses
        reference = tuning or float(ts["fs_hz"]) * math.sqrt(1 + float(ts["vas_l"]) / float(spec["volume_l"]))
        chambers[name] = chamber_network(spec, f, reference, name)
    z_load = chambers["rear"]["z"] + chambers["front"]["z"]
    zm = mechanical_impedance(ts, f, d) + d["sd"] ** 2 * z_load
    ze = blocked_impedance(ts, f) + series_r
    vin = voltage_rms * (np.ones_like(s) if terminal_transfer is None else np.asarray(terminal_transfer, complex))
    v = d["bl"] * vin / (ze * zm + d["bl"] ** 2)
    current = (vin - d["bl"] * v) / ze
    ucone = d["sd"] * v
    # the cone injects +ucone into the front chamber and -ucone into the rear one
    flows = chamber_flows(chambers["front"], ucone * chambers["front"]["z"]) + \
        chamber_flows(chambers["rear"], -ucone * chambers["rear"]["z"])
    radiating = [row for row in flows if row["radiates_to_room"]]
    if not radiating:
        raise InputError("no vent of this bandpass box opens into the room, so nothing is radiated; "
                         "give the outermost chamber a vent without 'into'")
    pressure = sum(s * RHO * row["flow"] / solid for row in radiating)
    ports = []
    for row in flows:
        speed = np.sqrt(2) * np.abs(row["flow"]) / row["geometry"]["area_m2"]
        ports.append(dict(chamber=row["label"], tuning_hz=row["tuning_hz"], vent=row["geometry"],
                          radiates_to_room=row["radiates_to_room"], air_speed_peak_ms=speed,
                          pipe_resonance_hz=row["pipe_resonance_hz"], lumped_limit_hz=row["lumped_limit_hz"],
                          chamber_volume_l=row["chamber_volume_l"]))
    order = 2 * (1 + count_vents(chambers["front"]) + count_vents(chambers["rear"]))
    result = dict(f_hz=f, pressure_pa=pressure, outlet_pressure_pa=pressure,
                  cone_pressure_pa=np.zeros(len(f), complex),
                  z_ohm=ze + d["bl"] ** 2 / zm - series_r,
                  excursion_peak_mm=np.sqrt(2) * abs(v / s) * 1000,
                  copper_loss_w=abs(current) ** 2 * d["re"], current_rms_a=abs(current), elements=d,
                  port_air_speed_peak_ms=np.max([p["air_speed_peak_ms"] for p in ports if p["radiates_to_room"]], axis=0),
                  bandpass=dict(
                      order=order, ports=ports,
                      chambers=[chambers["rear"]["record"], chambers["front"]["record"]],
                      order_note="order = 2 (1 + vents), counted from the topology: a sealed rear chamber contributes a "
                                 "second-order high-pass and every vent a further second-order section.",
                      cone_radiates_directly=False,
                      alignment_note="no bandpass alignment tables - the equivalent of Small's B4, QB3 and BL4 families - "
                                     "were obtained from any source. This is a circuit solved for a chosen geometry, not a "
                                     "looked-up alignment, and a result document must say so rather than implying one."))
    result["spl_db"] = 20 * np.log10(np.maximum(abs(pressure), 1e-30) / P0)
    return result


def box_response(ts, enclosure, f, voltage_rms=2.83, series_r=0.0, space="half", terminal_transfer=None):
    """Lumped response of a cone in a sealed, vented or passive-radiator box.

    enclosure: {"type": "sealed"|"vented"|"aperiodic"|"passive_radiator"|"bandpass", "net_volume_l", "tuning_hz",
                "ql", "qp", "port": {"diameter_mm", "count"}, "radiator": {...}, "added_mass_g",
                "rav_pa_s_per_m3" for the aperiodic vent}
    A bandpass enclosure is handed to bandpass_response, which has its own chamber description.
    Returns pressures at 1 m, SPL, impedance, excursion, port speed or radiator excursion, losses.
    """
    f = np.asarray(f, float)
    if enclosure.get("type") == "bandpass":
        return bandpass_response(ts, enclosure, f, voltage_rms, series_r, space, terminal_transfer)
    d = driver_elements(ts)
    kind = enclosure.get("type", "vented")
    net_l = positive(enclosure.get("net_volume_l"), "enclosure.net_volume_l")
    ql = positive(enclosure.get("ql", 10.0), "enclosure.ql")
    w = 2 * np.pi * f
    s = 1j * w
    cb = net_l / 1000 / (RHO * C * C)
    solid = 2 * np.pi if space == "half" else 4 * np.pi
    extra = {}
    if kind == "sealed":
        wc = 2 * np.pi * ts["fs_hz"] * math.sqrt(1 + ts["vas_l"] / net_l)
        rl = ql / (wc * cb)
        zb = 1 / (s * cb + 1 / rl)
        zp = None
        extra["system_resonance_hz"] = float(wc / (2 * np.pi))
        extra["qtc"] = float(d["qts"] * math.sqrt(1 + ts["vas_l"] / net_l))
    else:
        fb = positive(enclosure.get("tuning_hz"), "enclosure.tuning_hz")
        wb = 2 * np.pi * fb
        rl = ql / (wb * cb)
        if kind in ("vented", "aperiodic"):
            qp = positive(enclosure.get("qp", 20.0), "enclosure.qp")
            mp = 1 / (wb * wb * cb)
            zp = wb * mp / qp + s * mp
            if kind == "aperiodic":
                # one series resistance in the vent branch spans the two familiar loadings: infinite
                # RAV carries no volume velocity and is the sealed box, zero RAV is the vented box.
                rav = positive(enclosure.get("rav_pa_s_per_m3"), "enclosure.rav_pa_s_per_m3", zero=True)
                zp = zp + rav
                extra["aperiodic"] = dict(rav_pa_s_per_m3=rav, vented_limit_rav=0.0,
                                          sealed_limit_rav="infinite",
                                          note="RAV has no source. No relation between stuffing density or vent-covering "
                                               "material and an SI acoustic resistance was obtained, and nothing "
                                               "establishes whether the resistance is usefully constant with frequency or "
                                               "level. A single RAV is an exploration, never a prediction.")
            port = enclosure.get("port") or {}
            vent = vent_geometry(net_l, fb, positive(port.get("diameter_mm"), "enclosure.port.diameter_mm"), int(port.get("count", 1)))
            extra["vent"] = vent
        elif kind == "passive_radiator":
            radiator = enclosure.get("radiator") or {}
            pr = pr_elements(radiator)
            mass = pr_added_mass(net_l, fb, radiator)
            added = float(enclosure.get("added_mass_g", mass["required_added_mass_g"]))
            if added < 0.0:
                raise InputError(
                    f"enclosure.tuning_hz {fb:g} Hz needs {added:.1f} g of added radiator mass, and mass can only "
                    f"be added: this radiator in {net_l:g} L reaches at most {mass['maximum_tuning_hz']:.2f} Hz. "
                    "Ask for a lower tuning, use a lighter or stiffer radiator, change the volume, or set "
                    "enclosure.added_mass_g explicitly and read results.radiator.actual_tuning_hz.")
            total_mass = pr["mmp"] + added / 1000
            zp = (pr["rmp"] + s * total_mass + 1 / (s * pr["cmp"])) / pr["sd"] ** 2
            extra["radiator"] = dict(mass, added_mass_used_g=float(added),
                                     actual_tuning_hz=float(math.sqrt((1 / pr["cmp"] + pr["sd"] ** 2 / cb) / total_mass) / (2 * np.pi)))
        else:
            raise InputError(f"unknown enclosure.type '{kind}'")
        zb = 1 / (s * cb + 1 / rl + 1 / zp)
    zm = mechanical_impedance(ts, f, d) + d["sd"] ** 2 * zb
    ze = blocked_impedance(ts, f) + series_r
    vin = voltage_rms * (np.ones_like(s) if terminal_transfer is None else np.asarray(terminal_transfer, complex))
    v = d["bl"] * vin / (ze * zm + d["bl"] ** 2)
    current = (vin - d["bl"] * v) / ze
    ucone = d["sd"] * v
    p_cone = s * RHO * ucone / solid
    result = dict(f_hz=f, cone_pressure_pa=p_cone, z_ohm=ze + d["bl"] ** 2 / zm - series_r,
                  excursion_peak_mm=np.sqrt(2) * abs(v / s) * 1000,
                  copper_loss_w=abs(current) ** 2 * d["re"], current_rms_a=abs(current), elements=d, **extra)
    if zp is None:
        result["pressure_pa"] = p_cone
    else:
        uport = -zb * ucone / zp
        p_out = s * RHO * uport / solid
        result["pressure_pa"] = p_cone + p_out
        result["outlet_pressure_pa"] = p_out
        if kind in ("vented", "aperiodic"):
            result["port_air_speed_peak_ms"] = np.sqrt(2) * abs(uport) / extra["vent"]["area_m2"]
        else:
            result["radiator_excursion_peak_mm"] = np.sqrt(2) * abs(uport / (s * pr["sd"])) * 1000
    result["spl_db"] = 20 * np.log10(np.maximum(abs(result["pressure_pa"]), 1e-30) / P0)
    return result


def sealed_volume_for_qtc(ts, qtc):
    d = driver_elements(ts)
    if d["qts"] >= qtc:
        raise InputError(f"driver Qts {d['qts']:.3f} is not below the requested Qtc {qtc:g}")
    return float(ts["vas_l"] / ((qtc / d["qts"]) ** 2 - 1))


def lining_admittance(f, thickness_mm, resistivity):
    """Miki surface admittance of a rigidly backed porous layer; damping only."""
    f = np.asarray(f, float)
    if thickness_mm <= 0:
        return np.zeros_like(f, dtype=complex)
    x = f / resistivity * 1000
    zc = 1 + 5.50 * x ** (-.632) - 1j * 8.43 * x ** (-.632)
    kc = 2 * np.pi * f / C * (1 + 7.81 * x ** (-.618) - 1j * 11.41 * x ** (-.618))
    zs = -1j * zc / np.tan(kc * thickness_mm / 1000)
    return 1 / zs


def mesh_rule(f_max_hz, order=1, dof_per_wavelength=10):
    """Maximum element size for a wave-based solve: h = c P / (10 f_max) at P shape-function order.

    The common rule of thumb is 6 to 10 degrees of freedom per wavelength. What the rule does not
    address is the second term of the error bound,

        error <= C1 (k h / 2P)^P  +  C2 k (k h / 2P)^(2P)

    whose second term is numerical dispersion - the pollution effect - and carries an extra factor of
    k. THAT IS WHY A FIXED NUMBER OF ELEMENTS PER WAVELENGTH GETS WORSE AS FREQUENCY RISES, and the
    review that states the rule says so explicitly. A mesh specified as "8 per wavelength" is not a
    constant accuracy specification across a decade.
    """
    f_max_hz = float(f_max_hz)
    order = int(order)
    if f_max_hz <= 0 or order < 1:
        raise InputError("the meshing rule needs a positive f_max and a shape-function order of at least 1")
    h = C * order / (dof_per_wavelength * f_max_hz)
    return dict(f_max_hz=f_max_hz, shape_function_order=order, dof_per_wavelength=dof_per_wavelength,
                max_element_size_m=h, max_element_size_mm=h * 1000,
                wavelength_at_f_max_m=C / f_max_hz,
                rule="h = c P / (10 f_max), from the 6-to-10 degrees of freedom per wavelength rule of thumb",
                error_bound="error <= C1 (k h / 2P)^P + C2 k (k h / 2P)^(2P). The first term is interpolation error, "
                            "the second is numerical dispersion - the pollution effect - and it carries an extra factor "
                            "of k, so a fixed elements-per-wavelength figure LOSES VALIDITY AS FREQUENCY RISES.",
                what_it_buys="quadratic elements at 10 degrees of freedom per wavelength reproduce the analytic modal "
                             "frequencies of a rigid-walled rectangular room to within 0.002 to 0.08 percent over the "
                             "first ten modes.",
                what_it_does_not_buy="NUMERICAL ACCURACY IS NOT AGREEMENT WITH MEASUREMENT. A solver's 0.01 percent "
                                     "numerical error says nothing whatever about how far its answer sits from a "
                                     "microphone, and no source consulted states that distance for any tool.")


def piston_directivity(f, angle_rad, radius_m):
    q = 2 * np.pi * np.asarray(f, float) / C * radius_m * np.sin(angle_rad)
    result = np.ones_like(q)
    nz = np.abs(q) > 1e-9
    result[nz] = 2 * j1(q[nz]) / q[nz]
    return result


def gaussian_directivity(h_rad, v_rad, horizontal_deg, vertical_deg):
    """Gaussian coverage that is exactly -6 dB at half the nominal included angle."""
    return np.exp(-np.log(10) * 6 / 20 * ((np.rad2deg(h_rad) / (horizontal_deg / 2)) ** 2 + (np.rad2deg(v_rad) / (vertical_deg / 2)) ** 2))


def beamwidth_table_deg(f, points):
    table = np.asarray(points, float)
    lf = np.log(np.asarray(f, float))
    return np.interp(lf, np.log(table[:, 0]), table[:, 1]), np.interp(lf, np.log(table[:, 0]), table[:, 2])


def rectangular_directivity(f, h_rad, v_rad, width_m, height_m):
    f = np.asarray(f, float)
    return np.sinc(f * width_m / C * np.sin(h_rad)) * np.sinc(f * height_m / C * np.sin(v_rad))


def directivity(model, f, h_rad, v_rad):
    """Directivity factor for a source model at horizontal/vertical angles (broadcast shapes).

    model kinds: piston {radius_mm | diameter_mm | sd_cm2}, gaussian {horizontal_deg, vertical_deg},
    beamwidth_table {points [[hz, h_deg, v_deg], ...]}, rectangular {width_mm, height_mm}, omni.
    """
    kind = (model or {}).get("kind", "omni")
    f = np.asarray(f, float)
    if kind == "distributed_edge_dipole":
        from .diffraction import evaluate
        return evaluate(model, f, h_rad, v_rad)
    if kind == "measured_planes":
        from .response_data import measured_directivity
        return measured_directivity(model, f, h_rad, v_rad)
    if kind == "omni":
        return np.ones(np.broadcast(f, h_rad, v_rad).shape)
    if kind in ("dipole", "cardioid"):
        mu = np.cos(h_rad) * np.cos(v_rad)
        factor = mu if kind == "dipole" else (1 + mu) / 2
        return np.broadcast_to(factor, np.broadcast(f, h_rad, v_rad).shape).copy()
    if kind == "complex_grid":
        from scipy.interpolate import RegularGridInterpolator
        grid_f = np.asarray(model["frequency_hz"], float)
        grid_h = np.asarray(model["horizontal_deg"], float)
        grid_v = np.asarray(model["vertical_deg"], float)
        data = np.asarray(model["real"], float) + 1j * np.asarray(model["imag"], float)
        ff, hh, vv = np.broadcast_arrays(f, np.rad2deg(h_rad), np.rad2deg(v_rad))
        points = np.c_[vv.ravel(), hh.ravel(), np.log(ff.ravel())]
        if data.shape != (len(grid_v), len(grid_h), len(grid_f)):
            raise InputError("complex directivity grid shape needs [vertical,horizontal,frequency]")
        try:
            values = RegularGridInterpolator((grid_v, grid_h, np.log(grid_f)), data, bounds_error=True)(points)
        except ValueError as exc:
            raise InputError("complex angular source does not cover requested frequencies/directions") from exc
        return values.reshape(ff.shape)
    if kind == "piston":
        radius = piston_radius_m(model)
        theta = np.arctan2(np.hypot(np.tan(h_rad), np.tan(v_rad)), 1.0)
        return piston_directivity(f, theta, radius)
    if kind == "gaussian":
        return np.broadcast_to(gaussian_directivity(h_rad, v_rad, float(model["horizontal_deg"]), float(model["vertical_deg"])), np.broadcast(f, h_rad, v_rad).shape).copy()
    if kind == "beamwidth_table":
        h_deg, v_deg = beamwidth_table_deg(f, model["points"])
        return np.exp(-np.log(10) * 6 / 20 * ((np.rad2deg(h_rad) / (h_deg / 2)) ** 2 + (np.rad2deg(v_rad) / (v_deg / 2)) ** 2))
    if kind == "rectangular":
        return rectangular_directivity(f, h_rad, v_rad, float(model["width_mm"]) / 1000, float(model["height_mm"]) / 1000)
    raise InputError(f"unknown directivity kind '{kind}'")


def piston_radius_m(model):
    if model.get("radius_mm") is not None:
        return float(model["radius_mm"]) / 1000
    if model.get("diameter_mm") is not None:
        return float(model["diameter_mm"]) / 2000
    if model.get("sd_cm2") is not None:
        return math.sqrt(float(model["sd_cm2"]) * 1e-4 / math.pi)
    raise InputError("piston directivity needs radius_mm, diameter_mm or sd_cm2")


def beamwidth_deg(f_hz, model):
    """Included -6 dB angle of a model in the horizontal plane, or 360 when it never reaches -6 dB."""
    angles = np.linspace(0, np.pi / 2, 901)
    d = np.abs(directivity(model, np.array([f_hz]), angles, np.zeros_like(angles)))
    selected = np.flatnonzero(d <= 10 ** (-6 / 20))
    if not len(selected):
        return 360.0
    i = int(selected[0])
    if i == 0:
        return 0.0
    return float(2 * np.rad2deg(np.interp(10 ** (-6 / 20), d[i - 1:i + 1][::-1], angles[i - 1:i + 1][::-1])))


def butterworth(f, fc, order, highpass):
    q = 1j * np.asarray(f, float) / fc
    section = 1 / (q * q + np.sqrt(2) * q + 1)
    if highpass:
        section = section * q * q
    return section ** (order / 2)


def linkwitz_riley(f, fc, order, highpass=False):
    """Linkwitz-Riley of even order: squared Butterworth of half the order."""
    if order % 2:
        raise InputError("Linkwitz-Riley order must be even")
    return butterworth(f, fc, order // 2, highpass) ** 2


def bandwidth_shape(f, lower_hz=None, upper_hz=None, upper_order=4, lower_order=2):
    """Declared-bandwidth prior: fourth-order roll-off reaching -10 dB at the upper limit, second-order below the lower limit."""
    f = np.asarray(f, float)
    shape = np.ones(len(f), complex)
    if upper_hz:
        shape = shape * butterworth(f, 0.75 * float(upper_hz), upper_order, False)
    if lower_hz:
        shape = shape * butterworth(f, float(lower_hz), lower_order, True)
    return shape


_trapezoid = getattr(np, "trapezoid", None) or getattr(np, "trapz")


def minimum_phase(f_eval, f_points, db_points, lower_rolloff_db_oct=12.0, upper_rolloff_db_oct=24.0, step=.01, span=14.0):
    """Minimum-phase complex response (linear magnitude) from a sparse magnitude curve in dB via Bode's gain-phase integral."""
    f_eval = np.atleast_1d(np.asarray(f_eval, float))
    fp = np.asarray(f_points, float)
    dp = np.asarray(db_points, float)
    if len(fp) < 2 or np.any(np.diff(fp) <= 0) or np.any(fp <= 0) or np.any(f_eval <= 0):
        raise InputError("minimum-phase reconstruction needs positive, strictly increasing frequency points")
    ln_fp = np.log(fp)
    ln_f = np.log(f_eval)
    lo = min(float(ln_f.min()), float(ln_fp[0])) - span
    hi = max(float(ln_f.max()), float(ln_fp[-1])) + span
    grid = np.arange(lo, hi + step, step)
    db = np.interp(grid, ln_fp, dp)
    below = grid < ln_fp[0]
    above = grid > ln_fp[-1]
    db[below] = dp[0] - lower_rolloff_db_oct * (ln_fp[0] - grid[below]) / np.log(2)
    db[above] = dp[-1] - upper_rolloff_db_oct * (grid[above] - ln_fp[-1]) / np.log(2)
    amplitude = db / 20 * np.log(10)
    slope = np.gradient(amplitude, step)
    u = np.arange(-span, span + step / 2, step)
    kernel = np.log(1 / np.tanh(np.maximum(np.abs(u), 1e-9) / 2))
    phase = np.empty(len(f_eval))
    for index, x in enumerate(ln_f):
        centre = float(np.interp(x, grid, slope))
        local = np.interp(x + u, grid, slope)
        phase[index] = centre * np.pi / 2 + _trapezoid((local - centre) * kernel, u) / np.pi
    magnitude = np.exp(np.interp(ln_f, grid, amplitude))
    return magnitude * np.exp(1j * phase)


def impedance_model(model, f):
    """Complex load impedance from a declarative model.

    kinds: resistive {r_ohm}; resonant {re_ohm, le_mh, peak_r_ohm, peak_hz, peak_q};
    ribbon {r_ohm, parallel_l_mh}; free_air {ts}; sealed {ts, net_volume_l, ql};
    vented / passive_radiator {ts, enclosure}; curve {frequency_hz, real_ohm, imag_ohm}.
    """
    f = np.asarray(f, float)
    s = 2j * np.pi * f
    kind = require(model, "kind", label="impedance")
    if kind == "resistive":
        return np.full(len(f), positive(model.get("r_ohm"), "impedance.r_ohm"), complex)
    if kind == "resonant":
        re = positive(model.get("re_ohm"), "impedance.re_ohm")
        le = float(model.get("le_mh", 0.0)) * 1e-3
        peak_r = float(model.get("peak_r_ohm", 0.0))
        peak_hz = float(model.get("peak_hz", 0.0))
        peak_q = float(model.get("peak_q", 1.0))
        z = re + s * le
        if peak_r > 0 and peak_hz > 0:
            z = z + peak_r / (1 + 1j * peak_q * (f / peak_hz - peak_hz / f))
        return z
    if kind == "ribbon":
        r = positive(model.get("r_ohm"), "impedance.r_ohm")
        lp = model.get("parallel_l_mh")
        if lp:
            return 1 / (1 / r + 1 / (s * float(lp) * 1e-3))
        return np.full(len(f), r, complex)
    if kind == "free_air":
        ts = require(model, "ts", label="impedance")
        d = driver_elements(ts)
        return blocked_impedance(ts, f) + d["bl"] ** 2 / mechanical_impedance(ts, f, d)
    if kind in ("sealed", "vented", "passive_radiator"):
        ts = require(model, "ts", label="impedance")
        enclosure = dict(model.get("enclosure") or {}, type=kind)
        if kind == "sealed" and "net_volume_l" in model:
            enclosure["net_volume_l"] = model["net_volume_l"]
            enclosure["ql"] = model.get("ql", 10.0)
        return box_response(ts, enclosure, f)["z_ohm"]
    if kind == "curve":
        return np.interp(np.log(f), np.log(np.asarray(model["frequency_hz"], float)), np.asarray(model["real_ohm"], float)) + \
            1j * np.interp(np.log(f), np.log(np.asarray(model["frequency_hz"], float)), np.asarray(model["imag_ohm"], float))
    raise InputError(f"unknown impedance kind '{kind}'")


def require(document, key, label):
    if not isinstance(document, dict) or key not in document:
        raise InputError(f"{label} is missing '{key}'")
    return document[key]


def default_coil_dcr(l_mh):
    """Assumed copper DCR of an air-core coil when no value is supplied: 0.10 + 0.16 sqrt(L_mH) ohm."""
    return .10 + .16 * math.sqrt(max(l_mh, 0.0))


def element_impedance(element, f, scale=None):
    """Complex impedance of a network element description.

    {"type": "R", "value_ohm"}; {"type": "L", "value_mh", "dcr_ohm"}; {"type": "C", "value_uf", "esr_ohm"};
    {"type": "series"|"parallel", "parts": [...]}; {"type": "open"}; {"type": "short"}.
    scale maps element ids to multiplicative factors (tolerance draws or fitting).
    """
    f = np.asarray(f, float)
    s = 2j * np.pi * f
    kind = require(element, "type", label="element")
    factor = 1.0 if not scale else float(scale.get(element.get("id", ""), 1.0))
    if kind == "R":
        return np.full(len(f), positive(element.get("value_ohm"), "R value_ohm", zero=True) * factor, complex)
    if kind == "L":
        l_mh = positive(element.get("value_mh"), "L value_mh") * factor
        dcr = element.get("dcr_ohm")
        dcr = default_coil_dcr(l_mh) if dcr is None else float(dcr)
        z = dcr + s * l_mh * 1e-3
        admittance = 1 / z
        if element.get("parallel_r_ohm") is not None:
            admittance += 1 / positive(element["parallel_r_ohm"], "parallel_r_ohm")
        if element.get("parallel_c_pf") is not None:
            admittance += s * positive(element["parallel_c_pf"], "parallel_c_pf", zero=True) * 1e-12
        return 1 / admittance
    if kind == "C":
        c_uf = positive(element.get("value_uf"), "C value_uf") * factor
        esr = float(element.get("esr_ohm", 0.01))
        return esr + 1 / (s * c_uf * 1e-6)
    if kind == "series":
        return sum(element_impedance(part, f, scale) for part in element.get("parts", []))
    if kind == "parallel":
        return 1 / sum(1 / element_impedance(part, f, scale) for part in element.get("parts", []))
    if kind == "short":
        return np.zeros(len(f), complex)
    if kind == "open":
        return np.full(len(f), 1e12, complex)
    raise InputError(f"unknown element type '{kind}'")


def iter_elements(element):
    """Yield every leaf element (R, L, C) inside a possibly nested element."""
    if element.get("type") in ("series", "parallel"):
        for part in element.get("parts", []):
            yield from iter_elements(part)
    else:
        yield element


def shelf_baffle(f, width_mm):
    """First-order 6 dB baffle step with its corner at 115 / width Hz."""
    q = 1j * np.asarray(f, float) / (115 / (width_mm / 1000))
    return .5 * (1 + q / np.sqrt(.5)) / (1 + q / np.sqrt(2))


def edge_segments(width_mm, height_mm, x_mm, z_mm, segments=96):
    w, h = width_mm / 1000., height_mm / 1000.
    corners = np.array([[0., 0.], [w, 0.], [w, h], [0., h], [0., 0.]])
    per_edge = max(4, segments // 4)
    t = np.linspace(0., 1., per_edge + 1)[:-1]
    points = np.concatenate([a[None, :] + (b - a)[None, :] * t[:, None] for a, b in zip(corners[:-1], corners[1:])])
    source = np.array([x_mm / 1000., z_mm / 1000.])
    rel = points - source
    angles = np.arctan2(rel[:, 1], rel[:, 0])
    mid = (points + np.roll(points, -1, axis=0)) / 2 - source
    distance = np.hypot(mid[:, 0], mid[:, 1])
    subtended = np.abs(np.angle(np.exp(1j * (np.roll(angles, -1) - angles))))
    return subtended, distance


def edge_beaming(f, radius_m):
    f = np.asarray(f, float)
    if radius_m <= 0:
        return np.ones(f.shape)
    q = 2 * np.pi * f / C * radius_m
    out = np.ones(f.shape)
    nz = q > 1e-9
    out[nz] = 2 * j1(q[nz]) / q[nz]
    return out


def edge_diffraction(f, width_mm, height_mm, x_mm, z_mm, radius_m=0., observer_m=None, segments=96, edge_radius_m=0.):
    """On-axis rectangular-baffle factor: one minus the weighted sum of delayed, inverted half edge waves.

    With an observer distance the edge waves are also weighted by observer / hypot(observer, d):
    an edge wave reaches a near observer over a longer path than the direct sound and is therefore
    weaker, which is why a 250 mm baffle shows about 5 dB of step at 0.25 m against 6 dB far field.
    The weighting tends to one in the far field, where the model reduces to its previous form.

    edge_radius_m rolls the edge off above the lambda/8 frequency c / (8 r): below it a roundover
    is acoustically invisible, so the taper starts there rather than at DC.
    """
    f = np.asarray(f, float)
    if width_mm <= 0 or height_mm <= 0 or not 0 < x_mm < width_mm or not 0 < z_mm < height_mm:
        raise InputError("edge diffraction needs the source strictly inside a positive baffle rectangle")
    subtended, distance = edge_segments(width_mm, height_mm, x_mm, z_mm, segments)
    weight = subtended / subtended.sum()
    spread = np.ones_like(distance)
    extra = distance
    if observer_m:
        hyp = np.sqrt(observer_m ** 2 + distance ** 2)
        extra = distance + hyp - observer_m
        spread = observer_m / hyp
    k = 2 * np.pi * f / C
    edges = np.sum((weight * spread)[:, None] * np.exp(-1j * k[None, :] * extra[:, None]), axis=0)
    return 1 - .5 * edge_beaming(f, radius_m) * roundover_factor(f, edge_radius_m) * edges


def roundover_factor(f, edge_radius_m):
    """First-order taper of the edge wave above the lambda/8 frequency c / (8 r) of a roundover."""
    f = np.asarray(f, float)
    if edge_radius_m <= 0:
        return np.ones(f.shape)
    return 1 / (1 + 1j * f / roundover_corner_hz(edge_radius_m))


def roundover_corner_hz(edge_radius_m):
    """The lambda/8 frequency above which an edge radius can do anything at all."""
    return C / (8 * edge_radius_m)


def baffle_step_db(width_mm, height_mm, x_mm, z_mm, observer_m=None, segments=96):
    """Depth of the baffle step in dB: the low-frequency limit of the edge-diffraction factor.

    At f -> 0 every delay term is unity and the piston and roundover factors are one, so the
    factor is 1 - 0.5 sum(w a) exactly; the high-frequency asymptote is unity by construction.
    """
    subtended, distance = edge_segments(width_mm, height_mm, x_mm, z_mm, segments)
    weight = subtended / subtended.sum()
    spread = np.ones_like(distance) if not observer_m else observer_m / np.sqrt(observer_m ** 2 + distance ** 2)
    return float(-db(1 - .5 * np.sum(weight * spread)))


def recess_transfer(f, setback_mm, opening_width_mm, opening_height_mm):
    """Mouth pressure of a short rigid recess relative to a flush source; quarter-wave rise only."""
    f = np.atleast_1d(np.asarray(f, float))
    if setback_mm <= 0:
        return np.ones(len(f), complex)
    area = opening_width_mm * opening_height_mm * 1e-6
    radius = math.sqrt(area / math.pi)
    k = 2 * np.pi * f / C
    ka = k * radius
    resistance = np.ones(len(f))
    nz = ka > 1e-9
    resistance[nz] = 1 - j1(2 * ka[nz]) / ka[nz]
    reactance = np.minimum(8 * ka / (3 * np.pi), 1.)
    z_mouth = resistance + 1j * reactance
    kd = k * setback_mm / 1000.
    return 1 / (np.cos(kd) + 1j * z_mouth * np.sin(kd))


def piston_radiation_impedance(f, radius_m):
    """Normalized radiation impedance of a baffled circular piston (real from J1, imaginary from Struve H1)."""
    ka = 2 * np.pi * np.asarray(f, float) / C * radius_m
    ka = np.maximum(ka, 1e-9)
    return 1 - j1(2 * ka) / ka + 1j * struve(1, 2 * ka) / ka


def sustained_cutoff(f, spl, level_db, reference_band=(150., 300.), reference_level=None, upper_hz=None):
    """Lowest frequency above which the response stays at or above level_db relative to the reference up to the band.

    Returns (value_hz, bound) where bound is resolved, left_censored (never fell below) or no_sustained_pass.
    """
    f = np.asarray(f, float)
    spl = np.asarray(spl, float)
    if reference_level is None:
        inside = (f >= reference_band[0]) & (f <= reference_band[1])
        if not np.any(inside):
            raise InputError("reference band is outside the evaluated sweep")
        reference_level = float(np.mean(spl[inside]))
    delta = spl - reference_level
    top = reference_band[0] if upper_hz is None else upper_hz
    below = np.flatnonzero((f <= top) & (delta < level_db))
    if not len(below):
        return float(f[0]), "left_censored", reference_level
    j = int(below[-1])
    if j + 1 >= len(f) or delta[j + 1] < level_db:
        return None, "no_sustained_pass", reference_level
    return float(np.exp(np.interp(level_db, delta[j:j + 2], np.log(f[j:j + 2])))), "resolved", reference_level


def band_within(f, relative_db, tolerance_db, anchor_band):
    """Lowest and highest frequency where |relative_db| stays within tolerance, sustained outward from the anchor band."""
    f = np.asarray(f, float)
    relative_db = np.asarray(relative_db, float)
    inside = np.abs(relative_db) <= tolerance_db
    anchor = np.flatnonzero((f >= anchor_band[0]) & (f <= anchor_band[1]))
    if not len(anchor) or not inside[anchor].any():
        return dict(low_hz=None, high_hz=None, low_bound="no_anchor", high_bound="no_anchor", tolerance_db=float(tolerance_db))
    start = int(anchor[inside[anchor]][0])
    low = start
    while low > 0 and inside[low - 1]:
        low -= 1
    high = start
    while high < len(f) - 1 and inside[high + 1]:
        high += 1

    def edge(index, step):
        neighbour = index + step
        if neighbour < 0 or neighbour >= len(f):
            return float(f[index]), "censored_at_grid_edge"
        crossing = np.interp(tolerance_db, [abs(relative_db[index]), abs(relative_db[neighbour])], [np.log(f[index]), np.log(f[neighbour])])
        return float(np.exp(crossing)), "resolved"

    low_hz, low_bound = edge(low, -1)
    high_hz, high_bound = edge(high, 1)
    return dict(low_hz=low_hz, high_hz=high_hz, low_bound=low_bound, high_bound=high_bound, tolerance_db=float(tolerance_db))


def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-30))
