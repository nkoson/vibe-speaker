#!/usr/bin/env python3
"""Schematic, connection table and board netlist from a crossover_network parameter file.

  schematic.py --input xo.json --out docs/ [--name c01]

Writes <name>_schematic.png (one ladder per section), <name>_connections.md (pin to
pin table with values) and <name>_board.json, a board_nodal parameter file with
the same topology, one input terminal pair per section and a linked mode, ready to
edit with real wire resistances, shared returns and links.

Component labels in the drawing show the reference (L1, C2), the part name when
the element carries "part", and the electrical specification: value, coil DCR,
capacitor ESR and voltage rating, resistor power rating from "rating". A parallel
bank or a series array is drawn as one box with its members listed one per line,
and its leaves take the composite's reference with an a, b, c suffix so the board
netlist has unique component ids.

example_crossover.json beside this file is a self-contained parameter file that
exercises those cases; it needs no result files, and its output can be fed
straight to board_nodal and to crossover_network.
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import patches  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import cli, acoustics  # noqa: E402

TYPE_WORDS = {"L": "Coil", "C": "Capacitor", "R": "Resistor"}


def spec_text(leaf):
    """Electrical specification of one leaf element: value, loss and rating."""
    rating = leaf.get("rating") or {}
    if leaf["type"] == "L":
        dcr = leaf.get("dcr_ohm")
        loss = f"DCR {dcr:g} Ω" if dcr is not None else f"DCR ~{acoustics.default_coil_dcr(float(leaf['value_mh'])):.2f} Ω assumed"
        parts = [f"{leaf['value_mh']:g} mH", loss]
        if rating.get("current_rms_a"):
            parts.append(f"{rating['current_rms_a']:g} A")
        return ", ".join(parts)
    if leaf["type"] == "C":
        parts = [f"{leaf['value_uf']:g} µF"]
        if leaf.get("esr_ohm") is not None:
            parts.append(f"ESR {leaf['esr_ohm']:g} Ω")
        voltage = rating.get("voltage_v") or rating.get("voltage_rms")
        if voltage:
            parts.append(f"{voltage:g} V")
        return ", ".join(parts)
    if leaf["type"] == "R":
        parts = [f"{leaf['value_ohm']:g} Ω"]
        if rating.get("power_w"):
            parts.append(f"{rating['power_w']:g} W")
        return ", ".join(parts)
    return leaf["type"]


def element_spec(e):
    if e["type"] in ("series", "parallel"):
        joiner = " + " if e["type"] == "series" else " ∥ "
        return joiner.join(f"({element_spec(p)})" if p["type"] in ("series", "parallel") else element_spec(p) for p in e.get("parts", []))
    return spec_text(e)


def _label_block(e):
    """Label for one drawn element.

    A composite is drawn as one box, so its members are stacked one per line instead of being run
    together on a single line, which overlaps the neighbouring element's label once a bank has more
    than two members.
    """
    if e.get("type") in ("series", "parallel") and e.get("parts"):
        joiner = "in series" if e["type"] == "series" else "in parallel"
        lines = [f"{e.get('id', '')} ({joiner})".strip()]
        for part in e["parts"]:
            name = part.get("part") or TYPE_WORDS.get(part.get("type"), part.get("type", ""))
            # value only: the loss and the rating of every member are in the parts list, and a
            # bank of three would otherwise run into the neighbouring element's label
            lines.append(f"{name}, {element_spec(part).split(',')[0]}".strip())
        return "\n".join(lines)
    return f"{element_title(e)}\n{element_spec(e)}"


def element_title(e):
    """Reference and part or type name of an element, without any section prefix."""
    if e.get("wiring"):
        return "Wiring"
    words = []
    if e.get("id"):
        words.append(str(e["id"]))
    if e.get("part"):
        words.append(str(e["part"]))
    elif e["type"] in TYPE_WORDS:
        words.append(TYPE_WORDS[e["type"]])
    else:
        names = [p.get("part") or TYPE_WORDS.get(p["type"], p["type"]) for p in acoustics.iter_elements(e)]
        words.append((" + " if e["type"] == "series" else " ∥ ").join(names))
    return " ".join(words)


def _absolute(reference, base_dir):
    """Make a {file, path} reference independent of where the board file is written."""
    if isinstance(reference, dict) and "file" in reference:
        return dict(reference, file=str(cli.resolve_path(reference["file"], base_dir).resolve()))
    return reference


def _unique_ids(components, connections):
    """board_nodal requires unique ids; leaves of one composite share theirs until they are suffixed."""
    seen = {}
    for component in components:
        seen.setdefault(component["id"], []).append(component)
    for base, group in seen.items():
        if len(group) == 1:
            continue
        for index, component in enumerate(group):
            new = f"{base}{chr(ord('a') + index)}" if index < 26 else f"{base}_{index + 1}"
            for connection in connections:
                if connection["id"] == component["id"] and connection["from_node"] == component["nodes"][0] \
                        and connection["to_node"] == component["nodes"][1] and connection.get("_done") is None:
                    connection["id"] = new
                    connection["_done"] = True
                    break
            component["id"] = new
    for connection in connections:
        connection.pop("_done", None)


def netlist(sections, base_dir="."):
    """Flatten ladders into a board_nodal netlist with named nodes."""
    components = []
    sources = []
    loads = []
    connections = []
    for section in sections:
        name = section.get("name", "section")
        up = name.upper()
        plus, minus = f"{up}_IN+", f"{up}_IN-"
        sources.append(dict(id=up, plus=plus, minus=minus, voltage_rms=2.83))
        node = plus
        counter = 0
        wire = float(section.get("wire_loop_ohm", 0.0))
        if wire > 0:
            counter += 1
            new = f"{name}_n{counter}"
            components.append(dict(id=f"wiring_{name}", type="R", value_ohm=wire, nodes=[node, new]))
            connections.append(dict(id=f"wiring_{name}", label="Wiring", from_node=node, to_node=new, value=f"{wire:g} Ω allowance"))
            node = new
        for e in section.get("elements", []):
            if e["position"] == "series":
                counter += 1
                new = f"{name}_n{counter}"
                a, b = node, new
                node = new
            else:
                a, b = node, minus
            counter = _expand(e, a, b, name, counter, components, connections)
        polarity = float(section.get("polarity", 1))
        drv_plus, drv_minus = (f"{up}_DRV+", f"{up}_DRV-") if polarity >= 0 else (f"{up}_DRV-", f"{up}_DRV+")
        components.append(dict(id=f"lead_{name}_hot", type="R", value_ohm=0.005, nodes=[node, drv_plus], note="driver lead, set resistance"))
        components.append(dict(id=f"lead_{name}_return", type="R", value_ohm=0.005, nodes=[minus, drv_minus], note="driver lead, set resistance"))
        connections.append(dict(id=f"lead_{name}_hot", label=f"{up} driver lead", from_node=node, to_node=drv_plus, value=f"driver + terminal (polarity {polarity:+g})"))
        connections.append(dict(id=f"lead_{name}_return", label=f"{up} driver return", from_node=minus, to_node=drv_minus, value="driver - terminal"))
        impedance = section.get("load") or (dict(section["source"], path="results.z_ohm") if section.get("source") else {"kind": "resistive", "r_ohm": 8})
        loads.append(dict(id=name, plus=f"{up}_DRV+", minus=f"{up}_DRV-", impedance=_absolute(impedance, base_dir)))
    links = []
    first = sections[0].get("name", "section").upper()
    for section in sections[1:]:
        up = section.get("name", "section").upper()
        links += [[f"{first}_IN+", f"{up}_IN+"], [f"{first}_IN-", f"{up}_IN-"]]
    modes = [dict(id="linked_single_amplifier", links=links, active_sources=[sections[0].get("name", "section").upper()])]
    modes += [dict(id=f"{w.get('name')}_only", links=[], active_sources=[w.get("name", "section").upper()]) for w in sections]
    _unique_ids(components, connections)
    return dict(frequencies={"min_hz": 10, "max_hz": 40000, "points": 600}, components=components, wires=[], sources=sources, loads=loads, modes=modes,
                tolerances={"draws": 8, "seed": 9919, "C": 0.05, "L": 0.03, "R": 0.02}), connections


def _expand(e, a, b, name, counter, components, connections, inherited=None):
    """Expand a possibly composite element between nodes a and b into leaf components.

    A composite that carries an id lends it to its leaves, so a three-resistor Rs2 becomes
    Rs2a, Rs2b and Rs2c once _unique_ids has run, rather than three components with one id.
    """
    if e["type"] == "series":
        node = a
        parts = e.get("parts", [])
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                new = b
            else:
                counter += 1
                new = f"{name}_n{counter}"
            counter = _expand(part, node, new, name, counter, components, connections, e.get("id") or inherited)
            node = new
        return counter
    if e["type"] == "parallel":
        for part in e.get("parts", []):
            counter = _expand(part, a, b, name, counter, components, connections, e.get("id") or inherited)
        return counter
    leaf = dict(id=e.get("id") or inherited or f"{name}_x{counter}", type=e["type"], nodes=[a, b])
    for key in ("value_mh", "value_uf", "value_ohm", "dcr_ohm", "esr_ohm", "tolerance_fraction", "part", "rating"):
        if key in e:
            leaf[key] = e[key]
    components.append(leaf)
    connections.append(dict(id=leaf["id"], label=element_title(e), from_node=a, to_node=b, value=spec_text(e)))
    return counter


def draw(sections, path, title):
    fig, axes = plt.subplots(len(sections), 1, figsize=(17, 3.6 * len(sections)), constrained_layout=True)
    axes = [axes] if len(sections) == 1 else list(axes)
    for ax, section in zip(axes, sections):
        name = section.get("name", "section").upper()
        elements = list(section.get("elements", []))
        wire = float(section.get("wire_loop_ohm", 0.0))
        if wire > 0:
            elements = [dict(position="series", type="R", value_ohm=wire, wiring=True)] + elements
        step = 1.25
        ax.set(xlim=(-1.3, step * len(elements) + 2.4), ylim=(-1.9, 1.3))
        ax.axis("off")
        ax.plot([-.3, step * len(elements) + .7], [-.85, -.85], color="black")
        ax.text(-.5, .05, f"{name} input +", ha="right", va="center", fontsize=9)
        ax.text(-.5, -.85, f"{name} input −", ha="right", va="center", fontsize=9)
        ax.plot([-.3, 0], [0, 0], color="black")
        for j, e in enumerate(elements):
            x = j * step
            label = _label_block(e)
            if e["position"] == "series":
                ax.plot([x, x + .25], [0, 0], color="black")
                ax.add_patch(patches.Rectangle((x + .25, -.15), .75, .3, fill=False))
                ax.plot([x + 1.0, x + step], [0, 0], color="black")
                ax.text(x + .625, .24, label, ha="center", va="bottom", fontsize=8)
            else:
                ax.plot([x, x + step], [0, 0], color="black")
                ax.plot([x + .625, x + .625], [0, -.2], color="black")
                ax.add_patch(patches.Rectangle((x + .475, -.63), .3, .43, fill=False))
                ax.plot([x + .625, x + .625], [-.63, -.85], color="black")
                ax.text(x + .625, -.98, label, ha="center", va="top", fontsize=8)
        end = step * len(elements)
        ax.plot([end, end + .7], [0, 0], color="black")
        ax.plot([end + .7, end + .7], [0, -.18], color="black")
        ax.plot([end + .7, end + .7], [-.65, -.85], color="black")
        ax.add_patch(patches.Rectangle((end + .52, -.65), .36, .47, facecolor="white", edgecolor="black", zorder=3))
        ax.text(end + .98, -.35, f"{name} driver\npolarity {float(section.get('polarity', 1)):+g}", fontsize=9, va="center")
    fig.suptitle(title, fontsize=13)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def markdown(sections, connections, name):
    lines = [f"# Crossover connections: {name}", "", "Ladders are read from the input terminals toward the driver. Node names match the board netlist.", "",
             "| Component | Netlist id | From node | To node | Specification |", "|---|---|---|---|---|"]
    lines += [f"| {c['label']} | {c['id']} | {c['from_node']} | {c['to_node']} | {c['value']} |" for c in connections]
    lines += ["", "## Bill of components", "", "| Section | Reference | Part | Type | Specification | Loss used |", "|---|---|---|---|---|---|"]
    for section in sections:
        for e in section.get("elements", []):
            for leaf in acoustics.iter_elements(e):
                loss = leaf.get("dcr_ohm", leaf.get("esr_ohm"))
                lines.append(f"| {section.get('name').upper()} | {leaf.get('id') or e.get('id') or ''} | {leaf.get('part') or ''} | {TYPE_WORDS.get(leaf['type'], leaf['type'])} | {spec_text(leaf)} | {'' if loss is None else f'{loss:g} Ω'} |")
    first = sections[0].get("name", "section").upper()
    if len(sections) > 1:
        others = ", ".join(w.get("name", "section").upper() for w in sections[1:])
        lines += ["", f"Single amplifier: link the {first} input + to the {others} input + and the {first} input − to the {others} input − at the terminal cup. Remove the links for passive bi-amplification."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, help="crossover_network parameter file, or a crossover_fit result (fitted_sections is used)")
    parser.add_argument("--out", required=True)
    parser.add_argument("--name", default="crossover")
    parser.add_argument("--title", default=None, help="drawing title, default '<name>: passive crossover'")
    args = parser.parse_args()
    doc = cli.load_json(args.input)
    sections = doc.get("sections")
    if doc.get("simulation") == "crossover_fit":
        sections = doc["results"]["fitted_sections"]
    if not sections:
        raise SystemExit("no sections found in the input")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    board, connections = netlist(sections, Path(args.input).resolve().parent)
    draw(sections, out / f"{args.name}_schematic.png", args.title or f"{args.name}: passive crossover")
    (out / f"{args.name}_connections.md").write_text(markdown(sections, connections, args.name))
    (out / f"{args.name}_board.json").write_text(json.dumps(cli.to_jsonable(board), indent=1))
    for suffix in ("_schematic.png", "_connections.md", "_board.json"):
        print(out / f"{args.name}{suffix}")


if __name__ == "__main__":
    main()
