#!/usr/bin/env python3
"""Cabinet panel bays: the mode band between pinned and clamped edges, the modal response under internal
pressure, measured damping treatments and the BBC audibility criterion."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, panels  # noqa: E402

NAME = "plate_structure"
VERSION = "1.1"
NOTES = [
    "Isotropic or orthotropic thin plate, simply supported on the bay edges (brace lines are ideal supports, joints rigid), Navier sine modes, uniform RMS pressure over the bay.",
    "Displacements are RMS when the pressure is RMS; the modal-sum bound is an upper estimate that does not miss antinodes between sample points.",
    "No fluid-structure coupling, no panel radiation, no joint compliance, no aperture-bearing panels; comparative screening of panel thickness, material and brace spacing.",
    "The mode band is Leissa's frequency parameter evaluated at both edge conditions: pinned from the exact closed form lambda = pi^2 (1 + (a/b)^2), clamped interpolated from his tabulated values. The band is the deliverable - the edge condition alone moves the fundamental by a factor of 1.8 to 2.2 and a real glued joint is neither condition.",
    "Material data is the BBC's measured E at 250 Hz, density and maximum Q, with the Wood Handbook's static-bending moduli for the products the BBC did not measure. Plywood is orthotropic and this is isotropic plate theory applied with a geometric-mean E; E itself varies 10 to 20 percent across the band.",
    "Damping treatments are the BBC's measured loss factors on a 9 mm birch plywood substrate. The rank order transfers to another panel and the absolute values do not.",
    "The audibility criterion is the BBC's measured perceptibility curve, reported against a RELATIVE panel output. No absolute panel SPL is computed here and none should be: the BBC established that the panels, the driver and the enclosed air are coupled and that the coupling sets the radiated level, so an overall measurement is the only way to get it.",
]


def plate_modes(a_m, b_m, thickness_m, e_pa, rho, nu=.3, order=7, orthotropic=None, orientation_deg=0):
    if min(a_m, b_m, thickness_m, e_pa, rho) <= 0 or not 0 <= nu < .5:
        raise cli.InputError("positive plate dimensions and material values with 0 <= poisson_ratio < .5 are required")
    mn = np.array([(m, n) for m in range(1, order + 1) for n in range(1, order + 1)])
    surface_density = rho * thickness_m
    if orthotropic:
        ex, ey, g = float(orthotropic["E_parallel_pa"]), float(orthotropic["E_perpendicular_pa"]), float(orthotropic["G_inplane_pa"])
        nu_xy = float(orthotropic.get("nu_parallel_perp", .3))
        nu_yx = nu_xy * ey / ex
        factor = thickness_m ** 3 / (12 * (1 - nu_xy * nu_yx))
        d11, d22, d12, d66 = ex * factor, ey * factor, nu_xy * ey * factor, g * thickness_m ** 3 / 12
        if orientation_deg == 90:
            d11, d22 = d22, d11
    else:
        d11 = d22 = e_pa * thickness_m ** 3 / (12 * (1 - nu ** 2))
        d12 = nu * d11
        d66 = (1 - nu) * d11 / 2
    kx = np.pi * mn[:, 0] / a_m
    ky = np.pi * mn[:, 1] / b_m
    omega = np.sqrt((d11 * kx ** 4 + 2 * (d12 + 2 * d66) * kx * kx * ky * ky + d22 * ky ** 4) / surface_density)
    force_ratio = np.where((mn[:, 0] % 2 == 1) & (mn[:, 1] % 2 == 1), 16 / (np.pi ** 2 * mn[:, 0] * mn[:, 1]), 0.)
    ix = np.argsort(omega)
    return dict(indices=mn[ix], frequency_hz=omega[ix] / (2 * np.pi), omega=omega[ix], force_ratio=force_ratio[ix],
                surface_density=surface_density, bending_stiffness_nm=dict(D11=d11, D22=d22, D12=d12, D66=d66))


def modal_response(modes, f, pressure_pa, loss_factor, sample_points=15):
    f = np.atleast_1d(np.asarray(f, float))
    p = np.broadcast_to(np.asarray(pressure_pa, float), f.shape)
    wn = modes["omega"]
    w = 2 * np.pi * f
    denom = wn[None, :] ** 2 - w[:, None] ** 2 + 1j * loss_factor * wn[None, :] ** 2
    q = p[:, None] * modes["force_ratio"][None, :] / modes["surface_density"] / denom
    mn = modes["indices"]
    center_shape = np.sin(np.pi * mn[:, 0] / 2) * np.sin(np.pi * mn[:, 1] / 2)
    center = q @ center_shape
    bound = np.sum(np.abs(q), axis=1)
    # Volume displacement of the Navier series: only the odd-odd modes move net air, and each
    # contributes (2/(m pi))(2/(n pi)) of its amplitude times the bay area. The volume velocity that
    # follows is what a relative panel-output comparison needs; a displacement bound is not one.
    volume_shape = np.where((mn[:, 0] % 2 == 1) & (mn[:, 1] % 2 == 1),
                            4 / (np.pi ** 2 * mn[:, 0] * mn[:, 1]), 0.)
    volume_displacement = q @ volume_shape
    result = dict(center_m=center, bound_m=bound, velocity_bound_m_s=w * bound,
                  volume_displacement_per_area_m=volume_displacement,
                  volume_velocity_per_area_m_s=w * np.abs(volume_displacement))
    if sample_points:
        u = np.linspace(0, 1, sample_points)
        x, y = np.meshgrid(u, u, indexing="ij")
        shape = np.sin(np.pi * x.reshape(-1, 1) * mn[:, 0]) * np.sin(np.pi * y.reshape(-1, 1) * mn[:, 1])
        result["sampled_max_m"] = np.max(np.abs(q @ shape.T), axis=1)
    return result


def cone_volume_velocity(spec, f, base_dir):
    """RMS volume velocity of the cone, from an excursion curve and Sd, as the reference for a ratio.

    U = Sd omega x, with a peak excursion curve converted to RMS. This is the only reference the
    framework can supply without a measurement, and a volume-velocity ratio is NOT the BBC's measured
    panel-to-direct pressure ratio: it holds while both radiators are small compared with a wavelength
    and it flatters the panel above that, because a panel's radiation efficiency falls with modal
    cancellation and a cone's does not.
    """
    sd = cli.positive(spec.get("sd_cm2"), "audibility.cone.sd_cm2") * 1e-4
    if spec.get("constant_excursion_mm_peak") is not None:
        excursion = np.full(len(f), float(spec["constant_excursion_mm_peak"]))
    else:
        ref = dict(spec)
        ref.setdefault("frequency_path", "results.f_hz")
        ref["path"] = cli.require(spec, "excursion_path", label="audibility.cone")
        excursion = cli.curve_from_reference(ref, base_dir, f, kind="real")
    rms = np.asarray(excursion, float) / 1000 / np.sqrt(2)
    return sd * 2 * np.pi * f * rms, dict(sd_cm2=sd * 1e4, source=spec.get("excursion_path") or "constant")


def audibility_overlay(f, panel_volume_velocity, cone, scatter_db=1.0):
    """The BBC criterion as an overlay on a relative panel output: margin, and where it is smallest."""
    criterion = panels.audibility_criterion_db(f)
    relative = 20 * np.log10(np.maximum(np.asarray(panel_volume_velocity, float), 1e-30) /
                             np.maximum(np.asarray(cone, float), 1e-30))
    margin = criterion - relative
    worst = int(np.argmin(margin))
    return dict(relative_to_cone_db=relative, criterion_db=criterion, margin_db=margin,
                worst_margin_db=float(margin[worst]), worst_margin_hz=float(f[worst]),
                above_criterion=bool(margin[worst] < 0),
                above_criterion_with_scatter=bool(margin[worst] < scatter_db),
                scatter_db=scatter_db,
                basis="a RATIO OF VOLUME VELOCITIES, panel against cone, not a measured panel-to-direct pressure ratio. "
                      "It holds while both radiators are small compared with a wavelength and flatters the panel above "
                      "that. Read it as which octave to worry about, with the criterion's own +/- 1 dB scatter and its "
                      "complete lack of theoretical backing.")


def auto_bays(spec):
    """Side bays between braces, plus bottom and top, from inside dimensions and brace heights."""
    depth = float(spec["inside_depth_mm"])
    width = float(spec["inside_width_mm"])
    height = float(spec["inside_height_mm"])
    t = float(spec.get("brace_thickness_mm", 18.0))
    boundaries = [0.0] + sorted(float(z) + t / 2 for z in spec.get("brace_z_mm", [])) + [height]
    spans = np.diff(boundaries)
    if np.any(spans <= 0):
        raise cli.InputError("brace heights must lie inside the chamber in increasing order")
    bays = [dict(name=f"side_bay_{i + 1}", a_mm=depth, b_mm=float(s), count=2) for i, s in enumerate(spans)]
    bays.append(dict(name="bottom", a_mm=width, b_mm=depth, count=1))
    bays.append(dict(name="top", a_mm=width, b_mm=depth, count=1))
    if spec.get("rear_bays", True):
        bays.extend(dict(name=f"rear_bay_{i + 1}", a_mm=width, b_mm=float(s), count=1, note="rear panel bay; ignore if it carries the port or terminals") for i, s in enumerate(spans))
    return bays


VALIDITY = [
    "The modal response is computed for simply supported ideal bays, which is the lower edge of the mode band: a real glued and braced panel sits somewhere between pinned and clamped, up to an octave higher.",
    "This is panel motion, not radiated sound. An absolute panel SPL is not computable from the panels alone - that is a finding with a source, not an absence of effort - so every audibility judgement here is relative and carries the criterion's own +/- 1 dB scatter and its lack of any theoretical backing.",
    "Bracing is not quantified by any source consulted. A brace changes both the effective panel dimensions and the edge condition, so neither the aspect-ratio table nor the pinned/clamped bracket applies to a braced panel without an assumption that has to be stated.",
    "The mode band places the fundamental. It is optimistic at the bottom: the BBC's own cabinet measures below its pinned bound because a real panel carries the driver's reaction mass on compliant joints.",
]


def compute(params, base_dir):
    spec = cli.require(params, "material")
    material = panels.material(spec)
    thickness = cli.positive(material.get("thickness_mm"), "material.thickness_mm") / 1000
    e_pa = cli.positive(material.get("youngs_modulus_pa"), "material.youngs_modulus_pa")
    rho = cli.positive(material.get("density_kg_m3"), "material.density_kg_m3")
    nu = float(material.get("poisson_ratio", .3))
    ortho = material.get("orthotropic")
    treatments = [panels.treatment(name) for name in (spec.get("treatments") or [])]
    # a treatment's measured loss factor is an input to the response, which is what makes the
    # damping choice visible as a curve rather than as a claim
    losses = sorted(set([float(x) for x in spec.get("loss_factors", [] if treatments else [.015, .03, .08])] +
                        [t["loss_factor"] for t in treatments]))
    if not losses:
        raise cli.InputError("material needs loss_factors or treatments")
    order = int(params.get("mode_order", 7))
    bays = list(params.get("panels") or [])
    if params.get("auto_bays"):
        bays.extend(auto_bays(params["auto_bays"]))
    if not bays:
        raise cli.InputError("give panels[] or auto_bays")
    pressure = params.get("pressure") or {"constant_pa": 1.0}
    if "file" in pressure:
        f0 = cli.frequency_grid(params.get("frequencies"), 20.0, 1500.0, 121)
        ref = dict(pressure)
        ref.setdefault("frequency_path", "results.f_hz")
        p0 = cli.curve_from_reference(ref, base_dir, f0, kind="real") * float(pressure.get("scale", 1.0))
    else:
        f0 = cli.frequency_grid(params.get("frequencies"), 20.0, 1500.0, 121)
        p0 = np.full(len(f0), float(pressure["constant_pa"]))
    cone = None
    cone_record = None
    audibility = params.get("audibility") or {}
    if audibility.get("cone"):
        cone, cone_record = cone_volume_velocity(audibility["cone"], f0, base_dir)
    rows = []
    for panel in bays:
        a = cli.positive(panel.get("a_mm"), f"panel {panel.get('name')} a_mm") / 1000
        b = cli.positive(panel.get("b_mm"), f"panel {panel.get('name')} b_mm") / 1000
        t = thickness * float(panel.get("thickness_factor", 1.0))
        orientations = [0, 90] if ortho else [0]
        for orientation in orientations:
            modes = plate_modes(a, b, t, e_pa, rho, nu, order, ortho, orientation)
            natural = modes["frequency_hz"]
            f = np.unique(np.r_[f0, natural[(natural >= f0[0]) & (natural <= f0[-1])]])
            p = np.interp(f, f0, p0)
            static = modal_response(modes, [0.0], float(p.max()), 1e-12)
            variants = []
            for loss in losses:
                r = modal_response(modes, f, p, loss)
                i = int(np.argmax(r["bound_m"]))
                count = int(panel.get("count", 1))
                volume_velocity = r["volume_velocity_per_area_m_s"] * a * b * count
                variant = dict(loss_factor=loss, treatment=next((t["name"] for t in treatments
                                                                 if abs(t["loss_factor"] - loss) < 1e-12), None),
                               center_displacement_rms_mm=np.abs(r["center_m"]) * 1000, modal_bound_rms_mm=r["bound_m"] * 1000,
                               sampled_max_rms_mm=r["sampled_max_m"] * 1000, velocity_bound_rms_m_s=r["velocity_bound_m_s"],
                               volume_velocity_rms_m3_s=volume_velocity,
                               peak_bound_rms_mm=float(r["bound_m"][i] * 1000), peak_hz=float(f[i]),
                               peak_velocity_bound_m_s=float(r["velocity_bound_m_s"].max()))
                if cone is not None:
                    variant["audibility"] = audibility_overlay(f, volume_velocity, np.interp(f, f0, cone))
                variants.append(variant)
            band = panels.mode_band(a, b, t, e_pa, rho, nu)
            criterion = dict(
                margin_required_at_pinned_db=float(panels.audibility_criterion_db(band["pinned_hz"])[0]),
                margin_required_at_clamped_db=float(panels.audibility_criterion_db(band["clamped_hz"])[0]),
                reading="the panel's output has to sit at least this far below the direct axial response to have been "
                        "inaudible in the BBC's listening tests. The requirement tightens by 17 dB between 100 and "
                        "400 Hz, so moving a panel mode up in frequency moves it into the least forgiving part of the "
                        "curve - which is why a thicker wall with a higher Q radiated MORE in the BBC's own experiment.")
            rows.append(dict(name=panel.get("name"), a_mm=a * 1000, b_mm=b * 1000, thickness_mm=t * 1000, count=panel.get("count", 1), note=panel.get("note"),
                             mode_band=band, audibility=criterion,
                             grain_orientation_deg=orientation if ortho else None, f_hz=f, pressure_rms_pa=p,
                             natural_modes_hz=natural[:15], mode_indices=modes["indices"][:15],
                             first_mode_hz=float(natural[0]),
                             first_mode_note="the Navier solve is simply supported, so this is the pinned bound of "
                                             "mode_band and not a prediction of where the panel resonates",
                             static_center_mm_at_max_pressure=float(np.abs(static["center_m"][0]) * 1000),
                             static_sampled_max_mm=float(static["sampled_max_m"][0] * 1000), bending_stiffness_nm=modes["bending_stiffness_nm"],
                             loss_variants=variants))
    nominal = losses[len(losses) // 2]
    return dict(material=dict(material, thickness_mm=thickness * 1000, youngs_modulus_pa=e_pa, density_kg_m3=rho,
                              poisson_ratio=nu, orthotropic=ortho, loss_factors=losses),
                damping=dict(treatments=treatments, ranking_by_loss_factor_per_mm=panels.treatment_ranking(),
                             bare_panel_loss_factor=1 / panels.TREATMENTS["none"]["q"],
                             caveat=panels.TREATMENT_CAVEAT),
                audibility_criterion=dict(panels.criterion_record(f0), cone_reference=cone_record,
                                          overlay_available=cone is not None,
                                          overlay_note="give audibility.cone with an excursion curve and Sd to have every "
                                                       "panel's output compared with the cone's as a volume-velocity "
                                                       "ratio against the criterion. Without it only the required margin "
                                                       "at each panel's mode band is reported."),
                clamped_square_higher_modes=dict(lambda_values=panels.CLAMPED_SQUARE_MODES,
                                                 note="Leissa Table 4.27 for a clamped square plate. The pair at 131.6 "
                                                      "and 132.3 is why 'the panel resonance' is a simplification above "
                                                      "the first mode or two."),
                pressure_source=pressure, panels=rows,
                summary=dict(min_first_mode_hz=float(min(r["first_mode_hz"] for r in rows)),
                             lowest_mode_band_hz=min(rows, key=lambda r: r["mode_band"]["pinned_hz"])["mode_band"]["band_hz"],
                             lowest_mode_band_panel=min(rows, key=lambda r: r["mode_band"]["pinned_hz"])["name"],
                             worst_panel_by_peak_bound=max(rows, key=lambda r: next(v for v in r["loss_variants"] if v["loss_factor"] == nominal)["peak_bound_rms_mm"])["name"],
                             max_peak_bound_rms_mm_at_nominal_loss=float(max(next(v for v in r["loss_variants"] if v["loss_factor"] == nominal)["peak_bound_rms_mm"] for r in rows)),
                             max_static_center_mm=float(max(r["static_center_mm_at_max_pressure"] for r in rows)), nominal_loss_factor=nominal))


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Simply supported panel bay vibration under internal pressure", NOTES, VALIDITY))
