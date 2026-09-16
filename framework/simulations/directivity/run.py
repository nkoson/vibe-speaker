#!/usr/bin/env python3
"""Directivity of analytical source models - piston, Gaussian horn coverage, beamwidth table,
rectangular ribbon - and the oblate-spheroidal waveguide contour and cutoff from its geometry."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import cli, acoustics, horn  # noqa: E402

NAME = "directivity"
VERSION = "1.1"
NOTES = [
    "Piston: rigid circular piston in an infinite baffle, no breakup. Gaussian and beamwidth-table horns: -6 dB at half the nominal included angle, no throat or mouth physics.",
    "Rectangular: separable sinc pattern of a uniformly driven rectangle. Values are relative to the on-axis response of the same source.",
    "An oblate-spheroidal waveguide is the one source whose geometry is used here rather than described: its contour r(x) = sqrt(rt^2 + tan^2(theta0) x^2) and its cutoff fc = 0.2 c sin(theta0) / (pi rt) are computed from the throat radius and half angle. The cutoff is the 0.2-of-asymptotic-resistance convention, so it means roughly what exponential-horn cutoff means and nothing more, and the OS waveguide has no sharp cutoff at all.",
    "Throat impedance for the OS contour has no closed form and is deliberately not computed; the pattern is what a waveguide is chosen for, and shape barely moves impedance in the band where the horn equation holds.",
]


VALIDITY = [
    "Analytical patterns only: a piston pattern assumes pistonic behaviour and stops being the driver's pattern at break-up, and a Gaussian or tabulated horn coverage carries no throat or mouth physics. Check the upper working limit against a measured response, not against these curves.",
    "Values are relative to the on-axis response of the same source, so a beamwidth here is a shape statement and not a level.",
    "The three published ka ceilings - ka < 5, one wavelength per cone diameter, about a decade of passband - disagree by roughly an octave and none has a stated criterion behind it. This app computes patterns; it does not choose a ceiling.",
    "A waveguide cutoff computed from geometry says where the device stops loading and controlling, not what its pattern is. The pattern still comes from the mouth, through Keele's constant-directivity relation in horn_design, and the declared coverage model here carries no throat or mouth physics.",
]


def compute(params, base_dir):
    f = cli.frequency_grid(params.get("frequencies"), 200.0, 20000.0, 200)
    sources = cli.require(params, "sources")
    h_angles = np.asarray(params.get("horizontal_angles_deg", np.arange(0, 91, 5)), float)
    v_angles = np.asarray(params.get("vertical_angles_deg", np.arange(0, 91, 5)), float)
    rows = []
    for source in sources:
        model = cli.require(source, "directivity", label="source")
        h = acoustics.directivity(model, f[None, :], np.deg2rad(h_angles)[:, None], np.zeros((len(h_angles), 1)))
        v = acoustics.directivity(model, f[None, :], np.zeros((len(v_angles), 1)), np.deg2rad(v_angles)[:, None])
        row = dict(name=source.get("name"), directivity=model,
                    horizontal_db=acoustics.db(h), vertical_db=acoustics.db(v),
                    beamwidth_6db_deg=[acoustics.beamwidth_deg(x, model) for x in f])
        waveguide = source.get("os_waveguide")
        if waveguide:
            row["os_waveguide"] = horn.os_waveguide(
                cli.positive(waveguide.get("throat_radius_mm"), "source.os_waveguide.throat_radius_mm"),
                cli.positive(waveguide.get("half_angle_deg"), "source.os_waveguide.half_angle_deg"),
                waveguide.get("axial_positions_mm"))
            nominal = model.get("horizontal_deg")
            if nominal:
                row["os_waveguide"]["declared_coverage_deg"] = float(nominal)
                row["os_waveguide"]["included_angle_matches_declared_coverage"] = bool(
                    abs(row["os_waveguide"]["included_angle_deg"] - float(nominal)) <= 5.0)
        rows.append(row)
    return dict(f_hz=f, horizontal_angles_deg=h_angles, vertical_angles_deg=v_angles, sources=rows)


if __name__ == "__main__":
    sys.exit(cli.run(NAME, VERSION, compute, "Analytical source directivity, and OS waveguide geometry", NOTES, VALIDITY))
