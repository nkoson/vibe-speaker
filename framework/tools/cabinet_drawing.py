#!/usr/bin/env python3
"""Cut list, volume accounting and construction drawing of a rectangular cabinet.

  cabinet_drawing.py --input cabinet.json --out docs/ [--name c01]

Writes <name>_cutlist.json, <name>_cutlist.md and <name>_drawing.png. The input
describes outside dimensions, panel thickness, partitions, braces, cutouts and
ports; nothing here judges the design.

No interference checking: two objects may be given the same space and will be
drawn that way. The interior occupancy bookkeeping, and the depth extent of
anything behind a panel, belong to the reader; see
framework/references/cabinet-geometry.md.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import cli  # noqa: E402


def cut_list(spec):
    outer = spec["outer"]
    t = float(spec.get("panel_thickness_mm", 18.0))
    W, D, H = float(outer["width_mm"]), float(outer["depth_mm"]), float(outer["height_mm"])
    material = spec.get("material", f"{t:g} mm board")
    parts = [
        dict(name="front", width_mm=W - 2 * t, height_mm=H - 2 * t, count=1, cutouts=[c["name"] for c in spec.get("front_cutouts", [])]),
        dict(name="rear", width_mm=W - 2 * t, height_mm=H - 2 * t, count=1, cutouts=[c["name"] for c in spec.get("rear_cutouts", [])]),
        dict(name="side", width_mm=D, height_mm=H, count=2, cutouts=[]),
        dict(name="top", width_mm=W - 2 * t, height_mm=D, count=1, cutouts=[]),
        dict(name="bottom", width_mm=W - 2 * t, height_mm=D, count=1, cutouts=[]),
    ]
    inside_w, inside_d = W - 2 * t, D - 2 * t
    for p in spec.get("partitions", []):
        parts.append(dict(name=p.get("name", f"partition_{p['z_mm']:g}"), width_mm=inside_w, height_mm=inside_d, count=1,
                          cutouts=[c["name"] for c in p.get("cutouts", [])], z_mm=p["z_mm"]))
    for b in spec.get("braces", []):
        rim = float(b.get("rim_mm", 60.0))
        parts.append(dict(name=b.get("name", f"brace_{b['z_mm']:g}"), width_mm=inside_w, height_mm=inside_d, count=1,
                          cutouts=[f"window {inside_w - 2 * rim:g} x {inside_d - 2 * rim:g} mm, rim {rim:g} mm"], z_mm=b["z_mm"]))
    for p in parts:
        p["thickness_mm"] = float(p.get("thickness_mm", t))
        p["material"] = material
        p["area_m2"] = p["width_mm"] * p["height_mm"] * 1e-6 * p["count"]
    return parts


def volumes(spec):
    outer = spec["outer"]
    t = float(spec.get("panel_thickness_mm", 18.0))
    W, D, H = float(outer["width_mm"]), float(outer["depth_mm"]), float(outer["height_mm"])
    inside_w, inside_d = W - 2 * t, D - 2 * t
    chambers = []
    bounds = [t] + sorted(float(p["z_mm"]) for p in spec.get("partitions", [])) + [H - t]
    names = spec.get("chamber_names") or [f"chamber_{i + 1}" for i in range(len(bounds) - 1)]
    for i in range(len(bounds) - 1):
        z0, z1 = bounds[i], bounds[i + 1]
        if i > 0:
            z0 += t
        gross = inside_w * inside_d * (z1 - z0) * 1e-6
        brace_l = 0.0
        for b in spec.get("braces", []):
            if z0 <= float(b["z_mm"]) < z1:
                rim = float(b.get("rim_mm", 60.0))
                thick = float(b.get("thickness_mm", t))
                brace_l += (inside_w * inside_d - (inside_w - 2 * rim) * (inside_d - 2 * rim)) * thick * 1e-6
        port_l = 0.0
        for p in spec.get("ports", []):
            if z0 <= float(p["z_mm"]) < z1:
                port_l += math.pi * (float(p["od_mm"]) / 2) ** 2 * float(p["length_mm"]) * 1e-6
        lining = float(spec.get("lining_mm", 0.0))
        lining_l = 0.0
        if lining:
            lining_l = (2 * inside_d * (z1 - z0) + inside_w * (z1 - z0) + 2 * inside_w * inside_d) * lining * 1e-6 * float(spec.get("lining_solid_fraction", 0.15))
        drivers_l = sum(float(d.get("displacement_l", 0.0)) for d in spec.get("driver_displacements", []) if z0 <= float(d.get("z_mm", z0)) < z1)
        chambers.append(dict(name=names[i], z_from_mm=z0, z_to_mm=z1, inside_width_mm=inside_w, inside_depth_mm=inside_d, inside_height_mm=z1 - z0,
                             gross_l=gross, brace_l=brace_l, port_tube_l=port_l, lining_solid_l=lining_l, driver_l=drivers_l,
                             net_l=gross - brace_l - port_l - lining_l - drivers_l))
    return chambers


def draw(spec, chambers, path):
    outer = spec["outer"]
    t = float(spec.get("panel_thickness_mm", 18.0))
    W, D, H = float(outer["width_mm"]), float(outer["depth_mm"]), float(outer["height_mm"])
    fig, axes = plt.subplots(1, 3, figsize=(15, 8), constrained_layout=True)
    front, side, rear = axes
    for ax, title in ((front, "Front elevation"), (side, "Side section (front at left)"), (rear, "Rear elevation")):
        ax.set_aspect("equal")
        ax.set_title(title)
        ax.set_xlabel("mm")
        ax.grid(alpha=.2)
    front.add_patch(patches.Rectangle((0, 0), W, H, fill=False, lw=1.5))
    rear.add_patch(patches.Rectangle((0, 0), W, H, fill=False, lw=1.5))
    for ax, key in ((front, "front_cutouts"), (rear, "rear_cutouts")):
        for c in spec.get(key, []):
            x = float(c["x_mm"]) if key == "front_cutouts" else W - float(c["x_mm"])
            if c.get("shape", "circle") == "circle":
                ax.add_patch(patches.Circle((x, c["z_mm"]), float(c["diameter_mm"]) / 2, fill=False, ls="--"))
            else:
                ax.add_patch(patches.Rectangle((x - float(c["width_mm"]) / 2, float(c["z_mm"]) - float(c["height_mm"]) / 2), float(c["width_mm"]), float(c["height_mm"]), fill=False, ls="--"))
            ax.annotate(c["name"], (x, c["z_mm"]), ha="center", fontsize=8)
    side.add_patch(patches.Rectangle((0, 0), D, H, fill=False, lw=1.5))
    side.add_patch(patches.Rectangle((0, 0), t, H, color="#bbbbbb"))
    side.add_patch(patches.Rectangle((D - t, 0), t, H, color="#bbbbbb"))
    side.add_patch(patches.Rectangle((0, 0), D, t, color="#bbbbbb"))
    side.add_patch(patches.Rectangle((0, H - t), D, t, color="#bbbbbb"))
    for p in spec.get("partitions", []):
        side.add_patch(patches.Rectangle((t, float(p["z_mm"])), D - 2 * t, t, color="#888888"))
        side.annotate(p.get("name", "partition"), (D / 2, float(p["z_mm"]) + t), ha="center", fontsize=8)
    for b in spec.get("braces", []):
        rim = float(b.get("rim_mm", 60.0))
        thick = float(b.get("thickness_mm", t))
        side.add_patch(patches.Rectangle((t, float(b["z_mm"])), rim, thick, color="#555555"))
        side.add_patch(patches.Rectangle((D - t - rim, float(b["z_mm"])), rim, thick, color="#555555"))
        front.plot([t, W - t], [float(b["z_mm"]) + thick / 2] * 2, color="#555555", ls=":", lw=1)
        front.annotate(f"brace z={b['z_mm']:g}", (W - t, float(b["z_mm"])), ha="right", fontsize=7)
    for p in spec.get("ports", []):
        side.add_patch(patches.Rectangle((D - t - float(p["length_mm"]), float(p["z_mm"]) - float(p["od_mm"]) / 2), float(p["length_mm"]), float(p["od_mm"]), fill=False, hatch="//"))
    lining = float(spec.get("lining_mm", 0.0))
    if lining:
        for c in chambers:
            if c.get("lined", True):
                side.add_patch(patches.Rectangle((D - t - lining, c["z_from_mm"]), lining, c["inside_height_mm"], color="#ddcc99", alpha=.6))
    for c in chambers:
        side.annotate(f"{c['name']}\nnet {c['net_l']:.1f} L", (D / 2, (c["z_from_mm"] + c["z_to_mm"]) / 2), ha="center", fontsize=8)
    for ax in axes:
        ax.set_xlim(-50, max(W, D) + 50)
        ax.set_ylim(-50, H + 50)
    fig.suptitle(f"{spec.get('name', 'cabinet')}: {W:g} x {D:g} x {H:g} mm outside, {t:g} mm panels; drawing from the candidate record, not a measurement", fontsize=11)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def markdown(parts, chambers, spec):
    lines = [f"# Cut list: {spec.get('name', 'cabinet')}", "", f"Material: {spec.get('material', 'board')}. Outside {spec['outer']['width_mm']} x {spec['outer']['depth_mm']} x {spec['outer']['height_mm']} mm (W x D x H).", "",
             "| Part | Width mm | Height mm | Thickness mm | Qty | Cutouts |", "|---|---|---|---|---|---|"]
    for p in parts:
        lines.append(f"| {p['name']} | {p['width_mm']:.1f} | {p['height_mm']:.1f} | {p['thickness_mm']:g} | {p['count']} | {', '.join(p['cutouts']) or ''} |")
    lines += ["", "| Chamber | Inside W x D x H mm | Gross L | Braces L | Port tubes L | Lining solid L | Drivers L | Net L |", "|---|---|---|---|---|---|---|---|"]
    for c in chambers:
        lines.append(f"| {c['name']} | {c['inside_width_mm']:.0f} x {c['inside_depth_mm']:.0f} x {c['inside_height_mm']:.0f} | {c['gross_l']:.1f} | {c['brace_l']:.1f} | {c['port_tube_l']:.1f} | {c['lining_solid_l']:.1f} | {c['driver_l']:.1f} | {c['net_l']:.1f} |")
    area = sum(p["area_m2"] for p in parts)
    lines += ["", f"Total panel area {area:.2f} m2 (one cabinet)."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--name")
    args = parser.parse_args()
    spec = cli.load_json(args.input)
    name = args.name or spec.get("name", "cabinet")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    parts = cut_list(spec)
    chambers = volumes(spec)
    (out / f"{name}_cutlist.json").write_text(json.dumps(cli.to_jsonable(dict(cabinet=spec, parts=parts, chambers=chambers)), indent=1))
    (out / f"{name}_cutlist.md").write_text(markdown(parts, chambers, spec))
    draw(spec, chambers, out / f"{name}_drawing.png")
    print(out / f"{name}_cutlist.json")
    print(out / f"{name}_cutlist.md")
    print(out / f"{name}_drawing.png")


if __name__ == "__main__":
    main()
