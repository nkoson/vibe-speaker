#!/usr/bin/env python3
"""Draw room geometry and direct/room response from a room_response result."""
import argparse
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, NullFormatter
import numpy as np


def draw(document, destination, frequency_limits=None):
    if document.get("simulation") != "room_response" or document.get("status") != "computed":
        raise ValueError("expected a computed room_response result")
    result = document["results"]
    fig = plt.figure(figsize=(13, 8), layout="constrained")
    geometry = fig.add_subplot(221, projection="3d")
    response = fig.add_subplot(222)
    difference = fig.add_subplot(223)
    spread = fig.add_subplot(224)
    dimensions = result["room_dimensions_m"]
    corners = np.array(list(itertools.product(*[(0, size) for size in dimensions])))
    for i, a in enumerate(corners):
        for b in corners[i + 1:]:
            if np.count_nonzero(a != b) == 1:
                geometry.plot(*np.array([a, b]).T, color="0.65", lw=.7)
    for source in result["source_geometry"]:
        position = source["centre_m"]
        geometry.scatter(*position, color="#ba4a29", s=18)
        geometry.quiver(*position, *source["forward_vector"], length=.5, color="#ba4a29")
    colors = plt.cm.viridis(np.linspace(.1, .85, len(result["receivers"])))
    f = np.asarray(result["f_hz"])
    for receiver, color in zip(result["receivers"], colors):
        name = receiver["name"]
        geometry.scatter(*receiver["position_m"], color=color, marker="x", s=32)
        response.semilogx(f, receiver["spl_db"], color=color, lw=.7, alpha=.65, label=name)
        difference.semilogx(f, receiver["room_minus_direct_db"], color=color, lw=.8, label=name)
    response.semilogx(f, result["receivers"][0]["direct_spl_db"], color="black", ls="--", lw=1.4,
                     label=f"{result['receivers'][0]['name']} direct")
    response.semilogx(f, result["spatial_summary"]["energy_mean_spl_db"], color="#ba4a29", lw=1.4, label="Seat energy mean")
    spread.semilogx(f, result["spatial_summary"]["spread_db"], color="#345d7e")
    geometry.set(xlabel="x (m)", ylabel="y (m)", zlabel="z (m)",
                 title="3D room: orange sources/arrows, x = seats\nSeat colours follow the response legend")
    geometry.set_box_aspect(dimensions)
    response.set(title="SPL at listening positions", ylabel="SPL (dB re 20 µPa)")
    response.legend(fontsize=7, ncol=2)
    difference.set(title="Room minus direct sound at each seat", ylabel="Difference (dB)")
    spread.set(title="Seat-to-seat spread", ylabel="Maximum minus minimum (dB)")
    for axis in (response, difference, spread):
        axis.set_xlabel("Frequency (Hz)")
        axis.grid(alpha=.2, which="both")
        lo, hi = frequency_limits or (f[0], f[-1])
        if not 0 < lo < hi:
            raise ValueError("frequency limits need positive increasing bounds")
        axis.set_xlim(lo, hi)
        ticks = [v for v in (10,20,50,100,200,500,1000,2000,5000,10000,20000,50000)
                 if lo <= v <= hi]
        axis.set_xticks(ticks)
        axis.xaxis.set_major_formatter(ScalarFormatter())
        axis.xaxis.set_minor_formatter(NullFormatter())
        axis.tick_params(axis="x", labelsize=8)
        if lo < f[0]:
            axis.axvspan(lo, f[0], color="0.94", zorder=-1)
        if hi > f[-1]:
            axis.axvspan(f[-1], hi, color="0.94", zorder=-1)
    fig.suptitle("Room response and listening positions\n"
                 "Direct sound, early reflections and seat-to-seat variation"
                 + ("\nGray: outside the response-data band" if frequency_limits else ""), fontsize=12)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--frequency-limits", nargs=2, type=float, metavar=("LOW_HZ", "HIGH_HZ"),
                        help="Display bounds; unsimulated bands are shaded, never extrapolated")
    args = parser.parse_args()
    draw(json.loads(Path(args.input).read_text()), args.out, args.frequency_limits)
