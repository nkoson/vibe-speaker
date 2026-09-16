#!/usr/bin/env python3
"""Plot curves or angle maps from simulation result files to a PNG.

Examples:
  plot_curves.py --out fig.png --curve out/whole_speaker.json:results.f_hz:results.on_axis.spl_db:System \
      --curve out/whole_speaker.json:results.f_hz:results.on_axis.sections.0.spl_db:LF --ylabel "SPL (dB)" --ylim 60,110
  plot_curves.py --out map.png --matrix out/whole_speaker.json:results.f_hz:results.horizontal.angles_deg:results.horizontal.relative_to_axis_db
A complex record (real/imag) is plotted as its magnitude in dB, or its phase with :phase appended to the path.
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import cli  # noqa: E402


def _series(spec):
    parts = spec.split(":")
    if len(parts) < 3:
        raise SystemExit(f"curve needs file:xpath:ypath[:label]: {spec}")
    file, xpath, ypath = parts[:3]
    label = parts[3] if len(parts) > 3 else ypath
    phase = ypath.endswith(":phase") or (len(parts) > 4 and parts[4] == "phase")
    ypath = ypath.replace(":phase", "")
    doc = cli.load_json(file)
    x = np.asarray(cli.dotted(doc, xpath), float)
    y = cli.dotted(doc, ypath)
    if isinstance(y, dict):
        y = y["phase_deg"] if phase else y["magnitude_db"]
    return x, np.asarray(y, float), label


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--curve", action="append", default=[], help="file:xpath:ypath[:label]")
    parser.add_argument("--matrix", help="file:xpath:anglepath:matrixpath for an angle map")
    parser.add_argument("--title", default="")
    parser.add_argument("--xlabel", default="Frequency (Hz)")
    parser.add_argument("--ylabel", default="")
    parser.add_argument("--ylim", help="min,max")
    parser.add_argument("--xlim", help="min,max")
    parser.add_argument("--linear-x", action="store_true")
    parser.add_argument("--size", default="10,5", help="inches w,h")
    args = parser.parse_args()
    w, h = (float(v) for v in args.size.split(","))
    fig, ax = plt.subplots(figsize=(w, h), constrained_layout=True)
    if args.matrix:
        file, xpath, apath, mpath = args.matrix.split(":")
        doc = cli.load_json(file)
        f = np.asarray(cli.dotted(doc, xpath), float)
        angles = np.asarray(cli.dotted(doc, apath), float)
        m = np.asarray(cli.dotted(doc, mpath), float)
        mesh = ax.pcolormesh(f, angles, m, shading="auto", cmap="viridis", vmin=float(args.ylim.split(",")[0]) if args.ylim else None,
                             vmax=float(args.ylim.split(",")[1]) if args.ylim else None)
        fig.colorbar(mesh, ax=ax, label=args.ylabel or "dB")
        ax.set_ylabel("Angle (deg)")
    else:
        for spec in args.curve:
            x, y, label = _series(spec)
            ax.plot(x, y, label=label)
        if args.ylabel:
            ax.set_ylabel(args.ylabel)
        if args.ylim:
            ax.set_ylim(*(float(v) for v in args.ylim.split(",")))
        if len(args.curve) > 1:
            ax.legend(fontsize=8)
    if not args.linear_x:
        ax.set_xscale("log")
    if args.xlim:
        ax.set_xlim(*(float(v) for v in args.xlim.split(",")))
    ax.set_xlabel(args.xlabel)
    ax.set_title(args.title)
    ax.grid(True, which="both", alpha=.3)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150)
    print(args.out)


if __name__ == "__main__":
    main()
