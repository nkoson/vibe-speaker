#!/usr/bin/env python3
"""Finite-baffle transfer for a source on a rectangular front panel: shelf, edge diffraction and recess."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics  # noqa: E402

NAME = "baffle_diffraction"
VERSION = "1.1"
NOTES = [
    "Shelf: first-order 6 dB baffle step with corner at 115 / width Hz. Edge diffraction: first-order sum of delayed, inverted half edge waves weighted by subtended angle and piston beaming; on-axis factor only.",
    "The step is distance-dependent. Each edge wave is weighted by observer / hypot(observer, edge distance), so a near observer sees a shallower step than the far field: a 250 mm baffle centred source shows about 5 dB at 0.25 m against 6 dB far field. A correction derived at one distance and applied at another under- or over-compensates by that difference.",
    "An edge radius tapers the edge wave above its lambda/8 frequency c / (8 r) and does nothing below it, which is the frequency reported as edge_radius_effective_above_hz. The taper is a first-order prior, not a solved roundover.",
    "Recess: short rigid tube terminated by a piston radiation impedance; quarter-wave rise only, no cavity edge diffraction.",
    "No rear-wall scattering, off-axis diffraction or room; the factor multiplies the infinite-baffle (2 pi) source response and tends to 0.5 (-6 dB, the 4 pi limit) at low frequency in the far field.",
    "The full 6 dB step belongs to a speaker in free space. In a normal room the walls restore part of the low-frequency support and the realised step is unlikely to exceed about 3 dB, so how much to compensate is a voicing decision to state, not a number this app supplies.",
]
VALIDITY = [
    "First-order edge diffraction only: one reflection per edge segment, no secondary diffraction between edges and no scattering from the cabinet sides or rear.",
    "The on-axis factor is computed at the observation point named in the result. It is not an off-axis factor, and the power response it implies tilts the other way from the axial curve it flattens.",
    "Overall baffle width stops setting the response above about 6 kHz and has no effect above roughly 14 kHz; local geometry close to the source - a sub-baffle, a faceplate edge, a surround step - still matters well above that and is not in this model.",
]


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 20.0, 20000.0, 400)
    baffle = cli.require(params, "baffle")
    vertices = baffle.get("vertices_mm")
    width = cli.positive(baffle.get("width_mm", float(np.ptp(np.asarray(vertices)[:,0])) if vertices else None), "baffle.width_mm")
    height = cli.positive(baffle.get("height_mm", float(np.ptp(np.asarray(vertices)[:,1])) if vertices else None), "baffle.height_mm")
    observer = float(params.get("observer_distance_m", 3.0))
    segments = int(params.get("segments", 96))
    default_edge_radius = float(baffle.get("edge_radius_mm", 0.0)) / 1000
    rows = []
    for source in cli.require(params, "sources"):
        model = source.get("model", "edge_diffraction")
        radius = 0.0
        if source.get("radius_mm") is not None:
            radius = float(source["radius_mm"]) / 1000
        elif source.get("sd_cm2") is not None:
            radius = float(np.sqrt(float(source["sd_cm2"]) * 1e-4 / np.pi))
        edge_radius = float(source["edge_radius_mm"]) / 1000 if source.get("edge_radius_mm") is not None else default_edge_radius
        row = dict(name=source.get("name"), model=model, x_mm=source.get("x_mm"), z_mm=source.get("z_mm"),
                   piston_radius_mm=radius * 1000, edge_radius_mm=edge_radius * 1000)
        if model == "distributed_edge_dipole":
            from _common import diffraction
            angular = dict(kind=model,vertices_mm=vertices or [[0,0],[width,0],[width,height],[0,height]],
                           source_mm=[float(source["x_mm"]),float(source["z_mm"])],
                           subdivisions=int(params.get("edge_subdivisions",24)),radius_mm=radius*1000,
                           radiator_width_mm=source.get("radiator_width_mm",0),
                           radiator_height_mm=source.get("radiator_height_mm",0),
                           observer_distance_m=None if params.get("far_field",False) else observer,
                           open_baffle=bool(baffle.get("open_baffle")),edge_radius_mm=edge_radius*1000)
            factor=diffraction.evaluate(angular,f,0,0)
            far=diffraction.evaluate(dict(angular,observer_distance_m=None),f,0,0)
            row["angular_model"]=angular
            row["angular_contract"]="includes radiator directivity and baffle; replaces the section analytic directivity"
            if params.get("angular_grid"):
                grid=params["angular_grid"]
                for name,key in (("horizontal","horizontal_deg"),("vertical","vertical_deg")):
                    angles=np.asarray(grid.get(key,[0]),float)
                    hh=np.deg2rad(angles[:,None]) if name=="horizontal" else 0
                    vv=np.deg2rad(angles[:,None]) if name=="vertical" else 0
                    row[name]=dict(angles_deg=angles,factor=diffraction.evaluate(angular,f[None,:],hh,vv))
        elif model == "shelf":
            factor = acoustics.shelf_baffle(f, width)
            far = factor
        elif model == "edge_diffraction":
            x, z = float(source["x_mm"]), float(source["z_mm"])
            factor = acoustics.edge_diffraction(f, width, height, x, z, radius, observer, segments, edge_radius)
            far = acoustics.edge_diffraction(f, width, height, x, z, radius, None, segments, edge_radius)
            row["step"] = dict(
                at_observer_db=acoustics.baffle_step_db(width, height, x, z, observer, segments),
                far_field_db=acoustics.baffle_step_db(width, height, x, z, None, segments),
                observer_distance_m=observer,
                note="the low-frequency depth of the step; the high-frequency asymptote is 0 dB by construction. A "
                     "near-field-derived correction applied at the listening distance under-compensates by the difference, "
                     "which is why a splice wants two diffraction corrections, one at each distance.")
            row["step"]["observer_minus_far_field_db"] = row["step"]["at_observer_db"] - row["step"]["far_field_db"]
            row["far_field_factor"] = far
            row["far_field_relative_to_2pi_db"] = acoustics.db(far)
        elif model == "none":
            factor = np.ones(len(f), complex)
            far = factor
        else:
            raise cli.InputError(f"unknown baffle model '{model}'")
        row["baffle_factor"] = factor
        row["relative_to_2pi_db"] = acoustics.db(factor)
        if edge_radius > 0:
            row["edge_radius_effective_above_hz"] = acoustics.roundover_corner_hz(edge_radius)
            row["edge_radius_note"] = ("a roundover can only act on wavelengths shorter than about eight times its radius; "
                                       "below the reported frequency the edge is acoustically square whatever it looks like.")
        recess = source.get("recess")
        if recess and recess.get("setback_mm", 0) > 0:
            rt = acoustics.recess_transfer(f, float(recess["setback_mm"]), float(recess["opening_width_mm"]), float(recess["opening_height_mm"]))
            row["recess_transfer"] = rt
            row["combined_factor"] = factor * rt
        rows.append(row)
    return dict(f_hz=f, baffle=dict(width_mm=width, height_mm=height, edge_radius_mm=default_edge_radius * 1000),
                observer_distance_m=observer,
                shelf_corner_hz=float(115 / (width / 1000)),
                allison_full_support_hz=float(acoustics.C / (2 * width / 1000)),
                corner_note="115 / W and c / (2 W) name different points on a transition that spans roughly a decade; "
                            "read the computed curve rather than either number.",
                sources=rows,
                validity=dict(statements=list(VALIDITY),
                              baffle_width_irrelevant_above_hz=14000.0,
                              width_stops_setting_response_above_hz=6000.0))


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Finite-baffle diffraction transfer of front-mounted sources", NOTES, VALIDITY))
